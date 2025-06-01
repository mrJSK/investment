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
    Handles AST from both Python Lark parser and potentially simpler JS parser.
    """
    node_type = ast_node.get("type")

    if not isinstance(ast_node, dict):
        if isinstance(ast_node, (int, float, str)): return ast_node
        raise TypeError(f"AST node must be a dictionary or a literal, got: {type(ast_node)} for '{symbol}', Node: {ast_node}")

    # print(f"--- [eval_ast_node] Symbol: {symbol}, Type: {node_type}, Node: {ast_node} ---")

    if node_type == "NumberLiteral": # Common for both JS and Lark (via value rule)
        return ast_node["value"]
    if node_type == "FieldLiteral": # Common for both
        return str(ast_node["value"]).lower()

    if node_type == "IndicatorCall": # Common for both (Lark: indicator_full_call)
        ind_name = str(ast_node["name"]) # Assumes already uppercased by transformer
        indicator_part = ast_node.get("part")
        tf = str(ast_node.get("timeframe", "daily")).lower()

        raw_args_list = ast_node.get("arguments", [])
        evaluated_args_values = []
        for arg_node in raw_args_list:
            # If arg_node is a dict, it's likely a nested AST node (e.g., from JS parser or Lark for nested indicators)
            # If it's a primitive, it's likely from Lark transformer for simple params (like numbers, field strings)
            if isinstance(arg_node, dict) and "type" in arg_node:
                evaluated_args_values.append(eval_ast_node(symbol, arg_node, context))
            else: # Already a primitive value from Lark transformer
                evaluated_args_values.append(arg_node)
        
        # Prepare kwargs for call_indicator_logic
        # This mapping is crucial and needs to be robust.
        kwargs_for_call = {}
        # Using get_talib_params to help map, but still relies on order for unnamed params from AST
        # A more robust solution would involve named parameters in the grammar if possible,
        # or a more sophisticated mapping based on function signatures.
        
        # Heuristic mapping based on common indicator patterns and number of args
        # This is the most complex part to generalize perfectly.
        param_schema = get_talib_params(ind_name) # Get schema for TA-Lib or custom
        
        # Try to map based on common names if present in schema
        # This is a simplified approach. A full dynamic mapping is complex.
        if ind_name in ["SMA", "EMA", "RSI", "ATR", "ADX", "CCI", "MOM", "ROC", "STDDEV", "WMA", "DEMA", "TEMA", "KAMA", "TRIMA", "T3", "EFI"]:
            if len(evaluated_args_values) == 1 and isinstance(evaluated_args_values[0], (int, float)): # period
                kwargs_for_call['period'] = evaluated_args_values[0]
                # Check if 'field' is an implicit or expected param
                if any(p['name'] == 'real' for p in param_schema) or any(p['name'] == 'field' for p in param_schema if ind_name.upper() in CUSTOM_INDICATORS):
                    kwargs_for_call.setdefault('field', 'close')
            elif len(evaluated_args_values) == 2 and isinstance(evaluated_args_values[0], str): # field, period
                 kwargs_for_call['field'] = evaluated_args_values[0]
                 kwargs_for_call['period'] = evaluated_args_values[1]
        elif ind_name == "MACD":
            kwargs_for_call['field'] = 'close' # Default for MACD
            if len(evaluated_args_values) == 3: # fast, slow, signal
                kwargs_for_call['fastperiod'] = evaluated_args_values[0]
                kwargs_for_call['slowperiod'] = evaluated_args_values[1]
                kwargs_for_call['signalperiod'] = evaluated_args_values[2]
            elif len(evaluated_args_values) == 4 and isinstance(evaluated_args_values[0], str): # field, fast, slow, signal
                kwargs_for_call['field'] = evaluated_args_values[0]
                kwargs_for_call['fastperiod'] = evaluated_args_values[1]
                kwargs_for_call['slowperiod'] = evaluated_args_values[2]
                kwargs_for_call['signalperiod'] = evaluated_args_values[3]
        elif ind_name == "BBANDS":
            if len(evaluated_args_values) >= 2:
                kwargs_for_call['field'] = evaluated_args_values[0]
                kwargs_for_call['period'] = evaluated_args_values[1]
                if len(evaluated_args_values) >= 3: kwargs_for_call['nbdev'] = evaluated_args_values[2]
                # matype could be added if grammar supports it
        # For other indicators or if above heuristics fail, pass args as a list if `call_indicator_logic` can handle it
        # or if it's a custom indicator that expects positional args via a list in `args_list`.
        if not kwargs_for_call and evaluated_args_values:
            # This is a fallback - call_indicator_logic's custom part would need to handle 'args_list'
            # Or, for TA-Lib, it might fail if specific named params are strictly required.
            # Best to define explicit kwargs_for_call for all supported indicators.
            # For custom indicators, ensure their Python function signature matches what's built here.
            if ind_name in CUSTOM_INDICATORS: # Custom indicators might take specific named args
                 # Try to map based on the custom indicator's parameter names from get_talib_params
                custom_params_schema = get_talib_params(ind_name) # This now returns params for custom too
                for i, schema_param in enumerate(custom_params_schema):
                    if i < len(evaluated_args_values):
                        kwargs_for_call[schema_param['name']] = evaluated_args_values[i]
            else: # Fallback for unmapped TA-Lib or if custom schema is simple
                 kwargs_for_call['args_list'] = evaluated_args_values


        df_key = f"{symbol}_{tf}"
        if df_key not in context:
            df = load_ohlcv(symbol, tf)
            if df is None or df.empty:
                raise ValueError(f"Data not found/empty for {symbol} ({tf}) for {ind_name}")
            context[df_key] = df
        df = context[df_key]

        return call_indicator_logic(df, ind_name, indicator_part=indicator_part, **kwargs_for_call)

    # Node types from Lark parser (preferred) and JS parser (fallback)
    if node_type in ["Comparison", "compare"]:
        op = ast_node.get("operator") or ast_node.get("op")
        left_val = eval_ast_node(symbol, ast_node["left"], context)
        right_val = eval_ast_node(symbol, ast_node["right"], context)
        return evaluate_operation(left_val, op, right_val)

    if node_type in ["CrossExpression", "cross"]:
        op = ast_node.get("operator") or ast_node.get("op")
        left_val = eval_ast_node(symbol, ast_node["left"], context)
        right_val = eval_ast_node(symbol, ast_node["right"], context)
        return evaluate_operation(left_val, op, right_val)

    if node_type in ["BinaryExpression", "LogicalExpression", "logical_expr"]:
        op = (ast_node.get("operator") or ast_node.get("op")).upper()
        left_val = eval_ast_node(symbol, ast_node["left"], context)
        if op == "AND":
            return left_val and eval_ast_node(symbol, ast_node["right"], context)
        elif op == "OR":
            return left_val or eval_ast_node(symbol, ast_node["right"], context)
        raise ValueError(f"Unknown binary/logical operator: {op}")

    if node_type in ["UnaryExpression", "not_expr"]:
        op_field = ast_node.get("operator") # JS AST
        expr_field = ast_node.get("operand") # JS AST
        if node_type == "not_expr": # Lark AST
            op_field = "NOT"
            expr_field = ast_node.get("expr")
        
        if op_field and op_field.upper() == "NOT":
            operand_val = eval_ast_node(symbol, expr_field, context)
            return not operand_val
        raise ValueError(f"Unknown unary operator: {op_field}")

    if node_type == "SentimentCondition" or node_type == "sentiment_expr":
        indicator_node = ast_node["indicator"]
        sentiment = ast_node["sentiment"]
        indicator_name = str(indicator_node.get("name", "UNKNOWN_IND")).upper()
        indicator_tf = str(indicator_node.get("timeframe", "daily")).lower()
        
        # Argument preparation for the indicator within sentiment condition
        raw_sentiment_args = indicator_node.get("arguments", [])
        sentiment_indicator_kwargs = {}
        # Reuse the kwargs mapping logic from IndicatorCall if possible, or simplify
        # This example assumes simple period-based indicators for sentiment
        if indicator_name in ["RSI", "EFI"]:
            if raw_sentiment_args:
                arg_val = raw_sentiment_args[0]
                sentiment_indicator_kwargs['period'] = eval_ast_node(symbol, arg_val, context) if isinstance(arg_val, dict) else arg_val
            sentiment_indicator_kwargs.setdefault('field', 'close')
        elif indicator_name == "MACD":
            if len(raw_sentiment_args) == 3:
                sentiment_indicator_kwargs['field'] = 'close'
                sentiment_indicator_kwargs['fastperiod'] = eval_ast_node(symbol, raw_sentiment_args[0], context) if isinstance(raw_sentiment_args[0],dict) else raw_sentiment_args[0]
                sentiment_indicator_kwargs['slowperiod'] = eval_ast_node(symbol, raw_sentiment_args[1], context) if isinstance(raw_sentiment_args[1],dict) else raw_sentiment_args[1]
                sentiment_indicator_kwargs['signalperiod'] = eval_ast_node(symbol, raw_sentiment_args[2], context) if isinstance(raw_sentiment_args[2],dict) else raw_sentiment_args[2]
            # Add case for 4 args if field is explicit

        df_key = f"{symbol}_{indicator_tf}"
        if df_key not in context:
            df = load_ohlcv(symbol, indicator_tf)
            if df is None or df.empty:
                raise ValueError(f"Data not found for {symbol} ({indicator_tf}) for SentimentCondition on {indicator_name}")
            context[df_key] = df
        df = context[df_key]

        if sentiment == "is bullish":
            if indicator_name == "RSI":
                rsi_value = call_indicator_logic(df, "RSI", **sentiment_indicator_kwargs)
                return pd.notna(rsi_value) and rsi_value > 60
            elif indicator_name == "MACD":
                macd_line = call_indicator_logic(df, "MACD", indicator_part="macd", **sentiment_indicator_kwargs)
                signal_line = call_indicator_logic(df, "MACD", indicator_part="signal", **sentiment_indicator_kwargs)
                if pd.isna(macd_line) or pd.isna(signal_line): return False
                return macd_line > signal_line
            elif indicator_name == "EFI":
                efi_value = call_indicator_logic(df, "EFI", **sentiment_indicator_kwargs)
                return pd.notna(efi_value) and efi_value > 0
            return False
        elif sentiment == "is bearish":
            if indicator_name == "RSI":
                rsi_value = call_indicator_logic(df, "RSI", **sentiment_indicator_kwargs)
                return pd.notna(rsi_value) and rsi_value < 40
            elif indicator_name == "MACD":
                macd_line = call_indicator_logic(df, "MACD", indicator_part="macd", **sentiment_indicator_kwargs)
                signal_line = call_indicator_logic(df, "MACD", indicator_part="signal", **sentiment_indicator_kwargs)
                if pd.isna(macd_line) or pd.isna(signal_line): return False
                return macd_line < signal_line
            elif indicator_name == "EFI":
                efi_value = call_indicator_logic(df, "EFI", **sentiment_indicator_kwargs)
                return pd.notna(efi_value) and efi_value < 0
            return False
        return False

    if node_type == "MathExpression" or node_type == "math_expr":
        op = ast_node.get("operator") or ast_node.get("op")
        left_val = eval_ast_node(symbol, ast_node["left"], context)
        right_val = eval_ast_node(symbol, ast_node["right"], context)
        if pd.isna(left_val) or pd.isna(right_val): return np.nan
        if op == '+': return left_val + right_val
        if op == '-': return left_val - right_val
        if op == '*': return left_val * right_val
        if op == '/': return left_val / right_val if right_val != 0 and pd.notna(right_val) else np.nan
        raise ValueError(f"Unknown math operator: {op}")

    raise ValueError(f"Unknown AST node type: '{node_type}' in node {ast_node} for symbol {symbol}")

def evaluate_ast_for_symbol(symbol: str, ast_main: dict) -> bool:
    """Helper to evaluate the main AST for a symbol, catching errors."""
    try:
        result = bool(eval_ast_node(symbol, ast_main, context={}))
        return result
    except Exception as e:
        print(f"[EVAL SYMBOL ERROR] Symbol: {symbol}, ErrorType: {type(e).__name__}, Msg: {e}")
        # traceback.print_exc()
        return False

# --- Main Screener Execution View ---
@csrf_exempt
def run_screener(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        body = json.loads(request.body)
        query_string = body.get("query_string")
        ast_from_js = body.get("filters") # AST from JavaScript parser (optional fallback)
        ast_to_evaluate = None

        if query_string:
            # print(f"[run_screener] Received query_string: '{query_string}'. Parsing with Python Lark parser.")
            ast_to_evaluate = parse_query(query_string) # from dsl_parser.py
            if isinstance(ast_to_evaluate, dict) and ast_to_evaluate.get("type") == "PARSE_ERROR":
                 error_details = ast_to_evaluate.get('details', 'Syntax error')
                 print(f"[run_screener] Python Lark parser failed: {error_details}")
                 return JsonResponse({"error": f"Query Parsing Error (Server): {error_details}"}, status=400)
        elif ast_from_js:
            # print("[run_screener] Received AST from JS ('filters'). Using this AST.")
            ast_to_evaluate = ast_from_js
            if not isinstance(ast_to_evaluate, dict) or "type" not in ast_to_evaluate:
                print(f"[run_screener] ERROR: Invalid AST structure received from JS: {ast_to_evaluate}")
                return JsonResponse({"error": "Invalid query structure from client."}, status=400)
        else:
            print("[run_screener] ERROR: Neither 'query_string' nor 'filters' (AST) found.")
            return JsonResponse({"error": "Query is empty in request body."}, status=400)
        
        if not ast_to_evaluate:
            print(f"[run_screener] ERROR: AST is None after attempting to parse/get from request.")
            return JsonResponse({"error": "Failed to process query into a usable structure."}, status=400)

        segment = body.get("segment", "Nifty 500")
        symbols_to_scan = list_symbols("daily") # TODO: Make segment actually filter symbols
        if not symbols_to_scan:
            print("[run_screener] WARNING: No symbols found by list_symbols('daily').")
            return JsonResponse({"error": "No symbols available for scanning. Check server data configuration."}, status=500)

        # print(f"[run_screener] Scanning up to {len(symbols_to_scan)} symbols from segment '{segment}'. Sample: {symbols_to_scan[:5]}")

        results = []
        for symbol_to_test in symbols_to_scan[:50]: # Limiting for performance during testing
            if evaluate_ast_for_symbol(symbol_to_test, ast_to_evaluate):
                df_display = load_ohlcv(symbol_to_test, "daily") 
                if df_display is not None and not df_display.empty:
                    latest = df_display.iloc[-1]
                    prev_close = df_display['close'].iloc[-2] if len(df_display) > 1 else latest['close']
                    
                    open_p = latest.get('open', np.nan)
                    high_p = latest.get('high', np.nan)
                    low_p = latest.get('low', np.nan)
                    close_p = latest.get('close', np.nan)
                    volume_v = latest.get('volume', np.nan)
                    
                    pct_change = ((close_p - prev_close) / prev_close * 100) if pd.notna(close_p) and pd.notna(prev_close) and prev_close != 0 else 0.0
                    
                    timestamp_val = latest.name 
                    timestamp_str = str(pd.to_datetime(timestamp_val).date()) if pd.notna(timestamp_val) else "N/A"

                    results.append({
                        "symbol": symbol_to_test, "timestamp": timestamp_str,
                        "open": f"{open_p:.2f}" if pd.notna(open_p) else "N/A",
                        "high": f"{high_p:.2f}" if pd.notna(high_p) else "N/A",
                        "low": f"{low_p:.2f}" if pd.notna(low_p) else "N/A",
                        "close": f"{close_p:.2f}" if pd.notna(close_p) else "N/A",
                        "volume": f"{int(volume_v):,}" if pd.notna(volume_v) else "N/A",
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

