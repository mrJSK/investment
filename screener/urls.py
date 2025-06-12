# screener/urls.py (App level)
from django.urls import path
from .views import (
    ScreenerDashboardView,
    indicator_list_api,
    indicator_params_api,
    run_screener,
)
from screener import views

# FIX: Added app_name to register the 'screener' namespace
app_name = 'screener'

urlpatterns = [
    path('', ScreenerDashboardView.as_view(), name='dashboard'),
    path('api/indicators/', indicator_list_api, name='api_indicator_list'),
    path('api/indicator_params/', indicator_params_api, name='api_indicator_params'),
    path('api/run_screener/', run_screener, name='api_run_screener'),
    path('api/saved_scans/', views.saved_scans_list, name='saved_scans_list'),
    path('api/save_scan/', views.save_scan, name='save_scan'),
    path('api/run_backtest/', views.run_backtest_api, name='api_run_backtest'),
]
