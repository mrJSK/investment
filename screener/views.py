from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Scan # For your saved scan models
# from .forms import ScanForm, ConditionFormSet # For your saved scan CRUD views if you have them
from .indicator_utils import (
    SYMBOLS, TA_INDICATOR_LABELS, evaluate_filter_row,
    get_talib_function_list, get_talib_grouped_indicators, get_talib_params, load_ohlcv
)
import json
import pandas as pd
import traceback # For detailed error logging
from types import SimpleNamespace # For ajax_scan if you keep it

# --- Main Dashboard View ---
class DashboardView(TemplateView):
    template_name = 'screener/dashboard.html'

# --- API for Dynamic Screener on Dashboard ---

def indicator_list(request): # This function name must match what's in urls.py
    print("[VIEWS.PY] Inside indicator_list: Attempting to generate indicator list...")
    try:
        talib_functions = get_talib_function_list() # From indicator_utils.py
        print(f"[VIEWS.PY] indicator_list: Found {len(talib_functions)} TA-Lib functions via get_talib_function_list().")
        # If len is 0 or very small, there's an issue with get_talib_function_list() or TA-Lib setup.

        indicators_with_params = []
        if not talib_functions:
            print("[VIEWS.PY] indicator_list: WARNING - get_talib_function_list() returned empty or None.")

        for func_name in talib_functions:
            try:
                params_info = get_talib_params(func_name) # From indicator_utils.py
                
                frontend_param_names = ["timeframe"] 
                is_ohlc_based_indicator = True
                if any(p_keyword in func_name.upper() for p_keyword in ["VOLUME", "OBV", "AD", "ADOSC"]) or \
                   func_name.upper().startswith("CDL"):
                    is_ohlc_based_indicator = False
                
                has_explicit_price_input = any(p['name'] in ['real', 'open', 'high', 'low', 'close', 'volume', 'prices', 'inprice'] for p in params_info)

                if is_ohlc_based_indicator and not has_explicit_price_input:
                    frontend_param_names.append("field")

                for p_info in params_info:
                    p_name = p_info['name']
                    if p_name in ['real', 'open', 'high', 'low', 'close', 'volume', 'prices', 'inprice']:
                        continue

                    fe_param_name = p_name 
                    if p_name == "timeperiod": fe_param_name = "period"
                    elif p_name == "fastperiod": fe_param_name = "fast_period"
                    elif p_name == "slowperiod": fe_param_name = "slow_period"
                    elif p_name == "signalperiod": fe_param_name = "signal_period"
                    elif p_name == "nbdevup": fe_param_name = "nbdev"
                    elif p_name == "nbdevdn": continue 
                    elif p_name == "fastk_period": fe_param_name = "fastk_period"
                    elif p_name == "slowk_period": fe_param_name = "slowk_period"
                    elif p_name == "slowd_period": fe_param_name = "slowd_period"
                    elif "matype" in p_name.lower(): continue 
                    
                    if fe_param_name not in frontend_param_names:
                        frontend_param_names.append(fe_param_name)
                
                indicators_with_params.append({
                    "value": func_name, 
                    "label": f"{TA_INDICATOR_LABELS.get(func_name, func_name)} ({func_name})",
                    "params": sorted(list(set(frontend_param_names)))
                })
            except Exception as e_inner:
                print(f"[VIEWS.PY] indicator_list: Error processing params for indicator '{func_name}': {e_inner}")
                # Fallback for this specific indicator if param fetching fails
                indicators_with_params.append({
                    "value": func_name,
                    "label": f"{TA_INDICATOR_LABELS.get(func_name, func_name)} ({func_name})",
                    "params": ["timeframe", "field", "period"] # Generic fallback
                })
        
        print(f"[VIEWS.PY] indicator_list: Successfully processed {len(indicators_with_params)} indicators for API response.")
        if indicators_with_params:
            print(f"[VIEWS.PY] indicator_list: Sample of processed indicators: {indicators_with_params[:2]}") # Print first 2
            
        return JsonResponse({'indicators': indicators_with_params})
    except Exception as e_outer:
        print(f"[VIEWS.PY] indicator_list: MAJOR ERROR in API - {e_outer}")
        traceback.print_exc()
        return JsonResponse({'error': str(e_outer), 'indicators': []}, status=500)

def indicator_params(request): # Mapped to /api/indicator_params/
    """
    Provides detailed parameters for a specific TA-Lib function.
    Useful if frontend wants to dynamically build very specific input forms.
    """
    fn_name = request.GET.get('fn')
    if not fn_name:
        return JsonResponse({'error': 'Missing function name (fn parameter)'}, status=400)
    try:
        params = get_talib_params(fn_name) # from your indicator_utils.py
        return JsonResponse({'params': params})
    except AttributeError:
        return JsonResponse({'error': f"TA-Lib function '{fn_name}' not found."}, status=404)
    except Exception as e:
        print(f"[VIEWS] Error in indicator_params for {fn_name}: {e}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt # Ensure CSRF token is handled by JS if POSTing from JS without Django forms
def run_screener(request): # This is mapped to /api/run_screener/
    """
    Main API endpoint for executing dynamic scans from the dashboard.
    Receives filter conditions from builder.js, processes them using indicator_utils,
    and returns detailed results for matched stocks.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    try:
        body = json.loads(request.body)
        filters_from_frontend = body.get("filters", [])
        segment = body.get("segment", "Nifty 500") 

        # SYMBOLS should be loaded from indicator_utils.py, representing all available symbols
        # You might filter SYMBOLS based on the 'segment' variable here
        symbols_to_scan = SYMBOLS 
        # Example segment filtering (you'd need to implement functions like load_nifty50_symbols())
        # if segment == "Nifty 50": symbols_to_scan = load_nifty50_symbols() 
        # elif segment == "Nifty 100": symbols_to_scan = load_nifty100_symbols()

        print(f"[VIEWS] run_screener: Segment '{segment}', {len(symbols_to_scan)} symbols, {len(filters_from_frontend)} filters.")

        detailed_matches = []
        for symbol in symbols_to_scan:
            try:
                all_conditions_met_for_symbol = True
                if not filters_from_frontend: # Behavior for no filters: match none or all?
                    all_conditions_met_for_symbol = False 
                
                for f_data in filters_from_frontend:
                    # f_data is the transformed filter from builder.js, expected by evaluate_filter_row
                    # It should contain 'indicator', 'timeframe', 'field', 'period', 'mainOp', etc.
                    current_filter_timeframe = f_data.get('timeframe', 'Daily') # Default if not in filter data
                    
                    df = load_ohlcv(symbol, current_filter_timeframe)
                    if df is None or df.empty:
                        all_conditions_met_for_symbol = False
                        break 
                    
                    if not evaluate_filter_row(df.copy(), f_data):
                        all_conditions_met_for_symbol = False
                        break
                
                if all_conditions_met_for_symbol:
                    # Matched: Fetch latest daily data for OHLCV, Timestamp, %Change
                    df_display = load_ohlcv(symbol, 'Daily') # Use daily for consistent display data
                    if df_display is not None and not df_display.empty:
                        latest_row = df_display.iloc[-1]
                        prev_close = df_display['close'].iloc[-2] if len(df_display) > 1 else latest_row['close']
                        
                        timestamp_val = latest_row.get('timestamp', '')
                        if isinstance(timestamp_val, (pd.Timestamp, pd.Series)): # Handle if it's Series from single row df
                            timestamp_val = timestamp_val.iloc[0] if isinstance(timestamp_val, pd.Series) else timestamp_val
                            timestamp_str = pd.to_datetime(timestamp_val).strftime('%Y-%m-%d') # Date only
                        elif isinstance(timestamp_val, str):
                             timestamp_str = timestamp_val.split(" ")[0] # Assuming "YYYY-MM-DD HH:MM:SS" format
                        else:
                            timestamp_str = str(timestamp_val) if pd.notna(timestamp_val) else "N/A"

                        open_p = latest_row.get('open', 0)
                        high_p = latest_row.get('high', 0)
                        low_p = latest_row.get('low', 0)
                        close_p = latest_row.get('close', 0)
                        volume_v = latest_row.get('volume', 0)
                        
                        pct_change = ((close_p - prev_close) / prev_close * 100) if prev_close and prev_close != 0 else 0.0
                        
                        detailed_matches.append({
                            "symbol": symbol,
                            "timestamp": timestamp_str,
                            "open": f"{open_p:.2f}" if pd.notna(open_p) else "N/A",
                            "high": f"{high_p:.2f}" if pd.notna(high_p) else "N/A",
                            "low": f"{low_p:.2f}" if pd.notna(low_p) else "N/A",
                            "close": f"{close_p:.2f}" if pd.notna(close_p) else "N/A",
                            "volume": f"{volume_v:.0f}" if pd.notna(volume_v) else "N/A",
                            "change_pct": f"{pct_change:.2f}%"
                        })
                    else: # Fallback if display data can't be loaded
                        detailed_matches.append({"symbol": symbol, "timestamp": "N/A", "open": "N/A", 
                                                 "high": "N/A", "low": "N/A", "close": "N/A", 
                                                 "change_pct": "N/A", "volume": "N/A"})
            except Exception as e_symbol:
                print(f"[VIEWS] Error processing symbol {symbol} in run_screener: {e_symbol}")
                # traceback.print_exc() # Uncomment for full debug trace for this symbol
                continue # Move to next symbol
        
        print(f"[VIEWS] run_screener: Scan complete. Found {len(detailed_matches)} detailed matches.")
        return JsonResponse({"results": detailed_matches})
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload received by server."}, status=400)
    except Exception as e_global:
        print(f"[VIEWS] Global error in run_screener: {e_global}")
        traceback.print_exc()
        return JsonResponse({"error": f"Server error: {str(e_global)}"}, status=500)

# --- Other Views (from your file, kept for completeness) ---

@csrf_exempt # This was your original ajax_scan, ensure it's needed or remove if run_screener handles all.
def ajax_scan(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # ... (your existing logic for ajax_scan) ...
        # This view seems to use a different way of constructing 'scan' and 'conditions'
        # and calls a 'utils.run_scan' which is not defined in the provided indicator_utils.py
        # For clarity, the dashboard should primarily use the 'run_screener' view above.
        print("[VIEWS] ajax_scan called. This view might need review/integration with primary scan logic.")
        return JsonResponse({"results": [{"symbol": "AJAX_PLACEHOLDER", "ltp":"100"}]}) # Placeholder
    return JsonResponse({"error": "POST only for ajax_scan"}, status=400)

def screener_builder(request): # For your separate builder page if any
    return render(request, 'screener/builder.html') # Ensure this template exists

# --- Views for Saved Scans (from your file) ---
# These views interact with your Scan and Condition Django models.
# They are for managing scans saved to the database.

class ScanListView(View):
    def get(self, request):
        scans = Scan.objects.all().order_by('-created_at')
        return render(request, 'screener/scan_list.html', {'scans': scans})

# Placeholder for forms if not defined yet
class DummyForm:
    def __init__(self, *args, **kwargs): pass
    def is_valid(self): return True
    def save(self): return SimpleNamespace(pk=1) # Mock saved object
    def __str__(self): return ""
    
class DummyFormSet:
    def __init__(self, *args, **kwargs): self.instance = None
    def is_valid(self): return True
    def save(self): pass
    def __str__(self): return ""

try:
    from .forms import ScanForm, ConditionFormSet
except ImportError:
    print("[VIEWS] Warning: ScanForm or ConditionFormSet not found in forms.py. Using dummies for CRUD views.")
    ScanForm = DummyForm
    ConditionFormSet = DummyFormSet


class ScanCreateView(View):
    def get(self, request):
        form = ScanForm()
        formset = ConditionFormSet()
        return render(request, 'screener/scan_form.html', {'form': form, 'formset': formset})

    def post(self, request):
        form = ScanForm(request.POST)
        formset = ConditionFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            scan = form.save()
            formset.instance = scan
            formset.save()
            return redirect('scan_list') # Assuming 'scan_list' is a named URL for ScanListView
        return render(request, 'screener/scan_form.html', {'form': form, 'formset': formset})

class ScanUpdateView(View):
    def get(self, request, pk):
        scan = get_object_or_404(Scan, pk=pk)
        form = ScanForm(instance=scan)
        formset = ConditionFormSet(instance=scan)
        return render(request, 'screener/scan_form.html', {'form': form, 'formset': formset, 'scan': scan})

    def post(self, request, pk):
        scan = get_object_or_404(Scan, pk=pk)
        form = ScanForm(request.POST, instance=scan)
        formset = ConditionFormSet(request.POST, instance=scan)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('scan_list')
        return render(request, 'screener/scan_form.html', {'form': form, 'formset': formset, 'scan': scan})

class ScanRunView(View): # For running saved scans from the database
    def get(self, request, pk):
        scan = get_object_or_404(Scan, pk=pk)
        backtest_mode = ('backtest' in request.GET)
        
        # This needs a specific implementation of run_scan that takes a Scan model instance
        # and its associated Condition model instances.
        # Your `indicator_utils.evaluate_filter_row` expects a dictionary for filter data.
        # You'll need to transform `scan.conditions.all()` into that dictionary format.
        
        # Example transformation (conceptual):
        results_from_saved_scan = []
        # for condition_model in scan.conditions.all():
        #     filter_data_dict = {
        #         "indicator": condition_model.left_indicator,
        #         "timeframe": scan.timeframe, # Use the scan's overall timeframe
        #         "field": ..., # Determine field based on left_indicator
        #         "period": ...,# Determine period
        #         "mainOp": condition_model.operator,
        #         "rightType": "number" if condition_model.constant is not None else "indicator",
        #         "rightValue": condition_model.constant,
        #         "rightIndicator": condition_model.right_indicator,
        #         # ... other params ...
        #     }
        #     # Then run this f_data against symbols
        
        print(f"[VIEWS] Running saved scan '{scan.name}'. Actual run logic needs to be implemented here.")
        
        return render(request, 'screener/scan_results.html', {
            'scan': scan,
            'results': [{"symbol": "SAVED_SCAN_PLACEHOLDER", "close": "N/A"}], # Replace with actual results
            'backtest': backtest_mode
        })
    
from .indicator_utils import get_talib_grouped_indicators

def indicator_list_api(request):
    try:
        # This returns: {'Momentum Indicators': [...], 'Overlap Studies': [...], ...}
        return JsonResponse({'groups': get_talib_grouped_indicators()})
    except Exception as e:
        return JsonResponse({'error': str(e), 'groups': {}}, status=500)

