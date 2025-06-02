# screener/views.py

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from .models import Scan # Uncomment if you have Scan model and need it for other views

from .indicator_utils import (
    # SYMBOLS, # SYMBOLS is loaded in indicator_utils; views can call list_symbols
    CUSTOM_INDICATORS,
    TA_INDICATOR_LABELS,
    call_indicator_logic, # Uses the updated dispatcher
    evaluate_operation,
    get_talib_grouped_indicators,
    get_talib_params,
    list_symbols,
    load_ohlcv
)
from .dsl_parser import parse_query # Using your Python Lark parser

import json
import pandas as pd
import numpy as np
import traceback
import inspect # For more robust argument mapping if needed later

# --- Main Dashboard View ---
class DashboardView(TemplateView):
    template_name = 'screener/dashboard.html'

# --- API Endpoints for Frontend ---
def indicator_list_api(request):
    """Provides grouped indicators and their parameters for the frontend."""
    try:
        grouped_indicators = get_talib_grouped_indicators()
        return JsonResponse({'groups': grouped_indicators})
    except Exception as e:
        print(f"[VIEWS.PY] indicator_list_api: ERROR - {e}")
        traceback.print_exc()
        return JsonResponse({'error': str(e), 'groups': {}}, status=500)

def indicator_params_api(request):
    """Provides parameters for a specific TA-Lib function or custom indicator."""
    fn_name = request.GET.get('fn')
    if not fn_name:
        return JsonResponse({'error': 'Missing function name (fn parameter)'}, status=400)
    try:
        params = get_talib_params(fn_name)
        return JsonResponse({'params': params})
    except AttributeError:
        return JsonResponse({'error': f"Indicator function '{fn_name}' not found or params not available."}, status=404)
    except Exception as e:
        print(f"[VIEWS] Error in indicator_params_api for {fn_name}: {e}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

# --- AST Evaluation Logic ---
def eval_ast_node(symbol: str, ast_node: dict, context: dict) -> any:
    """
    Recursively evaluates an AST node for a given symbol.
    `context` caches DataFrames for the current symbol to avoid redundant loads.
    Handles AST from both Python Lark parser and JS parser.
    """
    node_type = ast_node.get("type")

    # If the AST node is not a dict, treat it as a literal
    if not isinstance(ast_node, dict):
        if isinstance(ast_node, (int, float, str)):
            return ast_node
        raise TypeError(f"AST node must be a dict or a literal, got: {type(ast_node)} for '{symbol}', Node: {ast_node}")

    # Handle numeric literals
    if node_type == "NumberLiteral":
        return ast_node["value"]

    # Handle field literals (e.g., CLOSE, OPEN)
    if node_type == "FieldLiteral":
        return str(ast_node["value"]).lower()

    # Handle indicator calls (including custom indicators like MACD_LINE, MACD_SIGNAL, etc.)
    if node_type == "IndicatorCall":
        ind_name = str(ast_node["name"])
        indicator_part = ast_node.get("part")  # e.g. for MACD.macd or STOCH.k
        tf = str(ast_node.get("timeframe", "daily")).lower()  # default to daily

        # Gather raw argument nodes from AST
        raw_args_list = ast_node.get("arguments", [])
        if not raw_args_list and "params" in ast_node:
            # Lark parser might have put params under "params"
            raw_args_list = ast_node.get("params", [])

        # Evaluate each argument (could be nested AST nodes)
        evaluated_args_values = []
        for arg_node in raw_args_list:
            if isinstance(arg_node, dict) and "type" in arg_node:
                evaluated_args_values.append(eval_ast_node(symbol, arg_node, context))
            else:
                evaluated_args_values.append(arg_node)

        # Build kwargs for calling the indicator function
        kwargs_for_call = {}
        param_schema = get_talib_params(ind_name)

        # Determine if this indicator expects a 'field' parameter
        expects_field_input = any(p["name"] == "real" for p in param_schema) or \
                              (ind_name.upper() in CUSTOM_INDICATORS and any(p["name"] == "field" for p in param_schema))

        arg_idx = 0
        if expects_field_input:
            # If the first evaluated arg is a string like "close", use it as the field
            if (evaluated_args_values
                and isinstance(evaluated_args_values[0], str)
                and evaluated_args_values[0].upper() in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]):
                kwargs_for_call["field"] = evaluated_args_values[0].lower()
                arg_idx += 1
            else:
                # Default to 'close'
                kwargs_for_call["field"] = "close"

        # If this is a custom indicator, map the remaining positional args to its parameters
        if ind_name.upper() in CUSTOM_INDICATORS:
            custom_param_schema = get_talib_params(ind_name)
            for schema_param in custom_param_schema:
                # Skip 'field' here because we already consumed it above (if present)
                if schema_param["name"] == "field":
                    continue

                if arg_idx < len(evaluated_args_values):
                    kwargs_for_call[schema_param["name"]] = evaluated_args_values[arg_idx]
                    arg_idx += 1

        else:
            # For built-in TA‐Lib indicators, map known param names
            # First, handle simple single-parameter cases like RSI(period)
            if len(param_schema) == 1 and param_schema[0]["name"] == "timeperiod" and arg_idx < len(evaluated_args_values):
                kwargs_for_call["period"] = evaluated_args_values[arg_idx]
                arg_idx += 1
            else:
                # A list of common TA-Lib parameter names
                common_param_names = [
                    "period", "fastperiod", "slowperiod", "signalperiod",
                    "nbdev", "multiplier", "fastk_period", "slowk_period", "slowd_period"
                ]
                for p_name in common_param_names:
                    # Map 'period' → 'timeperiod' in TA‐Lib
                    schema_equivalent = "timeperiod" if p_name == "period" else p_name
                    if any(p["name"] == schema_equivalent for p in param_schema):
                        if arg_idx < len(evaluated_args_values):
                            # Special case: BBANDS uses nbdevup/nbdevdn internally
                            if ind_name.upper() == "BBANDS" and p_name == "nbdev":
                                kwargs_for_call["nbdevup"] = evaluated_args_values[arg_idx]
                                kwargs_for_call["nbdevdn"] = evaluated_args_values[arg_idx]
                            else:
                                kwargs_for_call[p_name] = evaluated_args_values[arg_idx]
                            arg_idx += 1
                        # else: missing a value for this param, skip

        # Load (or retrieve from cache) the DataFrame for this symbol/timeframe
        df_key = f"{symbol}_{tf}"
        if df_key not in context:
            df = load_ohlcv(symbol, tf)
            if df is None or df.empty:
                raise ValueError(f"Data not found or empty for {symbol} ({tf}) for {ind_name}")
            context[df_key] = df
        df = context[df_key]

        # Call the indicator logic (custom or built-in) and return its result
        return call_indicator_logic(df, ind_name, indicator_part=indicator_part, **kwargs_for_call)

    # Handle comparisons (both Lark and JS AST shapes)
    if node_type in ["Comparison", "compare"]:
        op = ast_node.get("operator") or ast_node.get("op")
        left_val = eval_ast_node(symbol, ast_node["left"], context)
        right_val = eval_ast_node(symbol, ast_node["right"], context)
        return evaluate_operation(left_val, op, right_val)

    # Handle cross expressions
    if node_type in ["CrossExpression", "cross"]:
        op = ast_node.get("operator") or ast_node.get("op")
        left_val = eval_ast_node(symbol, ast_node["left"], context)
        right_val = eval_ast_node(symbol, ast_node["right"], context)
        return evaluate_operation(left_val, op, right_val)

    # Handle logical expressions (AND / OR)
    if node_type in ["BinaryExpression", "LogicalExpression", "logical", "logical_expr"]:
        op = str(ast_node.get("operator") or ast_node.get("op")).upper()
        left_val = eval_ast_node(symbol, ast_node["left"], context)

        # Short-circuit evaluation
        if op == "AND":
            return left_val and eval_ast_node(symbol, ast_node["right"], context)
        elif op == "OR":
            return left_val or eval_ast_node(symbol, ast_node["right"], context)
        raise ValueError(f"Unknown logical operator: {op}")

    # Handle unary NOT expressions
    if node_type in ["UnaryExpression", "not_expr"]:
        op_field = ast_node.get("operator")
        expr_field = ast_node.get("operand")
        if node_type == "not_expr":
            op_field = "NOT"
            expr_field = ast_node.get("expr")

        if op_field and op_field.upper() == "NOT":
            operand_val = eval_ast_node(symbol, expr_field, context)
            return not operand_val
        raise ValueError(f"Unknown unary operator: {op_field}")

    # Unknown node type
    raise ValueError(f"Unknown AST node type: '{node_type}' in node {ast_node} for symbol {symbol}")

def evaluate_ast_for_symbol(symbol: str, ast_main: dict) -> bool:
    """Helper to evaluate the main AST for a symbol, catching errors."""
    try:
        result = bool(eval_ast_node(symbol, ast_main, context={}))
        return result
    except Exception as e:
        print(f"[EVAL SYMBOL ERROR] Symbol: {symbol}, ErrorType: {type(e).__name__}, Msg: {e}")
        traceback.print_exc() # Uncomment for detailed error stack
        return False

# ---- Helper to get a display timeframe from AST ----
def get_display_timeframe_from_ast(ast_node: dict) -> str:
    """
    Attempts to find the first timeframe specified in an IndicatorCall node.
    Defaults to "daily" if none is explicitly found.
    """
    if isinstance(ast_node, dict):
        if ast_node.get("type") == "IndicatorCall" and "timeframe" in ast_node:
            # Ensure timeframe value is valid, otherwise default
            tf = str(ast_node["timeframe"]).lower()
            valid_tfs = ["daily", "weekly", "monthly", "1hour", "30min", "15min", "5min", "1min"]
            return tf if tf in valid_tfs else "daily"
        
        # Recursively search in other parts of the AST
        for key, value in ast_node.items():
            if key in ["left", "right", "arguments", "params", "expr", "operand"]: # Common keys holding sub-nodes
                if isinstance(value, list):
                    for item in value:
                        found_tf = get_display_timeframe_from_ast(item)
                        if found_tf != "daily": return found_tf # Prioritize non-default
                elif isinstance(value, dict):
                    found_tf = get_display_timeframe_from_ast(value)
                    if found_tf != "daily": return found_tf
    return "daily" # Default

# --- Main Screener Execution View ---
@csrf_exempt
def run_screener(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        body = json.loads(request.body)
        query_string = body.get("query_string") # From JS text area if sent
        ast_from_js = body.get("filters")     # AST from JS parser if sent
        ast_to_evaluate = None

        # Prefer query_string for Python Lark parser, fallback to JS AST
        if query_string:
            # print(f"[run_screener] Received query_string: '{query_string}'. Parsing with Python Lark parser.")
            ast_to_evaluate = parse_query(query_string) # from dsl_parser.py
            if isinstance(ast_to_evaluate, dict) and ast_to_evaluate.get("type") == "PARSE_ERROR": # Assuming dsl_parser returns this on failure
                 error_details = ast_to_evaluate.get('details', 'Syntax error in query string.')
                 print(f"[run_screener] Python Lark parser failed: {error_details}")
                 return JsonResponse({"error": f"Query Parsing Error (Server): {error_details}"}, status=400)
        elif ast_from_js:
            # print("[run_screener] Received AST from JS ('filters'). Using this AST.")
            ast_to_evaluate = ast_from_js
            if not isinstance(ast_to_evaluate, dict) or "type" not in ast_to_evaluate: # Basic validation
                print(f"[run_screener] ERROR: Invalid AST structure received from JS: {ast_to_evaluate}")
                return JsonResponse({"error": "Invalid query structure from client."}, status=400)
        else:
            print("[run_screener] ERROR: Neither 'query_string' nor 'filters' (AST) found in request.")
            return JsonResponse({"error": "Query is empty or malformed in request body."}, status=400)
        
        if not ast_to_evaluate: # Should be caught above, but as a safeguard
            print(f"[run_screener] ERROR: AST is None after attempting to parse/get from request.")
            return JsonResponse({"error": "Failed to process query into a usable structure."}, status=400)

        segment = body.get("segment", "Nifty 500") # Example: use segment to filter symbols
        
        # Determine the timeframe to list symbols for.
        # If the query implies a specific timeframe (e.g. "15min SMA(...)"),
        # it might be better to list symbols available for that timeframe.
        # For now, defaulting to "daily" for symbol listing, but data loading for eval uses AST timeframe.
        symbols_to_scan = list_symbols("daily") # TODO: Consider segment and query timeframe for symbol listing
        
        if not symbols_to_scan:
            print(f"[run_screener] WARNING: No symbols found by list_symbols('daily') for segment '{segment}'.")
            return JsonResponse({"error": "No symbols available for scanning. Check server data configuration."}, status=500)

        # print(f"[run_screener] AST to evaluate: {json.dumps(ast_to_evaluate, indent=2)}")
        # print(f"[run_screener] Scanning up to {len(symbols_to_scan)} symbols from segment '{segment}'. Sample: {symbols_to_scan[:5]}")

        results = []
        # Determine the timeframe to use for displaying results (e.g., from the first indicator)
        # This is a simplified approach; a complex query might use multiple timeframes.
        display_timeframe = get_display_timeframe_from_ast(ast_to_evaluate)
        print(f"[run_screener] Determined display timeframe from AST: {display_timeframe}")


        for symbol_to_test in symbols_to_scan[:50]: # Limiting for performance during testing
            if evaluate_ast_for_symbol(symbol_to_test, ast_to_evaluate):
                # Load data for the *display_timeframe* to show relevant latest data
                df_display = load_ohlcv(symbol_to_test, display_timeframe) 
                
                if df_display is not None and not df_display.empty:
                    latest = df_display.iloc[-1]
                    prev_close = df_display['close'].iloc[-2] if len(df_display) > 1 else latest['close']
                    
                    open_p = latest.get('open', np.nan)
                    high_p = latest.get('high', np.nan)
                    low_p = latest.get('low', np.nan)
                    close_p = latest.get('close', np.nan)
                    volume_v = latest.get('volume', np.nan)
                    
                    pct_change = ((close_p - prev_close) / prev_close * 100) if pd.notna(close_p) and pd.notna(prev_close) and prev_close != 0 else 0.0
                    
                    timestamp_val = latest.name # This is the index of the 'latest' row
                    
                    # MODIFIED: Format timestamp to include time if not daily
                    if display_timeframe != "daily" and pd.notna(timestamp_val):
                        timestamp_str = str(pd.to_datetime(timestamp_val)) # Full timestamp "YYYY-MM-DD HH:MM:SS"
                    elif pd.notna(timestamp_val):
                        timestamp_str = str(pd.to_datetime(timestamp_val).date()) # Date only for daily "YYYY-MM-DD"
                    else:
                        timestamp_str = "N/A"

                    results.append({
                        "symbol": symbol_to_test, "timestamp": timestamp_str,
                        "open": f"{open_p:.2f}" if pd.notna(open_p) else "N/A",
                        "high": f"{high_p:.2f}" if pd.notna(high_p) else "N/A",
                        "low": f"{low_p:.2f}" if pd.notna(low_p) else "N/A",
                        "close": f"{close_p:.2f}" if pd.notna(close_p) else "N/A",
                        "volume": f"{int(volume_v):,}" if pd.notna(volume_v) and pd.notna(volume_v) else "N/A",
                        "change_pct": f"{pct_change:.2f}%"
                    })
        
        # print(f"[run_screener] Scan complete. Found {len(results)} matches.")
        return JsonResponse({"results": results})

    except json.JSONDecodeError:
        print("[run_screener] ERROR: Invalid JSON payload.")
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e_global:
        error_type = type(e_global).__name__
        print(f"[run_screener] GLOBAL ERROR: {error_type} - {e_global}")
        traceback.print_exc()
        return JsonResponse({"error": f"Server error: {error_type} - {str(e_global)}"}, status=500)
