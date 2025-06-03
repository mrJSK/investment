# screener/urls.py (App level)
from django.urls import path
from .views import (
    DashboardView,
    indicator_list_api,
    indicator_params_api, # Changed from indicator_params to match views_py_cleaned_v2
    run_screener,
    # ScanListView, # Commented out as it was removed from the cleaned views.py
    # ScanCreateView, ScanUpdateView, ScanRunView, # Commented out
    # indicator_list, # This was an older version, indicator_list_api is used
    # screener_builder, # Commented out
    # ajax_scan # Commented out
)
from screener import views

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('api/indicators/', indicator_list_api, name='api_indicator_list'),
    path('api/indicator_params/', indicator_params_api, name='api_indicator_params'), # Ensure view name matches
    path('api/run_screener/', run_screener, name='api_run_screener'),
    path('api/saved_scans/', views.saved_scans_list, name='saved_scans_list'),
    path('api/save_scan/', views.save_scan, name='save_scan'),
    path('backtest/<int:scan_id>/', views.backtest_view, name='backtest_view'),
    
    # Commenting out URLs related to views that were removed for cleaning.
    # If you need the saved scan functionality, you'll need to ensure those views
    # are correctly defined in views.py or managed in a separate module.
    # path('scans/', ScanListView.as_view(), name='scan_list'),
    # path('scan/new/', ScanCreateView.as_view(), name='scan_create'),
    # path('scan/<int:pk>/edit/', ScanUpdateView.as_view(), name='scan_edit'),
    # path('scan/<int:pk>/run/', ScanRunView.as_view(), name='scan_run_saved'),
    # path('screener/', screener_builder, name='screener_builder_page'),
    # path('ajax-scan/', ajax_scan, name='ajax_scan_endpoint'),
]
