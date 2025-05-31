from django.urls import path
from .views import (
    DashboardView, ajax_scan, ScanCreateView, ScanUpdateView, ScanRunView,
    ScanListView, indicator_list, indicator_params,
    screener_builder, run_screener
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('ajax-scan/', ajax_scan, name='ajax_scan'),
    path('scan/new/', ScanCreateView.as_view(), name='scan_create'),
    path('scan/<int:pk>/edit/', ScanUpdateView.as_view(), name='scan_edit'),
    path('scan/<int:pk>/run/', ScanRunView.as_view(), name='scan_run'),
    path('scans/', ScanListView.as_view(), name='scan_list'),
    path('api/indicators/', indicator_list, name='indicator_list'),
    path('api/indicator_params/', indicator_params, name='indicator_params'),
    path('screener/', screener_builder, name='screener_builder'),
    path('api/run_screener/', run_screener, name='run_screener'),
]
