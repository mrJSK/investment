from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Scan
from .forms import ScanForm, ConditionFormSet
from .utils import run_scan
import json

class ScanListView(View):
    def get(self, request):
        scans = Scan.objects.all().order_by('-created_at')
        return render(request, 'screener/scan_list.html', {'scans': scans})

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
            return redirect('scan_list')
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

class ScanRunView(View):
    def get(self, request, pk):
        scan = get_object_or_404(Scan, pk=pk)
        backtest = ('backtest' in request.GET)
        results = run_scan(scan, backtest=backtest)
        return render(request, 'screener/scan_results.html', {
            'scan': scan,
            'results': results,
            'backtest': backtest
        })

class DashboardView(TemplateView):
    template_name = 'screener/dashboard.html'

@csrf_exempt
def ajax_scan(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Build a "Scan" object on the fly from request data
        from .models import Scan, Condition
        from types import SimpleNamespace

        # Get timeframe/segment/conditions from the request
        timeframe = data.get('timeframe', 'daily')
        segment = data.get('segment', 'Nifty 50')
        # Build condition objects (mimic what Django forms do)
        conditions = []
        for cond in data.get('filters', []):
            # You may want to map JS field names to model fields here
            condition_obj = SimpleNamespace(
                left_indicator=cond.get('left') or cond.get('left_indicator', ''),
                operator=cond.get('op') or cond.get('operator', ''),
                right_indicator=cond.get('right') or cond.get('right_indicator', ''),
                constant=cond.get('constant', None),
                logic=cond.get('logic', 'AND'),
            )
            conditions.append(condition_obj)

        # Build a fake Scan object for utils.py (must have .segment, .timeframe, .conditions)
        scan = SimpleNamespace(
            segment=segment,
            timeframe=timeframe,
            conditions=conditions
        )

        # Use real scan logic!
        from .utils import run_scan
        results = run_scan(scan, backtest=False)  # For live results, not historical

        # Format output for the dashboard table
        formatted = []
        for r in results:
            formatted.append({
                "symbol": r["symbol"],
                "price": r["close"],
                "change": r["pct_change"],
                "volume": r["volume"],
                "matched": r["matched"],
                "signal": "",  # (Optionally add logic for buy/sell signal here)
            })
        return JsonResponse({"results": formatted})
    return JsonResponse({"error": "POST only"}, status=400)

# screener/views.py (add to your file)

from django.http import JsonResponse
from .indicator_utils import SYMBOLS, TA_INDICATOR_LABELS, evaluate_filter_row, get_talib_function_list, get_talib_params, load_ohlcv

def indicator_list(request):
    indicators = get_talib_function_list()
    return JsonResponse({'indicators': [
        {"value": i, "label": f"{TA_INDICATOR_LABELS.get(i, i)} ({i})"}
        for i in indicators
    ]})


def indicator_params(request):
    fn = request.GET.get('fn')
    if not fn:
        return JsonResponse({'error': 'Missing function name'}, status=400)
    try:
        params = get_talib_params(fn)
        return JsonResponse({'params': params})
    except AttributeError:
        return JsonResponse({'error': 'Function not found'}, status=404)
    
from django.shortcuts import render
def screener_builder(request):
    return render(request, 'screener/builder.html')


def run_screener(request):
    # POST endpoint for screener filter logic
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    body = json.loads(request.body)
    filters = body.get("filters", [])
    segment = body.get("segment", "Nifty50")
    # For demo, use all symbols; filter by segment if needed
    matches = []
    for symbol in SYMBOLS:
        try:
            row_results = []
            for f in filters:
                # Load data for each row, with per-row timeframe if needed
                df = load_ohlcv(symbol, f['timeframe'])
                row_results.append(evaluate_filter_row(df, f))
            if all(row_results):  # Only include if all rows pass
                matches.append(symbol)
        except Exception as e:
            print(f"{symbol} failed: {e}")
            continue
    return JsonResponse({"matches": matches})
