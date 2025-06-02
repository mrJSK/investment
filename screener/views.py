# screener/views.py

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from screener.models import SavedScan
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
def eval_ast_node(symbol, ast_node, context):
    """
    Recursively evaluate the AST for a given symbol.
    Returns either a pandas Series of booleans (if indicator returns a series),
    or a single boolean (for the latest bar), or False (if data is missing).
    """

    node_type = ast_node["type"].upper()

    # --- Comparison: "left operator right", e.g. (RSI > 40) or (SMA14 < EMA20)
    if node_type == "COMPARISON":
        # Evaluate left and right. If either returns False (missing data), comparison is False.
        left_val  = eval_ast_node(symbol, ast_node["left"], context)
        right_val = eval_ast_node(symbol, ast_node["right"], context)

        # If we got False (missing) for either, treat the comparison as False
        if left_val is False or right_val is False:
            return False

        # At this point left_val and right_val should be either scalars or pandas Series.
        op = ast_node["operator"]

        try:
            if isinstance(left_val, (pd.Series, pd.DataFrame)) or isinstance(right_val, (pd.Series, pd.DataFrame)):
                # Element‐wise comparison → returns a Series of booleans
                if op == ">":
                    return left_val > right_val
                if op == "<":
                    return left_val < right_val
                if op == ">=":
                    return left_val >= right_val
                if op == "<=":
                    return left_val <= right_val
                if op == "==":
                    return left_val == right_val
                if op == "!=":
                    return left_val != right_val
                # Add other operators if needed...
                raise ValueError(f"Unknown comparison operator: {op}")
            else:
                # Scalar comparison → returns a single boolean
                if op == ">":
                    return left_val > right_val
                if op == "<":
                    return left_val < right_val
                if op == ">=":
                    return left_val >= right_val
                if op == "<=":
                    return left_val <= right_val
                if op == "==":
                    return left_val == right_val
                if op == "!=":
                    return left_val != right_val
                raise ValueError(f"Unknown comparison operator: {op}")
        except Exception as e:
            # In case of any weird type mismatch, treat as False
            print(f"[eval_ast_node][Comparison] Error comparing {symbol}: {e}")
            return False

    # --- BinaryExpression: "left AND/OR right"
    if node_type == "BINARYEXPRESSION":
        op = ast_node["operator"].upper()  # should be "AND" or "OR"
        # First, evaluate the left side
        left_val = eval_ast_node(symbol, ast_node["left"], context)

        # If left_val is a pandas Series (element‐wise), or a single boolean:
        #  For OR: if left_val is True (or contains any True), short‐circuit and return that.
        #  For AND: if left_val is False (or all False), short‐circuit and return that.

        # Normalize left_val to a pandas Series if it is a boolean:
        if isinstance(left_val, bool):
            left_bool_series = pd.Series([left_val])
        else:
            left_bool_series = left_val

        if op == "OR":
            # If ANY element of left_bool_series is True, OR short-circuits
            if left_bool_series.any():
                return left_val  # return left (could be scalar or series)
            # Else evaluate right side
            right_val = eval_ast_node(symbol, ast_node["right"], context)
            # If right_val is False (missing data) → return False (no match)
            if right_val is False:
                return False
            # Now OR the two sides (scalar or series)
            if isinstance(right_val, bool):
                return left_bool_series.any() or right_val
            return left_val | right_val  # element‐wise OR if series

        elif op == "AND":
            # If ALL elements of left_bool_series are False, AND short-circuits
            if not left_bool_series.any():
                return left_val  # false-ish → no need to check right
            # Else evaluate right side
            right_val = eval_ast_node(symbol, ast_node["right"], context)
            if right_val is False:
                return False
            # Now AND the two sides
            if isinstance(right_val, bool):
                return left_bool_series.all() and right_val
            return left_val & right_val  # element‐wise AND

        else:
            print(f"[eval_ast_node][BinaryExpression] Unknown logical operator: {op}")
            return False

    # --- IndicatorCall: e.g. "15min RSI(CLOSE,14)" or "Daily SMA(CLOSE,20)"
    if node_type == "INDICATORCALL":
        ind_name = str(ast_node["name"])
        indicator_part = ast_node.get("part")
        tf = str(ast_node.get("timeframe", "daily")).lower()

        raw_args_list = ast_node.get("arguments", [])
        if not raw_args_list and "params" in ast_node: # Compatibility with Lark parser output
            raw_args_list = ast_node.get("params", [])

        # ---->>>> CRITICAL: Evaluate each argument AST node to get its actual value <<<<----
        evaluated_args_values = []
        for arg_node in raw_args_list:
            # If arg_node is already a simple type (e.g. from Lark parser that directly returns values for literals)
            if isinstance(arg_node, (str, int, float)):
                evaluated_args_values.append(arg_node)
            # If it's an AST node from JS parser or a nested indicator call from Lark
            elif isinstance(arg_node, dict) and "type" in arg_node:
                evaluated_args_values.append(eval_ast_node(symbol, arg_node, context))
            else:
                # If it's some other unexpected type, it might cause issues later
                # For now, let's pass it along, but this could be a source of errors.
                print(f"WARN [eval_ast_node] Unexpected argument type for {ind_name}: {type(arg_node)}, value: {arg_node}")
                evaluated_args_values.append(arg_node)
        # ---->>>> END CRITICAL CORRECTION <<<<----

        # Build kwargs for calling the indicator function
        kwargs_for_call = {}
        param_schema = get_talib_params(ind_name) # from indicator_utils.py

        current_eval_arg_idx = 0

        # Iterate through the expected parameters defined in the schema
        for schema_item in param_schema:
            param_name_for_kwarg = schema_item['name'] # This is the frontend-friendly name

            if param_name_for_kwarg == 'field':
                # Handle 'field' argument (e.g., 'close', 'open')
                if current_eval_arg_idx < len(evaluated_args_values) and \
                   isinstance(evaluated_args_values[current_eval_arg_idx], str) and \
                   evaluated_args_values[current_eval_arg_idx].upper() in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]:
                    kwargs_for_call['field'] = evaluated_args_values[current_eval_arg_idx].lower()
                    current_eval_arg_idx += 1
                elif not ind_name.upper().startswith("STOCH_"): # STOCH custom functions handle HLC internally
                    kwargs_for_call['field'] = 'close' # Default to 'close' if not provided or not a string
            
            elif param_name_for_kwarg != 'field': # For other parameters (typically numeric)
                if current_eval_arg_idx < len(evaluated_args_values):
                    arg_value = evaluated_args_values[current_eval_arg_idx]
                    
                    # Ensure numeric arguments are converted correctly
                    # The error int() ... not 'dict' happens if arg_value is still a dict here.
                    # The recursive eval_ast_node for NumberLiteral should have returned a float/int.
                    if not isinstance(arg_value, (int, float)):
                         print(f"ERROR [eval_ast_node] Expected numeric value for '{param_name_for_kwarg}' in '{ind_name}', but got {type(arg_value)}: {arg_value}")
                         # Optionally, try to use default if conversion fails, or raise error
                         if "default" in schema_item and schema_item["default"] is not None:
                            arg_value = schema_item["default"]
                         else: # No valid value, no default, this will likely cause an error in call_indicator_logic
                            return False # Or raise an error

                    kwargs_for_call[param_name_for_kwarg] = arg_value
                    current_eval_arg_idx += 1
                elif "default" in schema_item and schema_item["default"] is not None:
                    kwargs_for_call[param_name_for_kwarg] = schema_item["default"]
        
        # Default 'field' to 'close' if it's in schema but not yet in kwargs_for_call
        # (and not for STOCH_K/STOCH_D which handle HLC internally)
        if any(p['name'] == 'field' for p in param_schema) and \
           'field' not in kwargs_for_call and \
           not ind_name.upper().startswith("STOCH_"):
            kwargs_for_call['field'] = 'close'

        print(f"DEBUG [eval_ast_node] Indicator: {ind_name}({tf}), Prepared kwargs_for_call: {kwargs_for_call}")

        # Load (or retrieve from cache) the DataFrame for this symbol/timeframe
        df_key = f"{symbol}_{tf}"
        if df_key not in context:
            df = load_ohlcv(symbol, tf)
            if df is None or df.empty:
                # This print is what you see for the "Missing data" error
                print(f"[EVAL SYMBOL ERROR] Symbol: {symbol}, Missing data for {tf} when computing {ind_name}")
                raise ValueError(f"Data not found or empty for {symbol} ({tf}) for {ind_name}") # Raise to be caught by evaluate_ast_for_symbol
            context[df_key] = df
        df = context[df_key]
        
        return call_indicator_logic(df, ind_name, indicator_part=indicator_part, **kwargs_for_call)

    # --- FieldLiteral: e.g. "CLOSE" with no timeframe means “latest close price”
    if node_type == "FIELDLITERAL":
        field_name = ast_node["value"].lower()  # e.g. "close", "open"
        # Assume that you always have “df_daily” in context or reload on demand
        df_daily = load_ohlcv(symbol, "daily")
        if df_daily is None or df_daily.empty:
            return False
        try:
            # Return the most recent bar’s field value as a scalar
            return df_daily[field_name].iloc[-1]
        except Exception as e:
            print(f"[eval_ast_node][FieldLiteral] Error fetching field for {symbol}: {e}")
            return False

    # --- NumberLiteral: e.g. 14, 40, etc.
    if node_type == "NUMBERLITERAL":
        return ast_node["value"]

    # If we reach an unexpected node type, return False
    print(f"[eval_ast_node] Unknown AST node type: {node_type}")
    return False

# ----------------------------------------------------------------
# Example helper: compute_indicator() 
# (You must already have similar logic in your code. Just ensure that
#  it never lets a missing‐data situation bubble up as an exception.)
# ----------------------------------------------------------------
def compute_indicator(name, args, df):
    """
    Compute various indicators by name on df (a pandas DataFrame indexed by timestamp),
    using arguments args (a list of AST nodes already evaluated to scalars or fields).

    Must return either a pandas Series of booleans/floats (if the indicator yields a series),
    or a single scalar (e.g. float) if it’s something like "CLOSE()" or "FIELD()".

    Raise ValueError if the arguments are invalid.
    """
    name = name.upper()

    if name == "CLOSE":
        # No args → just return the full close series
        return df["close"]
    if name == "OPEN":
        return df["open"]
    if name == "HIGH":
        return df["high"]
    if name == "LOW":
        return df["low"]
    if name == "VOLUME":
        return df["volume"]

    if name == "SMA":
        # args = [FieldLiteral("close"), NumberLiteral(14)]
        series_node = args[0]
        period = args[1]
        # We assume the first argument is always a FieldLiteral pointing to df[field]
        series = df[series_node["value"].lower()]
        return series.rolling(int(period), min_periods=1).mean()

    if name == "RSI":
        # args = [FieldLiteral("close"), NumberLiteral(14)]
        series_node = args[0]
        period = int(args[1])
        series = df[series_node["value"].lower()]
        # A quick RSI implementation (you can replace with TA‐Lib or pandas‐ta)
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        rs = avg_gain / (avg_loss.replace(0, 1e-9))  # avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        return rsi

    # Add other indicators (EMA, MACD, etc.) here…

    raise ValueError(f"Unsupported indicator: {name}")

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
    

def saved_scans_list(request):
    """
    GET /screener/api/saved_scans/
    Returns a JSON array of all saved scans, ordered by newest first.
    Each item: { id, name, filters, segment, created_at }.
    """
    if request.method != "GET":
        return JsonResponse({"error": "GET method required"}, status=400)

    scans = SavedScan.objects.order_by("-created_at")
    data = []
    for scan in scans:
        data.append({
            "id": scan.id,
            "name": scan.name,
            "filters": scan.filters_json,
            "segment": scan.segment,
            "created_at": scan.created_at.isoformat(),
        })
    return JsonResponse({"saved_scans": data})


@csrf_exempt
def save_scan(request):
    """
    POST /screener/api/save_scan/
    Expects JSON body:
      {
        "name": "<Scan Name>",
        "filters": { …structured JSON from transformQueryStringToBackendStructure… },
        "segment": "<selected segment>"
      }
    Returns {"success": true, "scan": { …saved scan… }} on success,
            {"error": "..."} on failure.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = payload.get("name", "").strip()
    filters = payload.get("filters")
    segment = payload.get("segment", "").strip()

    if not name:
        return JsonResponse({"error": "Missing scan name"}, status=400)
    if not filters:
        return JsonResponse({"error": "Missing filters"}, status=400)
    if not segment:
        return JsonResponse({"error": "Missing segment"}, status=400)

    # Save into the database
    scan = SavedScan.objects.create(
        name=name,
        filters_json=filters,
        segment=segment
    )
    return JsonResponse({
        "success": True,
        "scan": {
            "id": scan.id,
            "name": scan.name,
            "filters": scan.filters_json,
            "segment": scan.segment,
            "created_at": scan.created_at.isoformat(),
        }
    })
