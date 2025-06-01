# screener/urls.py (App level)
from django.urls import path
from .views import (
    DashboardView,
    ScanListView,
    indicator_list_api,
    indicator_params,
    run_screener,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('api/indicators/', indicator_list_api, name='api_indicator_list'),
    path('api/indicator_params/', indicator_params, name='api_indicator_params'),
    path('api/run_screener/', run_screener, name='api_run_screener'),
    path('scans/', ScanListView.as_view(), name='scan_list'),
    # path('scan/new/', ScanCreateView.as_view(), name='scan_create'),
    # path('scan/<int:pk>/edit/', ScanUpdateView.as_view(), name='scan_edit'),
    # path('scan/<int:pk>/run/', ScanRunView.as_view(), name='scan_run_saved'),
    # path('screener/', screener_builder, name='screener_builder_page'),
    # path('ajax-scan/', ajax_scan, name='ajax_scan_endpoint'),
]
