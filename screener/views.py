from django.shortcuts import render
from .models import Screener
from .services import run_screener

def scanner_view(request):
    result = None
    screeners = Screener.objects.all()
    selected_id = None

    if request.method == "POST":
        screener_id = request.POST.get("screener_id")
        if screener_id:
            selected_id = int(screener_id)
            result = run_screener(selected_id)

    return render(request, 'screener/dashboard.html', {
        'screeners': screeners,
        'results': result,
        'selected_id': selected_id
    })
