# screener/views.py

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import talib

from screener.backtest_engine import run_backtest
from screener.models import SavedScan

from .indicator_utils import (
    CUSTOM_INDICATORS,
    TA_INDICATOR_LABELS,
    call_indicator_logic, # Now returns full series
    get_talib_grouped_indicators,
    get_talib_params,
    list_symbols,
    load_ohlcv,
)
from .dsl_parser import parse_query

import json
import pandas as pd
import numpy as np
import traceback
import inspect


# --- Helper functions for AST processing (No changes) ---

def reconstruct_arg_string(arg_node):
    """Recursively reconstructs a string representation of an argument node."""
    if not isinstance(arg_node, dict) or 'type' not in arg_node:
        return str(arg_node) # For simple values like numbers
        
    node_type = arg_node['type']
    if node_type == 'FieldLiteral':
        return f"{arg_node.get('value', '').upper()}()"
    elif node_type == 'NumberLiteral':
        return str(arg_node.get('value', ''))
    elif node_type == 'IndicatorCall':
        return reconstruct_indicator_string_from_node(arg_node)
    return '?'

def reconstruct_indicator_string_from_node(node):
    """Constructs a readable string from an IndicatorCall AST node."""
    if not isinstance(node, dict) or node.get('type') != 'IndicatorCall':
        return ""
    
    name = node.get('name', 'UNKNOWN')
    timeframe = node.get('timeframe', 'Daily').capitalize()
    
    args_list = node.get('arguments', node.get('params', []))
    args = ", ".join([reconstruct_arg_string(arg) for arg in args_list])

    part = f".{node['part']}" if node.get('part') else ""
    return f"{timeframe} {name}({args}){part}"

def get_indicator_nodes_from_ast(ast_node):
    """Recursively traverses the AST to find all unique IndicatorCall nodes."""
    nodes = []
    
    if not isinstance(ast_node, dict):
        return nodes

    if ast_node.get("type") == "IndicatorCall":
        nodes.append(ast_node)

    for key, value in ast_node.items():
        if isinstance(value, dict):
            nodes.extend(get_indicator_nodes_from_ast(value))
        elif isinstance(value, list):
            for item in value:
                nodes.extend(get_indicator_nodes_from_ast(item))
    
    unique_nodes = {reconstruct_indicator_string_from_node(n): n for n in nodes}
    return list(unique_nodes.values())


# --- Main Dashboard View (No changes) ---
class DashboardView(TemplateView):
    template_name = 'screener/dashboard.html'

# --- API Endpoints for Frontend (No changes) ---
def indicator_list_api(request):
    try:
        grouped_indicators = get_talib_grouped_indicators()
        return JsonResponse({'groups': grouped_indicators})
    except Exception as e:
        print(f"[VIEWS.PY] indicator_list_api: ERROR - {e}")
        traceback.print_exc()
        return JsonResponse({'error': str(e), 'groups': {}}, status=500)

def indicator_params_api(request):
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


# --- AST Evaluation Logic (CRITICAL CHANGES HERE) ---
def eval_ast_node(symbol, ast_node, context):
    """
    Recursively evaluate the AST for a given symbol.
    Returns either a pandas Series (for indicators) or a boolean/scalar (for comparisons/literals).
    `context` must include 'current_date' for backtesting point-in-time data loading.
    For regular screener runs, 'current_date' will be None, indicating to load all available data.
    """

    node_type = ast_node.get("type", "").upper()
    current_date = context.get('current_date', None)

    # --- Comparison: "left operator right"
    if node_type == "COMPARISON":
        left_val  = eval_ast_node(symbol, ast_node["left"], context)
        right_val = eval_ast_node(symbol, ast_node["right"], context)

        # Before comparison, ensure values are ready.
        # If left_val is an empty Series (e.g., from insufficient data), treat as NaN/False.
        if isinstance(left_val, pd.Series) and left_val.empty:
            return False
        # If right_val is an empty Series, treat as NaN/False.
        if isinstance(right_val, pd.Series) and right_val.empty:
            return False

        op = ast_node["operator"]
        try:
            # For direct comparisons (>, <, == etc.), we need the last value of the series.
            # For crosses, we need the full series to apply shift().

            # Convert left_val to scalar if it's a Series and operator is not CROSS
            if isinstance(left_val, pd.Series) and not op.upper().startswith("CROSS"):
                left_val_scalar = left_val.iloc[-1]
            else:
                left_val_scalar = left_val # Keep as series for crosses, or as already scalar

            # Convert right_val to scalar if it's a Series and operator is not CROSS
            if isinstance(right_val, pd.Series) and not op.upper().startswith("CROSS"):
                right_val_scalar = right_val.iloc[-1]
            else:
                right_val_scalar = right_val # Keep as series for crosses, or as already scalar
            
            # --- Perform Comparison ---
            if op == ">": return bool(left_val_scalar > right_val_scalar)
            elif op == "<": return bool(left_val_scalar < right_val_scalar)
            elif op == ">=": return bool(left_val_scalar >= right_val_scalar)
            elif op == "<=": return bool(left_val_scalar <= right_val_scalar)
            elif op == "==": return bool(left_val_scalar == right_val_scalar)
            elif op == "!=": return bool(left_val_scalar != right_val_scalar)
            
            # --- CROSSES operators: Use full series for shift, then take last boolean ---
            elif op.upper() == "CROSSES ABOVE":
                # Ensure left_val is a Series
                if not isinstance(left_val, (pd.Series, np.ndarray)) or left_val.empty:
                    return False

                # If right_val is a scalar, convert it to a Series of the same length/index as left_val
                if isinstance(right_val, (float, int, np.number)):
                    if hasattr(left_val, 'index'): # Use original Series index for alignment
                        right_val_series = pd.Series(right_val, index=left_val.index)
                    else: # Fallback for pure numpy array case, create a simple array
                        right_val_series = np.full_like(left_val, right_val, dtype=float)
                elif isinstance(right_val, (pd.Series, np.ndarray)):
                    right_val_series = right_val
                else:
                    return False
                
                # Need at least 2 bars for a cross
                if len(left_val) < 2 or len(right_val_series) < 2:
                    return False
                
                # Perform the cross-over logic
                cross_result_series = (left_val.shift(1) < right_val_series.shift(1)) & (left_val > right_val_series)
                
                # Return the boolean result for the latest bar
                return bool(cross_result_series.iloc[-1]) if not cross_result_series.empty and pd.notna(cross_result_series.iloc[-1]) else False

            elif op.upper() == "CROSSES BELOW":
                if not isinstance(left_val, (pd.Series, np.ndarray)) or left_val.empty:
                    return False

                if isinstance(right_val, (float, int, np.number)):
                    if hasattr(left_val, 'index'):
                        right_val_series = pd.Series(right_val, index=left_val.index)
                    else:
                        right_val_series = np.full_like(left_val, right_val, dtype=float)
                elif isinstance(right_val, (pd.Series, np.ndarray)):
                    right_val_series = right_val
                else:
                    return False

                if len(left_val) < 2 or len(right_val_series) < 2:
                    return False
                
                cross_result_series = (left_val.shift(1) > right_val_series.shift(1)) & (left_val < right_val_series)
                
                return bool(cross_result_series.iloc[-1]) if not cross_result_series.empty and pd.notna(cross_result_series.iloc[-1]) else False
            else:
                raise ValueError(f"Unknown comparison operator: {op}")
            
        except Exception as e:
            # print(f"DEBUG: Error during comparison for {symbol} on {current_date}: {e}. Left: {left_val}, Right: {right_val}")
            # traceback.print_exc()
            return False

    # --- BinaryExpression: "left AND/OR right"
    if node_type == "BINARYEXPRESSION":
        op = ast_node["operator"].upper()
        
        # Evaluate left child. Take its scalar boolean value.
        left_result_scalar = eval_ast_node(symbol, ast_node["left"], context)
        # Ensure it's a boolean, if it came from a series, it might still be a series of booleans
        if isinstance(left_result_scalar, pd.Series):
            if left_result_scalar.empty: left_result_scalar = False
            else: left_result_scalar = bool(left_result_scalar.iloc[-1]) # Take last boolean for evaluation
        
        # Short-circuit evaluation
        if op == "OR" and left_result_scalar:
            return True
        if op == "AND" and not left_result_scalar:
            return False
            
        # Evaluate right child. Take its scalar boolean value.
        right_result_scalar = eval_ast_node(symbol, ast_node["right"], context)
        if isinstance(right_result_scalar, pd.Series):
            if right_result_scalar.empty: right_result_scalar = False
            else: right_result_scalar = bool(right_result_scalar.iloc[-1]) # Take last boolean for evaluation

        if op == "OR":
            return left_result_scalar or right_result_scalar
        elif op == "AND":
            return left_result_scalar and right_result_scalar
        return False

    # --- IndicatorCall: e.g. "Daily RSI(CLOSE(),14)"
    if node_type == "INDICATORCALL":
        ind_name = str(ast_node["name"])
        indicator_part = ast_node.get("part")
        tf = str(ast_node.get("timeframe", "daily")).lower()
        
        raw_args_list = ast_node.get("arguments", [])
        evaluated_args_values = []
        
        for arg_node in raw_args_list:
            if arg_node.get("type", "").upper() == "INDICATORCALL" and not arg_node.get("arguments"):
                field_name = arg_node.get("name", "").lower()
                if field_name.upper() in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]:
                     evaluated_args_values.append(field_name)
                     continue
            
            evaluated_args_values.append(eval_ast_node(symbol, arg_node, context))

        kwargs_for_call = {}
        param_schema = get_talib_params(ind_name)
        current_eval_arg_idx = 0

        for schema_item in param_schema:
            param_name = schema_item['name']
            if current_eval_arg_idx < len(evaluated_args_values):
                kwargs_for_call[param_name] = evaluated_args_values[current_eval_arg_idx]
                current_eval_arg_idx += 1
            elif 'default' in schema_item and schema_item['default'] is not None:
                kwargs_for_call[param_name] = schema_item['default']
        
        if any(p['name'] == 'field' for p in param_schema) and 'field' not in kwargs_for_call and not ind_name.upper().startswith("STOCH_"):
            kwargs_for_call['field'] = 'close'

        df = load_ohlcv(symbol, tf, end_date=current_date)
        if df is None or df.empty:
            return pd.Series(dtype=float) # Return an empty series if data is missing or insufficient
        
        try:
            indicator_value_series = call_indicator_logic(df, ind_name, indicator_part=indicator_part, **kwargs_for_call)
            # IMPORTANT: eval_ast_node for IndicatorCall *returns the series*, not the last value
            return indicator_value_series
        except Exception as e:
            # print(f"DEBUG: Error calculating indicator {ind_name} for {symbol} ({tf}) on {current_date}: {e}")
            # traceback.print_exc()
            return pd.Series(dtype=float) # Return empty series on error

    # --- Candlestick Pattern ---
    if node_type == "CANDLESTICK":
        pattern_name = str(ast_node["pattern"]).upper()
        tf = "daily" 
        
        df = load_ohlcv(symbol, tf, end_date=current_date)
        if df is None or df.empty:
            return False

        if not hasattr(talib, pattern_name):
            return False
        
        try:
            pattern_func = getattr(talib, pattern_name)
            result_array = pattern_func(df['open'], df['high'], df['low'], df['close'])
            # Candlestick patterns return -100, 0, or 100. We want a boolean for the latest bar.
            is_pattern_present = bool(result_array[-1] != 0)
            return is_pattern_present
        except Exception as e:
            # print(f"DEBUG: Error calculating candlestick pattern {pattern_name} for {symbol} on {current_date}: {e}")
            # traceback.print_exc()
            return False

    # --- Literals ---
    if node_type == "FIELDLITERAL":
        # Returns the string name of the field (e.g., 'close').
        # This will be used by call_indicator_logic (for 'real' param) or converted to series in COMPARISON.
        return ast_node["value"] 

    if node_type == "NUMBERLITERAL":
        return ast_node["value"] # Returns the number itself

    # --- Fallback ---
    # print(f"[eval_ast_node] Unknown AST node type: {node_type} for symbol {symbol}. Node: {ast_node}")
    return False

def evaluate_ast_for_symbol(symbol: str, ast_main: dict) -> bool:
    """Helper to evaluate the main AST for a symbol, catching errors."""
    try:
        # Note: eval_ast_node for the top-level expression returns the final boolean.
        result = bool(eval_ast_node(symbol, ast_main, context={}))
        return result
    except Exception as e:
        # print(f"[EVAL SYMBOL ERROR] Symbol: {symbol}, ErrorType: {type(e).__name__}, Msg: {e}")
        # traceback.print_exc()
        return False

def get_display_timeframe_from_ast(ast_node: dict) -> str:
    """Finds the first timeframe in an AST, defaulting to 'daily'."""
    nodes = get_indicator_nodes_from_ast(ast_node)
    if nodes:
        return nodes[0].get('timeframe', 'daily').lower()
    return 'daily'


# --- Main Screener Execution View (`run_screener`) ---
@csrf_exempt
def run_screener(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        body = json.loads(request.body)
        ast_from_js = body.get("filters")
        
        if not ast_from_js:
            return JsonResponse({"error": "Query is empty or malformed."}, status=400)

        segment = body.get("segment", "Nifty 500")
        
        target_symbols = body.get("target_symbols", None) 
        
        if target_symbols and isinstance(target_symbols, list):
            symbols_to_scan = target_symbols 
        else:
            symbols_to_scan = list_symbols("daily")[:100] 
            
        if not symbols_to_scan:
            return JsonResponse({"error": "No symbols available to scan based on the provided list or defaults."}, status=500)

        indicator_nodes = get_indicator_nodes_from_ast(ast_from_js)
        query_indicators = [reconstruct_indicator_string_from_node(n) for n in indicator_nodes]
        display_timeframe = get_display_timeframe_from_ast(ast_from_js)
        
        results = []

        for symbol in symbols_to_scan:
            # For the regular screener, we pass an empty context, so current_date will be None.
            # This makes load_ohlcv load all available data by default, which is correct for a live screener.
            if evaluate_ast_for_symbol(symbol, ast_from_js):
                
                try:
                    display_context = {} 
                    
                    indicator_values = {}
                    for node in indicator_nodes:
                        key = reconstruct_indicator_string_from_node(node)
                        # For display, we only need the last value (scalar) of the indicator
                        value_series = eval_ast_node(symbol, node, display_context) 
                        
                        # Extract the last value from the series for display
                        if isinstance(value_series, pd.Series) and not value_series.empty:
                            value_scalar = value_series.iloc[-1]
                        elif isinstance(value_series, (float, int, np.number)): # Already a scalar (e.g. from literal)
                            value_scalar = value_series
                        else:
                            value_scalar = np.nan # Or some default string for non-numeric/empty

                        indicator_values[key] = f"{value_scalar:.2f}" if pd.notna(value_scalar) else "N/A"

                    df_key = f"{symbol}_{display_timeframe}"
                    df_display = display_context.get(df_key)
                    
                    if df_display is None:
                        df_display = load_ohlcv(symbol, display_timeframe)

                    if df_display is not None and not df_display.empty:
                        latest = df_display.iloc[-1]
                        prev_close = df_display['close'].iloc[-2] if len(df_display) > 1 else latest['close']
                        pct_change = ((latest['close'] - prev_close) / prev_close * 100) if prev_close != 0 else 0
                        
                        results.append({
                            "symbol": symbol,
                            "timestamp": str(latest.name.date()),
                            "open": f"{latest.get('open', 0):.2f}",
                            "high": f"{latest.get('high', 0):.2f}",
                            "low": f"{latest.get('low', 0):.2f}",
                            "close": f"{latest.get('close', 0):.2f}",
                            "volume": f"{int(latest.get('volume', 0)):,}",
                            "change_pct": f"{pct_change:.2f}",
                            "indicator_values": indicator_values
                        })

                except Exception as e:
                    print(f"Error gathering display data for passing stock {symbol}: {e}")
        
        return JsonResponse({"results": results, "query_indicators": query_indicators})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)
    

def saved_scans_list(request):
    """GET /screener/api/saved_scans/"""
    if request.method != "GET":
        return JsonResponse({"error": "GET method required"}, status=400)
    scans = SavedScan.objects.order_by("-created_at")
    data = [{"id": s.id, "name": s.name, "filters": s.filters_json, "segment": s.segment} for s in scans]
    return JsonResponse({"saved_scans": data})


@csrf_exempt
def save_scan(request):
    """POST /screener/api/save_scan/"""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=400)
    try:
        payload = json.loads(request.body)
        name = payload.get("name", "").strip()
        if not name:
            return JsonResponse({"error": "Missing scan name"}, status=400)
        scan = SavedScan.objects.create(
            name=name,
            filters_json=payload.get("filters"),
            segment=payload.get("segment")
        )
        return JsonResponse({
            "success": True,
            "scan": {"id": scan.id, "name": scan.name, "filters": scan.filters_json, "segment": scan.segment}
        })
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
@csrf_exempt
def run_backtest_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        body = json.loads(request.body)
        ast_filter = body.get("filters")
        if not ast_filter:
            return JsonResponse({"error": "Query (filters) is required for backtest."}, status=400)

        start_date = body.get("start_date", "2023-01-01")
        end_date = body.get("end_date", "2023-12-31")
        initial_capital = float(body.get("initial_capital", 100000))
        stop_loss_pct = float(body.get("stop_loss_pct", 2.0))
        take_profit_pct = float(body.get("take_profit_pct", 5.0))
        position_size_pct = float(body.get("position_size_pct", 10.0))
        
        symbols_to_scan = list_symbols("daily")[:50] 

        results = run_backtest(
            ast_filter=ast_filter,
            symbols_to_scan=symbols_to_scan,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            position_size_pct=position_size_pct
        )
        return JsonResponse(results)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Server error during backtest: {str(e)}"}, status=500)