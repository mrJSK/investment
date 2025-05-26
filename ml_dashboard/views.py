import json
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .train_utils import (
    get_available_datasets,
    get_available_models,
    get_all_talib_features,
    get_sample_features,
    run_training_with_capture,
    to_python_type,
)

def dashboard(request):
    datasets = get_available_datasets()
    models = get_available_models()
    indicators = get_all_talib_features()
    return render(request, 'ml_dashboard/dashboard.html', {
        'ml_models': models,
        'datasets': datasets,
        'talib_features': indicators
    })

@csrf_exempt
def train_model(request):
    if request.method == 'POST':
        try:
            selected_model = request.POST.get('ml_model')
            dataset = request.POST.get('dataset')
            feature_configs = json.loads(request.POST.get('feature_configs', '[]'))
            result = run_training_with_capture(selected_model, dataset, feature_configs)   # 1. Call ML
            result = to_python_type(result)                                               # 2. Convert numpy to python
            # Mark as error if result includes "error" key, else success
            if "error" in result:
                result["status"] = "error"
            else:
                result["status"] = "success"
            result["model"] = selected_model
            result["dataset"] = dataset
            # Pass logs/message back in all cases
            return JsonResponse(result)
        except Exception as e:
            # Return error AND the full traceback in logs
            tb = traceback.format_exc()
            return JsonResponse({
                'status': 'error',
                'error': f'{type(e).__name__}: {e}',
                'logs': tb
            }, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

@csrf_exempt
def ajax_get_features(request):
    dataset = request.POST.get('dataset')
    features = get_sample_features(dataset)
    return JsonResponse({'features': features})
    