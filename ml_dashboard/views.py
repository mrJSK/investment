import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .train_utils import (
    get_available_datasets,
    get_available_models,
    get_all_talib_features,
    get_sample_features,
    run_training_with_capture,
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
            result = run_training_with_capture(selected_model, dataset, feature_configs)
            result.update({
                'status': 'success' if 'error' not in result else 'error',
                'model': selected_model,
                'dataset': dataset,
                'message': result.get('message', 'Training complete!' if 'error' not in result else result.get('error'))
            })
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error: {e}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

@csrf_exempt
def ajax_get_features(request):
    dataset = request.POST.get('dataset')
    features = get_sample_features(dataset)
    return JsonResponse({'features': features})
