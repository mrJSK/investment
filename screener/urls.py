# screener/urls.py
from django.urls import path
from .views import DashboardView, ajax_scan, ScanCreateView, ScanUpdateView, ScanRunView, ScanListView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('ajax-scan/', ajax_scan, name='ajax_scan'),
    path('scan/new/', ScanCreateView.as_view(), name='scan_create'),
    path('scan/<int:pk>/edit/', ScanUpdateView.as_view(), name='scan_edit'),
    path('scan/<int:pk>/run/', ScanRunView.as_view(), name='scan_run'),
    path('scans/', ScanListView.as_view(), name='scan_list'),
]
