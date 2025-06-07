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


# --- Helper functions for AST processing ---

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
    
    # Handle different argument structures
    args_list = node.get('arguments', node.get('params', []))
    args = ", ".join([reconstruct_arg_string(arg) for arg in args_list])

    part = f".{node['part']}" if node.get('part') else ""
    return f"{timeframe} {name}({args}){part}"

def get_indicator_nodes_from_ast(ast_node):
    """Recursively traverses the AST to find all unique IndicatorCall nodes."""
    nodes = []
    
    if not isinstance(ast_node, dict):
        return nodes

    # Check if the current node is an indicator call
    if ast_node.get("type") == "IndicatorCall":
        nodes.append(ast_node)

    # Recursively check other parts of the AST
    for key, value in ast_node.items():
        if isinstance(value, dict):
            nodes.extend(get_indicator_nodes_from_ast(value))
        elif isinstance(value, list):
            for item in value:
                nodes.extend(get_indicator_nodes_from_ast(item))
    
    # Return unique nodes based on their string representation
    unique_nodes = {reconstruct_indicator_string_from_node(n): n for n in nodes}
    return list(unique_nodes.values())


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

    node_type = ast_node.get("type", "").upper()

    # --- Comparison: "left operator right", e.g. (RSI > 40) or (SMA14 < EMA20)
    if node_type == "COMPARISON":
        left_val  = eval_ast_node(symbol, ast_node["left"], context)
        right_val = eval_ast_node(symbol, ast_node["right"], context)

        if left_val is False or right_val is False or left_val is None or right_val is None or pd.isna(left_val) or pd.isna(right_val):
            return False

        op = ast_node["operator"]
        try:
            if op == ">": return left_val > right_val
            if op == "<": return left_val < right_val
            if op == ">=": return left_val >= right_val
            if op == "<=": return left_val <= right_val
            if op == "==": return left_val == right_val
            if op == "!=": return left_val != right_val
            # CROSSES operators need special handling for series
            if op.upper() == "CROSSES ABOVE":
                return (left_val.shift(1) < right_val.shift(1)) & (left_val > right_val)
            if op.upper() == "CROSSES BELOW":
                return (left_val.shift(1) > right_val.shift(1)) & (left_val < right_val)
            raise ValueError(f"Unknown comparison operator: {op}")
        except Exception:
            return False

    # --- BinaryExpression: "left AND/OR right"
    if node_type == "BINARYEXPRESSION":
        op = ast_node["operator"].upper()
        left_val = eval_ast_node(symbol, ast_node["left"], context)
        
        if op == "OR":
            return left_val or eval_ast_node(symbol, ast_node["right"], context)
        elif op == "AND":
            return left_val and eval_ast_node(symbol, ast_node["right"], context)
        return False

    # --- IndicatorCall: e.g. "15min RSI(CLOSE,14)"
    if node_type == "INDICATORCALL":
        ind_name = str(ast_node["name"])
        indicator_part = ast_node.get("part")
        tf = str(ast_node.get("timeframe", "daily")).lower()

        raw_args_list = ast_node.get("arguments", [])
        evaluated_args_values = [eval_ast_node(symbol, arg, context) for arg in raw_args_list]
        
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

        df_key = f"{symbol}_{tf}"
        if df_key not in context:
            df = load_ohlcv(symbol, tf)
            if df is None or df.empty:
                raise ValueError(f"Data not found for {symbol} ({tf})")
            context[df_key] = df
        df = context[df_key]
        
        return call_indicator_logic(df, ind_name, indicator_part=indicator_part, **kwargs_for_call)

    if node_type == "FIELDLITERAL":
        return ast_node["value"] # Already a string like 'close'

    if node_type == "NUMBERLITERAL":
        return ast_node["value"]

    print(f"[eval_ast_node] Unknown AST node type: {node_type}")
    return False

def evaluate_ast_for_symbol(symbol: str, ast_main: dict) -> bool:
    """Helper to evaluate the main AST for a symbol, catching errors."""
    try:
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


# --- Main Screener Execution View ---
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
        # Note: Limiting symbols for performance. You can adjust this.
        symbols_to_scan = list_symbols("daily")[:100] 
        if not symbols_to_scan:
            return JsonResponse({"error": "No symbols available to scan."}, status=500)

        indicator_nodes = get_indicator_nodes_from_ast(ast_from_js)
        query_indicators = [reconstruct_indicator_string_from_node(n) for n in indicator_nodes]
        display_timeframe = get_display_timeframe_from_ast(ast_from_js)
        
        results = []

        for symbol in symbols_to_scan:
            # Step 1: Check if the symbol passes the main filter condition
            if evaluate_ast_for_symbol(symbol, ast_from_js):
                
                # Step 2: If it passes, gather all display data for this one symbol
                try:
                    # Use a single context to cache DataFrames for this symbol
                    context = {}
                    
                    # Calculate values for all display indicators
                    indicator_values = {}
                    for node in indicator_nodes:
                        key = reconstruct_indicator_string_from_node(node)
                        # eval_ast_node will populate the context dictionary
                        value = eval_ast_node(symbol, node, context)
                        indicator_values[key] = f"{value:.2f}" if isinstance(value, (float, np.number)) else str(value)

                    # Get the main DataFrame for this symbol's display data
                    df_key = f"{symbol}_{display_timeframe}"
                    df_display = context.get(df_key)
                    
                    # If the display DF wasn't loaded during indicator calculation, load it now
                    if df_display is None:
                        df_display = load_ohlcv(symbol, display_timeframe)

                    # Step 3: If we have the data, construct and append the single result row
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
                    # Log if gathering data for a passing stock fails, but don't crash
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