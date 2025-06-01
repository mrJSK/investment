# # screener/views.py

# from django.shortcuts import render, get_object_or_404, redirect
# from django.views import View
# from django.views.generic import TemplateView
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Scan # For your saved scan models
# # from .forms import ScanForm, ConditionFormSet # For your saved scan CRUD views if you have them
# from .indicator_utils import (
#     SYMBOLS, TA_INDICATOR_LABELS, call_talib_indicator, evaluate_filter_row, evaluate_operation,
#     get_talib_function_list, get_talib_grouped_indicators, get_talib_params, load_ohlcv
# )
# import json
# import pandas as pd
# import traceback # For detailed error logging
# from types import SimpleNamespace # For ajax_scan if you keep it

# # --- Main Dashboard View ---
# class DashboardView(TemplateView):
#     template_name = 'screener/dashboard.html' # Ensure this template exists

# # --- API for Dynamic Screener on Dashboard ---

# def indicator_list(request):
#     print("[VIEWS.PY] Inside indicator_list: Attempting to generate indicator list...")
#     try:
#         talib_functions = get_talib_function_list() 
#         print(f"[VIEWS.PY] indicator_list: Found {len(talib_functions)} TA-Lib functions via get_talib_function_list().")
        
#         indicators_with_params = []
#         if not talib_functions:
#             print("[VIEWS.PY] indicator_list: WARNING - get_talib_function_list() returned empty or None.")

#         for func_name in talib_functions:
#             try:
#                 params_info = get_talib_params(func_name)
                
#                 frontend_param_names = ["timeframe"] 
#                 is_ohlc_based_indicator = True
#                 if any(p_keyword in func_name.upper() for p_keyword in ["VOLUME", "OBV", "AD", "ADOSC"]) or \
#                    func_name.upper().startswith("CDL"):
#                     is_ohlc_based_indicator = False
                
#                 has_explicit_price_input = any(p['name'] in ['real', 'open', 'high', 'low', 'close', 'volume', 'prices', 'inprice'] for p in params_info)

#                 if is_ohlc_based_indicator and not has_explicit_price_input:
#                     frontend_param_names.append("field")

#                 for p_info in params_info:
#                     p_name = p_info['name']
#                     if p_name in ['real', 'open', 'high', 'low', 'close', 'volume', 'prices', 'inprice']:
#                         continue

#                     fe_param_name = p_name 
#                     if p_name == "timeperiod": fe_param_name = "period"
#                     elif p_name == "fastperiod": fe_param_name = "fast_period"
#                     elif p_name == "slowperiod": fe_param_name = "slow_period"
#                     elif p_name == "signalperiod": fe_param_name = "signal_period"
#                     elif p_name == "nbdevup": fe_param_name = "nbdev"
#                     elif p_name == "nbdevdn": continue 
#                     elif p_name == "fastk_period": fe_param_name = "fastk_period"
#                     elif p_name == "slowk_period": fe_param_name = "slowk_period"
#                     elif p_name == "slowd_period": fe_param_name = "slowd_period"
#                     elif "matype" in p_name.lower(): continue 
                    
#                     if fe_param_name not in frontend_param_names:
#                         frontend_param_names.append(fe_param_name)
                
#                 indicators_with_params.append({
#                     "value": func_name, 
#                     "label": f"{TA_INDICATOR_LABELS.get(func_name, func_name)} ({func_name})",
#                     "params": sorted(list(set(frontend_param_names)))
#                 })
#             except Exception as e_inner:
#                 print(f"[VIEWS.PY] indicator_list: Error processing params for indicator '{func_name}': {e_inner}")
#                 indicators_with_params.append({
#                     "value": func_name,
#                     "label": f"{TA_INDICATOR_LABELS.get(func_name, func_name)} ({func_name})",
#                     "params": ["timeframe", "field", "period"] 
#                 })
        
#         print(f"[VIEWS.PY] indicator_list: Successfully processed {len(indicators_with_params)} indicators for API response.")
#         if indicators_with_params:
#             print(f"[VIEWS.PY] indicator_list: Sample of processed indicators: {indicators_with_params[:2]}")
            
#         return JsonResponse({'indicators': indicators_with_params})
#     except Exception as e_outer:
#         print(f"[VIEWS.PY] indicator_list: MAJOR ERROR in API - {e_outer}")
#         traceback.print_exc()
#         return JsonResponse({'error': str(e_outer), 'indicators': []}, status=500)

# def indicator_params(request):
#     fn_name = request.GET.get('fn')
#     if not fn_name:
#         return JsonResponse({'error': 'Missing function name (fn parameter)'}, status=400)
#     try:
#         params = get_talib_params(fn_name)
#         return JsonResponse({'params': params})
#     except AttributeError:
#         return JsonResponse({'error': f"TA-Lib function '{fn_name}' not found."}, status=404)
#     except Exception as e:
#         print(f"[VIEWS] Error in indicator_params for {fn_name}: {e}")
#         traceback.print_exc()
#         return JsonResponse({'error': str(e)}, status=500)


# @csrf_exempt 
# def ajax_scan(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         print("[VIEWS] ajax_scan called. This view might need review/integration with primary scan logic.")
#         return JsonResponse({"results": [{"symbol": "AJAX_PLACEHOLDER", "ltp":"100"}]}) 
#     return JsonResponse({"error": "POST only for ajax_scan"}, status=400)

# def screener_builder(request): 
#     return render(request, 'screener/builder.html') 

# # --- Views for Saved Scans ---
# class ScanListView(View):
#     def get(self, request):
#         scans = Scan.objects.all().order_by('-created_at')
#         return render(request, 'screener/scan_list.html', {'scans': scans})

# class DummyForm:
#     def __init__(self, *args, **kwargs): pass
#     def is_valid(self): return True
#     def save(self): return SimpleNamespace(pk=1) 
#     def __str__(self): return ""
    
# class DummyFormSet:
#     def __init__(self, *args, **kwargs): self.instance = None
#     def is_valid(self): return True
#     def save(self): pass
#     def __str__(self): return ""

# try:
#     from .forms import ScanForm, ConditionFormSet
# except ImportError:
#     print("[VIEWS] Warning: ScanForm or ConditionFormSet not found in forms.py. Using dummies for CRUD views.")
#     ScanForm = DummyForm
#     ConditionFormSet = DummyFormSet


# class ScanCreateView(View):
#     def get(self, request):
#         form = ScanForm()
#         formset = ConditionFormSet()
#         return render(request, 'screener/scan_form.html', {'form': form, 'formset': formset})

#     def post(self, request):
#         form = ScanForm(request.POST)
#         formset = ConditionFormSet(request.POST)
#         if form.is_valid() and formset.is_valid():
#             scan = form.save()
#             formset.instance = scan
#             formset.save()
#             return redirect('scan_list') 
#         return render(request, 'screener/scan_form.html', {'form': form, 'formset': formset})

# class ScanUpdateView(View):
#     def get(self, request, pk):
#         scan = get_object_or_404(Scan, pk=pk)
#         form = ScanForm(instance=scan)
#         formset = ConditionFormSet(instance=scan)
#         return render(request, 'screener/scan_form.html', {'form': form, 'formset': formset, 'scan': scan})

#     def post(self, request, pk):
#         scan = get_object_or_404(Scan, pk=pk)
#         form = ScanForm(request.POST, instance=scan)
#         formset = ConditionFormSet(request.POST, instance=scan)
#         if form.is_valid() and formset.is_valid():
#             form.save()
#             formset.save()
#             return redirect('scan_list')
#         return render(request, 'screener/scan_form.html', {'form': form, 'formset': formset, 'scan': scan})

# class ScanRunView(View): 
#     def get(self, request, pk):
#         scan = get_object_or_404(Scan, pk=pk)
#         backtest_mode = ('backtest' in request.GET)
#         print(f"[VIEWS] Running saved scan '{scan.name}'. Actual run logic needs to be implemented here.")
#         return render(request, 'screener/scan_results.html', {
#             'scan': scan,
#             'results': [{"symbol": "SAVED_SCAN_PLACEHOLDER", "close": "N/A"}], 
#             'backtest': backtest_mode
#         })
    
# def indicator_list_api(request):
#     try:
#         return JsonResponse({'groups': get_talib_grouped_indicators()})
#     except Exception as e:
#         return JsonResponse({'error': str(e), 'groups': {}}, status=500)
    

# # The actual recursive AST evaluator (Conceptual - needs full implementation)
# def eval_ast_node(symbol, ast_node, context=None):
#     context = context if context is not None else {} # Ensure context is a dict
#     node_type = ast_node.get("type")

#     # Ensure ast_node is a dictionary
#     if not isinstance(ast_node, dict):
#         # If it's a fundamental value (like a number or field name string from an argument list)
#         # that has already been processed by the Lark transformer into a Python type, return it.
#         if isinstance(ast_node, (int, float, str)):
#             return ast_node 
#         raise TypeError(f"AST node is not a dictionary: {ast_node} (type: {type(ast_node)})")

#     # print(f"Evaluating node: {node_type} for {symbol} with content {ast_node}")

#     if node_type == "NumberLiteral":
#         return ast_node["value"]
#     if node_type == "FieldLiteral": # e.g. "close" as an argument
#         return ast_node["value"].lower() 

#     if node_type == "IndicatorCall":
#         ind_name = ast_node["name"].upper() # Ensure indicator name is uppercase for TA-Lib
#         tf = ast_node.get("timeframe", "Daily").lower() # Default to Daily if not specified
        
#         # Process arguments: they should already be evaluated if they were literals,
#         # or they could be other indicator calls (not handled in this simplified version)
#         args_values = []
#         raw_args = ast_node.get("arguments", [])
#         # print(f"Raw args for {ind_name}: {raw_args}")
#         for arg_node in raw_args:
#             args_values.append(eval_ast_node(symbol, arg_node, context)) # Recursively evaluate arg nodes
        
#         # print(f"Processed args for {ind_name}: {args_values}")

#         df_key = f"{symbol}_{tf}"
#         if df_key not in context:
#             df = load_ohlcv(symbol, tf)
#             if df is None or df.empty:
#                 raise ValueError(f"Data not found for {symbol} ({tf}) to calculate {ind_name}")
#             context[df_key] = df
#         df = context[df_key]

#         # --- Actual Indicator Calculation ---
#         # This part needs to correctly map `args_values` to TA-Lib function parameters
#         # For SMA(Close, 14): args_values might be ["close", 14]
#         # For MACD(12,26,9): args_values might be [12, 26, 9] (if field 'close' is implicit or handled differently)
        
#         # Simplified example for SMA and RSI, assuming specific argument order
#         # You MUST make this robust for all your indicators and their param orders.
#         try:
#             if ind_name == "SMA" and len(args_values) == 2:
#                 field_name = args_values[0] # Expects "close", "open", etc.
#                 period = int(args_values[1])
#                 # print(f"Calling SMA on {df[field_name].tail()} with period {period}")
#                 return call_talib_indicator(df, ind_name, field_name, period=period)
#             elif ind_name == "RSI" and len(args_values) == 2:
#                 field_name = args_values[0]
#                 period = int(args_values[1])
#                 return call_talib_indicator(df, ind_name, field_name, period=period)
#             elif ind_name == "CLOSE": # Special handling if "CLOSE" is treated as an indicator
#                  return df['close'].iloc[-1]
#             elif ind_name == "VOLUME":
#                  return df['volume'].iloc[-1]
#             # Add more indicator handlers here based on their expected arguments from the AST
#             else:
#                 # Generic attempt for indicators with a single 'period' and implicit 'close' field
#                 if len(args_values) == 1 and isinstance(args_values[0], (int, float)): # e.g. ATR(14)
#                     return call_talib_indicator(df, ind_name, 'close', period=int(args_values[0]))
#                 elif len(args_values) == 2 and isinstance(args_values[0], str) and isinstance(args_values[1], (int, float)):
#                      return call_talib_indicator(df, ind_name, args_values[0], period=int(args_values[1]))

#                 raise NotImplementedError(f"Indicator '{ind_name}' with args {args_values} evaluation not fully implemented.")
#         except KeyError as e:
#             raise ValueError(f"Field error for {ind_name} on {symbol}: {e}. Args were: {args_values}. Available df columns: {df.columns.tolist()}")
#         except Exception as e_ind:
#             raise ValueError(f"Error calculating {ind_name} for {symbol} with args {args_values}: {e_ind}")


#     if node_type == "Comparison":
#         op = ast_node["operator"]
#         # print(f"Left comparison node: {ast_node['left']}")
#         # print(f"Right comparison node: {ast_node['right']}")
#         left_val = eval_ast_node(symbol, ast_node["left"], context)
#         right_val = eval_ast_node(symbol, ast_node["right"], context)
#         # print(f"Comparing for {symbol}: {left_val} {op} {right_val}")
#         return evaluate_operation(left_val, op, right_val)

#     if node_type == "BinaryExpression": # For AND/OR
#         op = ast_node["operator"].upper()
#         left_val = eval_ast_node(symbol, ast_node["left"], context)
#         if op == "AND":
#             if not left_val: return False # Short-circuit
#             return left_val and eval_ast_node(symbol, ast_node["right"], context)
#         elif op == "OR":
#             if left_val: return True # Short-circuit
#             return left_val or eval_ast_node(symbol, ast_node["right"], context)
#         raise ValueError(f"Unknown binary operator: {op}")
    
#     if node_type == "UnaryExpression" and ast_node["operator"].upper() == "NOT": # For NOT
#         operand_val = eval_ast_node(symbol, ast_node["operand"], context)
#         return not operand_val

#     raise ValueError(f"Unknown AST node type: {node_type} in node {ast_node}")


# def evaluate_ast_for_symbol(symbol, ast_main):
#     try:
#         # print(f"Evaluating AST for symbol {symbol}: {ast_main}")
#         return bool(eval_ast_node(symbol, ast_main, context={})) # Pass a new context for each symbol
#     except Exception as e:
#         print(f"[AST EVAL ERROR] Symbol: {symbol}: {e}")
#         # traceback.print_exc() # Uncomment for full traceback during debugging
#         return False

# # --- The main Django view ---
# @csrf_exempt
# def run_screener(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "POST method required"}, status=405)
#     try:
#         body = json.loads(request.body)
        
#         # MODIFIED: Look for "filters" key first, then fallbacks
#         ast = body.get("filters") # This is what builder.js sends
#         query_string = None

#         if not ast: # If "filters" is not present or is None
#             ast = body.get("ast") or body.get("query_ast")
#             if not ast and "type" in body:  
#                 ast = body 
#             query_string = body.get("query_string", "").strip()
        
#         print(f"[VIEWS] run_screener: Received body: {body}")
#         print(f"[VIEWS] run_screener: Initial AST from 'filters': {body.get('filters')}")
#         print(f"[VIEWS] run_screener: Effective AST to be used: {ast}")
#         print(f"[VIEWS] run_screener: Query string if AST was not primary: {query_string}")


#         if not ast and not query_string:
#             return JsonResponse({"error": "Query (AST or string) is empty in request body."}, status=400)
        
#         # If AST was not directly provided via "filters" or "ast", but query_string is, parse it.
#         if not ast and query_string:
#             from .dsl_parser import parse_query # Assuming dsl_parser.py is used and works
#             print(f"[VIEWS] run_screener: Parsing query_string: '{query_string}' with dsl_parser")
#             ast = parse_query(query_string)
#             if ast.get("type") == "PARSE_ERROR": # Check if dsl_parser returns error structure
#                  print(f"[VIEWS] run_screener: dsl_parser failed: {ast.get('details')}")
#                  return JsonResponse({"error": f"Query Parsing Error (dsl_parser): {ast.get('details')}"}, status=400)

#         if not ast or (isinstance(ast, dict) and ast.get("type") in ["PARSE_ERROR", "TRANSFORM_ERROR"]): # Check for error structure from JS parser too
#             error_detail = ast.get("details", "Unknown parsing error") if isinstance(ast, dict) else "Query could not be processed."
#             print(f"[VIEWS] run_screener: Final AST is invalid or parse error: {error_detail}")
#             return JsonResponse({"error": f"Query could not be parsed: {error_detail}"}, status=400)

#         print(f"[VIEWS] run_screener: Using AST for evaluation: {json.dumps(ast, indent=2)}")

#         segment = body.get("segment", "Nifty 500")
#         symbols_to_scan = SYMBOLS # Replace with actual segment-based symbol loading if needed
#         print(f"Scanning {len(symbols_to_scan)} symbols in segment '{segment}'.")

#         results = []
#         # Limit symbols for testing, remove [:X] in production
#         for symbol_to_test in symbols_to_scan[:20]: 
#             try:
#                 if evaluate_ast_for_symbol(symbol_to_test, ast):
#                     df = load_ohlcv(symbol_to_test, "daily") # Load daily data for display
#                     if df is not None and not df.empty:
#                         latest = df.iloc[-1]
#                         prev_close = df['close'].iloc[-2] if len(df) > 1 else latest['close']
#                         pct_change = ((latest['close'] - prev_close) / prev_close * 100) if prev_close and prev_close != 0 else 0.0
                        
#                         timestamp_val = latest.get('timestamp', latest.name if isinstance(latest.name, (str, pd.Timestamp)) else '')
#                         timestamp_str = str(timestamp_val).split(" ")[0] if pd.notna(timestamp_val) else "N/A"

#                         results.append({
#                             "symbol": symbol_to_test,
#                             "timestamp": timestamp_str,
#                             "open": f"{latest.get('open', 0):.2f}",
#                             "high": f"{latest.get('high', 0):.2f}",
#                             "low": f"{latest.get('low', 0):.2f}",
#                             "close": f"{latest.get('close', 0):.2f}",
#                             "volume": f"{int(latest.get('volume', 0)):,}",
#                             "change_pct": f"{pct_change:.2f}%"
#                         })
#             except Exception as e_eval_sym:
#                 print(f"[EVAL SYMBOL ERROR] {symbol_to_test}: {e_eval_sym}")
#                 # traceback.print_exc() # Uncomment for full traceback
        
#         print(f"[VIEWS] run_screener: Scan complete. Found {len(results)} matches.")
#         return JsonResponse({"results": results})

#     except json.JSONDecodeError:
#         print("[VIEWS] run_screener: Invalid JSON payload.")
#         return JsonResponse({"error": "Invalid JSON payload"}, status=400)
#     except Exception as e_global:
#         print(f"[VIEWS] Global error in run_screener: {e_global}")
#         traceback.print_exc()
#         return JsonResponse({"error": f"Server error: {str(e_global)}"}, status=500)


from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Scan 
from .indicator_utils import (
    SYMBOLS, TA_INDICATOR_LABELS, call_talib_indicator, evaluate_operation,
    get_talib_function_list, get_talib_grouped_indicators, get_talib_params, list_symbols, load_ohlcv
)
import json
import pandas as pd
import traceback 
from types import SimpleNamespace
import numpy as np # For NaN checks

# --- Main Dashboard View ---
class DashboardView(TemplateView):
    template_name = 'screener/dashboard.html'

# --- API for Dynamic Screener on Dashboard ---
# indicator_list, indicator_params, ajax_scan, screener_builder, Scan CRUD views remain largely the same
# Ensure they are using the updated indicator_utils for consistency if needed.

def indicator_list_api(request): # Renamed from indicator_list to avoid conflict if you had both
    print("[VIEWS.PY] Inside indicator_list_api: Attempting to generate indicator list...")
    try:
        grouped_indicators = get_talib_grouped_indicators() # From indicator_utils.py
        print(f"[VIEWS.PY] indicator_list_api: Successfully fetched grouped indicators.")
        return JsonResponse({'groups': grouped_indicators})
    except Exception as e_outer:
        print(f"[VIEWS.PY] indicator_list_api: MAJOR ERROR in API - {e_outer}")
        traceback.print_exc()
        return JsonResponse({'error': str(e_outer), 'groups': {}}, status=500)

def indicator_params(request):
    fn_name = request.GET.get('fn')
    if not fn_name:
        return JsonResponse({'error': 'Missing function name (fn parameter)'}, status=400)
    try:
        params = get_talib_params(fn_name)
        return JsonResponse({'params': params})
    except AttributeError:
        return JsonResponse({'error': f"TA-Lib function '{fn_name}' not found."}, status=404)
    except Exception as e:
        print(f"[VIEWS] Error in indicator_params for {fn_name}: {e}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

# ... (other views like ScanListView, ScanCreateView, etc. - assumed to be okay for now) ...
class ScanListView(View):
    def get(self, request):
        scans = Scan.objects.all().order_by('-created_at')
        return render(request, 'screener/scan_list.html', {'scans': scans})

# --- AST Evaluator ---
def eval_ast_node(symbol, ast_node, context=None):
    context = context if context is not None else {} 
    node_type = ast_node.get("type")

    if not isinstance(ast_node, dict):
        if isinstance(ast_node, (int, float, str)): return ast_node 
        raise TypeError(f"AST node is not a dictionary: {ast_node} (type: {type(ast_node)}) for symbol {symbol}")

    # print(f"--- [eval_ast_node] Symbol: {symbol}, Type: {node_type}, Node: {ast_node} ---")

    if node_type == "NumberLiteral":
        return ast_node["value"]
    if node_type == "FieldLiteral": 
        return ast_node["value"].lower() 

    if node_type == "IndicatorCall":
        ind_name = ast_node["name"] # JS parser stores original case, TA-Lib needs UPPER
        tf = ast_node.get("timeframe", "Daily").lower()
        
        args_values = []
        raw_args = ast_node.get("arguments", [])
        for arg_node in raw_args:
            args_values.append(eval_ast_node(symbol, arg_node, context)) 
        
        # print(f"[eval_ast_node] IndicatorCall for {ind_name} on {tf} with processed args: {args_values}")

        df_key = f"{symbol}_{tf}"
        if df_key not in context:
            df = load_ohlcv(symbol, tf) # load_ohlcv now handles lowercase columns
            if df is None or df.empty:
                # print(f"[eval_ast_node] Data not found or empty for {df_key}")
                raise ValueError(f"Data not found/empty for {symbol} ({tf}) for {ind_name}")
            context[df_key] = df
        df = context[df_key]

        try:
            # Prepare kwargs for call_talib_indicator based on common param names
            # This needs to be robust. The JS parser AST gives generic "arguments".
            # We need to map them to TA-Lib's expected parameter names.
            # Example: SMA(CLOSE, 14) -> AST args: [{"type":"FieldLiteral", "value":"CLOSE"}, {"type":"NumberLiteral", "value":14}]
            # call_talib_indicator expects `field_name` and `period`.
            
            # Basic mapping for common indicators:
            indicator_kwargs = {}
            if ind_name.upper() in ["SMA", "EMA", "RSI", "ATR", "ADX", "CCI", "MOM", "ROC", "STDDEV", "WMA", "DEMA", "TEMA", "KAMA", "TRIMA", "T3"]: # Common single period + field indicators
                if len(args_values) == 2 and isinstance(args_values[0], str) and isinstance(args_values[1], (int, float)):
                    # field_name = args_values[0] # Already evaluated to string "close"
                    # period = args_values[1]     # Already evaluated to number 14
                    return call_talib_indicator(df, ind_name, field_name=args_values[0], period=args_values[1])
                else:
                    raise ValueError(f"Incorrect arguments for {ind_name}: expected field string and period number, got {args_values}")
            
            elif ind_name.upper() == "MACD": # MACD(fast, slow, signal) - field is implicit 'close'
                if len(args_values) == 3: # Assuming field 'close' is implicit or handled by call_talib_indicator default
                    return call_talib_indicator(df, ind_name, field_name='close', 
                                                fastperiod=args_values[0], slowperiod=args_values[1], signalperiod=args_values[2])
                else: # MACD(field, fast, slow, signal)
                     if len(args_values) == 4 and isinstance(args_values[0], str):
                         return call_talib_indicator(df, ind_name, field_name=args_values[0],
                                                     fastperiod=args_values[1], slowperiod=args_values[2], signalperiod=args_values[3])
                     else:
                        raise ValueError(f"Incorrect arguments for MACD: {args_values}")

            elif ind_name.upper() == "BBANDS": # BBANDS(field, period, nbdevup, nbdevdn, matype)
                 if len(args_values) >= 2: # field, period are mandatory
                     field_val = args_values[0]
                     period_val = args_values[1]
                     bb_kwargs = {'nbdevup': args_values[2] if len(args_values) > 2 else 2,
                                  'nbdevdn': args_values[3] if len(args_values) > 3 else 2,
                                  'matype': args_values[4] if len(args_values) > 4 else 0} # MAType 0 is SMA
                     return call_talib_indicator(df, ind_name, field_name=field_val, period=period_val, **bb_kwargs)
                 else:
                     raise ValueError(f"Incorrect arguments for BBANDS: {args_values}")


            elif ind_name.upper() == "STOCH": # STOCH(field, fastk, slowk, slowd, slowk_matype, slowd_matype)
                if len(args_values) >= 1: # Field is often implicit 'high,low,close'
                    stoch_kwargs = {
                        'fastk_period': args_values[0] if isinstance(args_values[0], (int, float)) else 5, # Assuming first numeric is fastk if no field
                        'slowk_period': args_values[1] if len(args_values) > 1 and isinstance(args_values[1],(int,float)) else 3,
                        'slowd_period': args_values[2] if len(args_values) > 2 and isinstance(args_values[2],(int,float)) else 3,
                    }
                    # STOCH in TA-Lib takes high, low, close directly, not a single field_name string.
                    # call_talib_indicator needs to be adapted or this logic needs to pass df columns.
                    # For now, this will likely fail in call_talib_indicator unless it's adapted.
                    # A better call_talib_indicator would check fn signature.
                    print(f"WARN: STOCH evaluation may need specific handling in call_talib_indicator for HLC inputs.")
                    return call_talib_indicator(df, ind_name, field_name='close', **stoch_kwargs) # Placeholder field
                else:
                    raise ValueError(f"Incorrect arguments for STOCH: {args_values}")


            # Special handling for simple price fields if they come as "IndicatorCall"
            elif ind_name.upper() in ["CLOSE", "OPEN", "HIGH", "LOW", "VOLUME"]:
                field_to_get = ind_name.lower()
                if field_to_get not in df.columns:
                    raise KeyError(f"Field '{field_to_get}' not in DataFrame for {symbol} on {tf}")
                return df[field_to_get].iloc[-1]
            
            else: # Generic attempt for other indicators
                if len(args_values) == 1 and isinstance(args_values[0], (int, float)): # e.g. ATR(14) -> field 'close' implicit
                    return call_talib_indicator(df, ind_name, 'close', period=args_values[0])
                elif len(args_values) == 2 and isinstance(args_values[0], str) and isinstance(args_values[1], (int, float)): # e.g. SMA(OPEN, 10)
                     return call_talib_indicator(df, ind_name, args_values[0], period=args_values[1])
                
                raise NotImplementedError(f"Indicator '{ind_name}' with args {args_values} evaluation logic not fully defined.")
        
        except KeyError as e: # Catch if a field like 'close' is not in df.columns
            print(f"[eval_ast_node] KeyError for {ind_name} on {symbol}: {e}. Args: {args_values}. DF Columns: {df.columns.tolist()}")
            raise ValueError(f"Field error for {ind_name}: {e}")
        except Exception as e_ind_call:
            print(f"[eval_ast_node] Error calculating {ind_name} for {symbol} with args {args_values}: {e_ind_call}")
            # traceback.print_exc()
            raise ValueError(f"Calculation error for {ind_name}: {e_ind_call}")

    if node_type == "Comparison":
        op = ast_node["operator"]
        left_val = eval_ast_node(symbol, ast_node["left"], context)
        right_val = eval_ast_node(symbol, ast_node["right"], context)
        # print(f"[eval_ast_node] Comparing for {symbol}: {left_val} {op} {right_val} (Types: {type(left_val)}, {type(right_val)})")
        return evaluate_operation(left_val, op, right_val)

    if node_type == "BinaryExpression": 
        op = ast_node["operator"].upper()
        left_val = eval_ast_node(symbol, ast_node["left"], context)
        if op == "AND":
            if not left_val: return False 
            return left_val and eval_ast_node(symbol, ast_node["right"], context)
        elif op == "OR":
            if left_val: return True 
            return left_val or eval_ast_node(symbol, ast_node["right"], context)
        raise ValueError(f"Unknown binary operator: {op}")
    
    if node_type == "UnaryExpression" and ast_node["operator"].upper() == "NOT": 
        operand_val = eval_ast_node(symbol, ast_node["operand"], context)
        return not operand_val

    raise ValueError(f"Unknown AST node type: {node_type} in node {ast_node} for symbol {symbol}")


def evaluate_ast_for_symbol(symbol, ast_main):
    try:
        result = bool(eval_ast_node(symbol, ast_main, context={}))
        # print(f"[evaluate_ast_for_symbol] Symbol: {symbol}, Result: {result}")
        return result
    except Exception as e:
        print(f"[EVAL SYMBOL ERROR] Symbol: {symbol}, Error: {e}")
        # traceback.print_exc() 
        return False

# --- The main Django view ---
@csrf_exempt
def run_screener(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        body = json.loads(request.body)
        ast = body.get("filters") 
        query_string = None # Not expecting query_string if AST is sent

        # print(f"[run_screener] Received body: {json.dumps(body, indent=2)}")

        if not ast: 
            # Fallback if 'filters' is not the key, or if frontend might send it differently
            ast = body.get("ast") or body.get("query_ast")
            if not ast and "type" in body: ast = body 
            query_string = body.get("query_string", "").strip()
            # print(f"[run_screener] AST not found in 'filters', trying fallbacks. query_string: '{query_string}'")
        
        if not ast and not query_string:
            print("[run_screener] ERROR: Query (AST or string) is empty in request body.")
            return JsonResponse({"error": "Query (AST or string) is empty in request body."}, status=400)
        
        if not ast and query_string: # If only query_string was provided (e.g. from a different client)
            from .dsl_parser import parse_query # Assuming dsl_parser.py is your Lark parser
            print(f"[run_screener] Parsing query_string via dsl_parser: '{query_string}'")
            ast = parse_query(query_string) # This should return your Python AST structure
            if isinstance(ast, dict) and ast.get("type") == "PARSE_ERROR": 
                 print(f"[run_screener] dsl_parser failed: {ast.get('details')}")
                 return JsonResponse({"error": f"Query Parsing Error (Python Parser): {ast.get('details', 'Unknown syntax error')}"}, status=400)
        
        if not ast or (isinstance(ast, dict) and ast.get("type") in ["PARSE_ERROR", "TRANSFORM_ERROR"]):
            error_detail = ast.get("details", "Unknown parsing error") if isinstance(ast, dict) else "Query could not be processed into valid AST."
            print(f"[run_screener] ERROR: Final AST is invalid or a parse error object: {error_detail}")
            return JsonResponse({"error": f"Query could not be parsed: {error_detail}"}, status=400)

        # print(f"[run_screener] Using AST for evaluation: {json.dumps(ast, indent=2)}")

        segment = body.get("segment", "Nifty 500") # Default segment
        # symbols_to_scan = SYMBOLS # Use symbols loaded by indicator_utils
        # For testing, explicitly list some symbols you know have data
        symbols_to_scan = list_symbols("daily") # Get symbols from the 'daily' data folder
        if not symbols_to_scan:
            print("[run_screener] WARNING: No symbols found by list_symbols('daily'). Check DATA_DIR and file structure.")
            return JsonResponse({"error": "No symbols available for scanning. Check server data configuration."}, status=500)

        print(f"[run_screener] Scanning up to {len(symbols_to_scan)} symbols in segment '{segment}'. Sample: {symbols_to_scan[:5]}")


        results = []
        # Limit symbols for testing, remove [:X] in production
        for symbol_to_test in symbols_to_scan[:50]: # Increased limit for better testing
            # print(f"\n[run_screener] Processing symbol: {symbol_to_test}")
            try:
                if evaluate_ast_for_symbol(symbol_to_test, ast):
                    # print(f"[run_screener] MATCH for symbol: {symbol_to_test}")
                    df_display = load_ohlcv(symbol_to_test, "daily") 
                    if df_display is not None and not df_display.empty:
                        latest = df_display.iloc[-1]
                        prev_close = df_display['close'].iloc[-2] if len(df_display) > 1 else latest['close']
                        
                        # Ensure values are not NaN before formatting
                        open_p = latest.get('open', np.nan)
                        high_p = latest.get('high', np.nan)
                        low_p = latest.get('low', np.nan)
                        close_p = latest.get('close', np.nan)
                        volume_v = latest.get('volume', np.nan)
                        
                        pct_change = ((close_p - prev_close) / prev_close * 100) if pd.notna(close_p) and pd.notna(prev_close) and prev_close != 0 else 0.0
                        
                        timestamp_val = latest.name # Assuming index is timestamp/date
                        timestamp_str = str(timestamp_val).split(" ")[0] if pd.notna(timestamp_val) else "N/A"

                        results.append({
                            "symbol": symbol_to_test,
                            "timestamp": timestamp_str,
                            "open": f"{open_p:.2f}" if pd.notna(open_p) else "N/A",
                            "high": f"{high_p:.2f}" if pd.notna(high_p) else "N/A",
                            "low": f"{low_p:.2f}" if pd.notna(low_p) else "N/A",
                            "close": f"{close_p:.2f}" if pd.notna(close_p) else "N/A",
                            "volume": f"{int(volume_v):,}" if pd.notna(volume_v) else "N/A",
                            "change_pct": f"{pct_change:.2f}%"
                        })
                    else:
                        print(f"[run_screener] No display data loaded for matched symbol {symbol_to_test}")
            except Exception as e_eval_sym_loop:
                print(f"[EVAL SYMBOL ERROR in run_screener loop] {symbol_to_test}: {e_eval_sym_loop}")
                # traceback.print_exc() 
        
        print(f"[run_screener] Scan complete. Found {len(results)} matches.")
        return JsonResponse({"results": results})

    except json.JSONDecodeError:
        print("[run_screener] ERROR: Invalid JSON payload.")
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e_global:
        print(f"[run_screener] GLOBAL ERROR: {e_global}")
        traceback.print_exc()
        return JsonResponse({"error": f"Server error: {str(e_global)}"}, status=500)