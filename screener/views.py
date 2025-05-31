from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # Only if not using Django's template CSRF for POSTs from JS
from .models import Scan # For saved scans
# from .forms import ScanForm, ConditionFormSet # For saved scan CRUD views
from .indicator_utils import (
    SYMBOLS, TA_INDICATOR_LABELS, evaluate_filter_row, 
    get_talib_function_list, get_talib_params, load_ohlcv
)
import json
from types import SimpleNamespace
import traceback # For detailed error logging

# --- Views for Saved Scans (CRUD operations) ---
class ScanListView(View):
    def get(self, request):
        scans = Scan.objects.all().order_by('-created_at')
        return render(request, 'screener/scan_list.html', {'scans': scans})

class ScanCreateView(View): # Assumes you have ScanForm and ConditionFormSet defined in forms.py
    def get(self, request):
        # from .forms import ScanForm, ConditionFormSet # Example import
        # form = ScanForm()
        # formset = ConditionFormSet()
        # For now, providing a placeholder if forms.py is not fully set up for this example
        return render(request, 'screener/scan_form.html', {'form': {}, 'formset': {}})


    def post(self, request):
        # from .forms import ScanForm, ConditionFormSet # Example import
        # form = ScanForm(request.POST)
        # formset = ConditionFormSet(request.POST)
        # if form.is_valid() and formset.is_valid():
        #     scan = form.save()
        #     formset.instance = scan
        #     formset.save()
        #     return redirect('scan_list')
        # return render(request, 'screener/scan_form.html', {'form': form, 'formset': formset})
        return redirect('scan_list') # Placeholder

class ScanUpdateView(View): # Assumes you have ScanForm and ConditionFormSet
    def get(self, request, pk):
        scan = get_object_or_404(Scan, pk=pk)
        # from .forms import ScanForm, ConditionFormSet # Example import
        # form = ScanForm(instance=scan)
        # formset = ConditionFormSet(instance=scan)
        return render(request, 'screener/scan_form.html', {'form': {}, 'formset': {}, 'scan': scan})

    def post(self, request, pk):
        scan = get_object_or_404(Scan, pk=pk)
        # from .forms import ScanForm, ConditionFormSet # Example import
        # form = ScanForm(request.POST, instance=scan)
        # formset = ConditionFormSet(request.POST, instance=scan)
        # if form.is_valid() and formset.is_valid():
        #     form.save()
        #     formset.save()
        #     return redirect('scan_list')
        # return render(request, 'screener/scan_form.html', {'form': form, 'formset': formset, 'scan': scan})
        return redirect('scan_list') # Placeholder

class ScanRunView(View): # This runs a SAVED scan from the database
    def get(self, request, pk):
        scan = get_object_or_404(Scan, pk=pk)
        backtest = ('backtest' in request.GET)
        
        # You need a version of run_scan that works with saved Scan models and Condition models
        # The existing run_scan in your utils.py or the run_screener below might need adaptation
        # For now, let's assume a placeholder results
        results_placeholder = [
            {"symbol": "SAVED_SCAN_STOCK1", "close": "100", "pct_change": "1%", "volume": "1M", "matched": "Conditions met"},
        ]
        # results = run_saved_scan_logic(scan, backtest=backtest) # Implement this
        return render(request, 'screener/scan_results.html', {
            'scan': scan,
            'results': results_placeholder, # Replace with actual results
            'backtest': backtest
        })

# --- Dashboard and Dynamic Screener API Views ---

class DashboardView(TemplateView):
    template_name = 'screener/dashboard.html' # Main page for the dynamic screener

# API to get list of indicators for the frontend builder.js
def indicator_list_api(request): # Renamed to avoid clash if you have other indicator_list views
    talib_functions = get_talib_function_list() # From your indicator_utils.py
    indicators_with_params = []
    for func_name in talib_functions:
        try:
            # Fetch parameters for each TA-Lib function
            params_info = get_talib_params(func_name) # From your indicator_utils.py
            param_names = [p['name'] for p in params_info if p['name'] not in ['real', 'open', 'high', 'low', 'close', 'volume']]
            # Add 'timeframe' and 'field' as common conceptual params if not function args
            std_params = ["timeframe"]
            if not any(p in func_name.upper() for p in ["VOLUME", "OBV", "ADLINE", "AD"]): # These usually don't take price field
                 if not any(p_name in ["price", "prices"] for p_name in param_names): # If no explicit price series param
                    std_params.append("field")


            # Combine specific TA-Lib params with standard ones
            # Ensure no duplicates and maintain order for clarity if needed
            combined_params = std_params[:]
            for p_name in param_names:
                if p_name not in combined_params:
                    # Map talib param names to frontend friendly names if needed
                    # e.g., timeperiod -> period, fastperiod -> fast_period
                    fe_param_name = p_name
                    if p_name == "timeperiod": fe_param_name = "period"
                    elif p_name == "fastperiod": fe_param_name = "fast_period"
                    elif p_name == "slowperiod": fe_param_name = "slow_period"
                    elif p_name == "signalperiod": fe_param_name = "signal_period"
                    elif p_name == "nbdevup": fe_param_name = "nbdev" # For BBANDS
                    elif p_name == "nbdevdn": continue # nbdevup and nbdevdn are usually same for BBANDS
                    
                    if fe_param_name not in combined_params:
                         combined_params.append(fe_param_name)

            indicators_with_params.append({
                "value": func_name, 
                "label": f"{TA_INDICATOR_LABELS.get(func_name, func_name)} ({func_name})",
                "params": combined_params
            })
        except Exception as e:
            print(f"Could not get params for {func_name}: {e}")
            indicators_with_params.append({ # Fallback
                "value": func_name,
                "label": f"{TA_INDICATOR_LABELS.get(func_name, func_name)} ({func_name})",
                "params": ["timeframe", "field", "period"] # Generic fallback
            })
    return JsonResponse({'indicators': indicators_with_params})

# API to get parameters for a specific indicator (your existing view)
def indicator_params_api(request): # Renamed to avoid clash
    fn = request.GET.get('fn')
    if not fn:
        return JsonResponse({'error': 'Missing function name'}, status=400)
    try:
        params = get_talib_params(fn) # From your indicator_utils.py
        return JsonResponse({'params': params})
    except AttributeError: # getattr in get_talib_params might raise this for non-talib functions
        return JsonResponse({'error': f"TA-Lib function '{fn}' not found or error getting params."}, status=404)
    except Exception as e:
        return JsonResponse({'error': f"Error getting params for '{fn}': {str(e)}"}, status=500)

# API to run the screener from the dynamic dashboard
@csrf_exempt # Use this if you are not submitting via a Django form and handling CSRF via AJAX headers
def run_screener_api_new(request): # Renamed to distinguish from your existing run_screener
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    
    try:
        body = json.loads(request.body)
        filters_from_frontend = body.get("filters", [])
        segment = body.get("segment", "Nifty 500") # Default segment from dashboard.html

        # Map segment to your list of symbols (SYMBOLS in indicator_utils is currently from os.listdir)
        # This part needs to be robust, e.g., loading from a segment definition file or DB
        symbols_to_scan = SYMBOLS 
        print(f"Scanning segment: {segment} with {len(symbols_to_scan)} symbols using {len(filters_from_frontend)} filters.")

        matched_symbols_details = []
        for symbol in symbols_to_scan:
            try:
                all_conditions_met_for_symbol = True
                if not filters_from_frontend: # If no filters, decide behavior (match all or none)
                    # To match Chartink (which usually requires at least one filter), let's assume no match if no filters
                    all_conditions_met_for_symbol = False # Or True to list all in segment
                
                for f_data in filters_from_frontend:
                    # The f_data structure from builder.js (transformed) should have:
                    # indicator, timeframe, field, period, mainOp, rightType, rightValue, rightIndicator, rightPeriod etc.
                    # Ensure 'timeframe' is correctly passed to load_ohlcv
                    current_filter_timeframe = f_data.get('timeframe', 'Daily') # Default timeframe for data loading
                    
                    df = load_ohlcv(symbol, current_filter_timeframe)
                    if df is None or df.empty:
                        all_conditions_met_for_symbol = False
                        # print(f"No data or empty df for {symbol} on {current_filter_timeframe}")
                        break 
                    
                    if not evaluate_filter_row(df.copy(), f_data): # evaluate_filter_row is from your indicator_utils
                        all_conditions_met_for_symbol = False
                        break
                
                if all_conditions_met_for_symbol:
                    # Fetch latest daily data for price details if symbol matched
                    df_daily_latest = load_ohlcv(symbol, 'Daily') # Assuming 'Daily' for consistent LTP/Change
                    if df_daily_latest is not None and not df_daily_latest.empty:
                        latest_row = df_daily_latest.iloc[-1]
                        prev_close = df_daily_latest['close'].iloc[-2] if len(df_daily_latest) > 1 else latest_row['close']
                        
                        ltp = latest_row.get('close', 0)
                        volume = latest_row.get('volume', 0)
                        pct_change_val = ((ltp - prev_close) / prev_close * 100) if prev_close else 0
                        
                        matched_symbols_details.append({
                            "symbol": symbol,
                            "ltp": f"{ltp:.2f}",
                            "change_pct": f"{pct_change_val:.2f}%",
                            "volume": f"{volume:.0f}"
                        })
                    else: # Fallback if daily data is missing for a matched symbol
                        matched_symbols_details.append({"symbol": symbol, "ltp": "N/A", "change_pct": "N/A", "volume": "N/A"})

            except Exception as e:
                print(f"Error processing symbol {symbol} during scan: {e}")
                # traceback.print_exc() # For more detailed error logging during development
                continue
        
        print(f"Scan complete. Matched {len(matched_symbols_details)} symbols.")
        return JsonResponse({"results": matched_symbols_details})
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        traceback.print_exc() # Print detailed exception to server console
        return JsonResponse({"error": f"Server error during scan: {str(e)}"}, status=500)

# Your existing `ajax_scan` view - it seems to construct a SimpleNamespace scan object
# and call `utils.run_scan` (which is not defined in the provided `indicator_utils.py` or `services.py`).
# If you intend to use this, ensure `utils.run_scan` is correctly implemented.
# For the dashboard, `run_screener_api_new` above is more aligned with `indicator_utils.evaluate_filter_row`.
@csrf_exempt
def ajax_scan(request): # This is your original ajax_scan, review if it's still needed
    if request.method == 'POST':
        data = json.loads(request.body)
        timeframe = data.get('timeframe', 'daily') # This timeframe is not used in your example below
        segment = data.get('segment', 'Nifty 50')
        
        # This part constructs a 'scan' object differently than `run_screener_api_new`
        # It seems to assume a different structure for `filters` than what builder.js creates
        # or what `evaluate_filter_row` expects.
        conditions_data = []
        for cond_frontend in data.get('filters', []):
            # This mapping needs to be precise based on what builder.js sends
            # and what your models.Condition or SimpleNamespace expects for utils.run_scan
            condition_obj_data = {
                'left_indicator': cond_frontend.get('left', {}).get('value') if isinstance(cond_frontend.get('left'), dict) else cond_frontend.get('left_indicator',''),
                'operator': cond_frontend.get('op') or cond_frontend.get('operator',''),
                'right_indicator': cond_frontend.get('right', {}).get('value') if isinstance(cond_frontend.get('right'), dict) else cond_frontend.get('right_indicator',''),
                'constant': cond_frontend.get('right', {}).get('value') if isinstance(cond_frontend.get('right'), dict) and cond_frontend.get('right').get('type') == 'number' else cond_frontend.get('constant'),
                'logic': cond_frontend.get('logic', 'AND'),
                # You'll need to pass timeframe and params for indicators if utils.run_scan needs them
            }
            conditions_data.append(SimpleNamespace(**condition_obj_data))

        scan_obj_for_util = SimpleNamespace(
            segment=segment,
            timeframe=timeframe, # Overall timeframe for the scan
            conditions=conditions_data # List of condition namespaces
        )
        
        # from .utils import run_scan as run_scan_from_utils # Assuming utils.run_scan exists and works with this
        # results = run_scan_from_utils(scan_obj_for_util, backtest=False)
        results_placeholder = [{"symbol": "FROM_AJAX_SCAN", "close": "200", "pct_change": "2%", "volume": "2M", "matched": "Ajax conditions"}]


        formatted = []
        for r in results_placeholder: # Replace with actual results
            formatted.append({
                "symbol": r["symbol"],
                "ltp": r.get("close") or r.get("price"), # Adjust keys based on what run_scan_from_utils returns
                "change_pct": r.get("pct_change") or r.get("change"),
                "volume": r["volume"],
                "matched": r.get("matched","N/A"),
            })
        return JsonResponse({"results": formatted})
    return JsonResponse({"error": "POST only for ajax_scan"}, status=400)


# This is the run_screener view from your uploaded file,
# which is mapped to /api/run_screener/ in your urls.py.
# I've integrated its core logic into run_screener_api_new above.
# If you prefer to keep this separate, ensure builder.js calls the correct one
# and that the data formats align.
def run_screener(request): # Original run_screener from your file
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    body = json.loads(request.body)
    filters = body.get("filters", []) # Expects filters in the format for evaluate_filter_row
    segment = body.get("segment", "Nifty50") # Typo? Nifty 50?
    
    symbols_to_scan = SYMBOLS # From indicator_utils
    # Potentially filter symbols_to_scan by segment here

    matches = []
    for symbol in symbols_to_scan:
        try:
            all_conditions_pass = True
            if not filters: all_conditions_pass = False # Or true if you want all symbols on no filter

            for f_data in filters:
                # Each f_data needs 'timeframe' for load_ohlcv
                # and all other params for evaluate_filter_row
                tf = f_data.get('timeframe', 'Daily') # Make sure frontend sends this correctly structured
                df = load_ohlcv(symbol, tf)
                if df is None or df.empty:
                    all_conditions_pass = False
                    break
                if not evaluate_filter_row(df.copy(), f_data):
                    all_conditions_pass = False
                    break
            
            if all_conditions_pass:
                matches.append(symbol) # Only returns symbols
        except Exception as e:
            print(f"{symbol} failed in run_screener: {e}")
            continue
    # This view only returns symbols, builder.js's updateResultsTable expects more details.
    # Consider modifying this to return detailed results like in run_screener_api_new
    return JsonResponse({"matches": matches})


# A simple view for a different builder page you might have
def screener_builder(request):
    return render(request, 'screener/builder.html')