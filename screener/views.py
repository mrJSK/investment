from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Scan
from .forms import ScanForm, ConditionFormSet
from .utils import run_scan

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
