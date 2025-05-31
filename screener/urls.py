# screener/urls.py
from django.urls import path
from .views import (
    DashboardView,
    # ajax_scan, # This seems like an alternative implementation; we'll focus on run_screener
    ScanCreateView, ScanUpdateView, ScanRunView,
    ScanListView,
    indicator_list, 
    indicator_params, # This might be useful for more detailed param info later
    screener_builder, # Assuming this is for a different page or older version
    run_screener # This will be our main endpoint for the dashboard scan
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'), # Serves dashboard.html
    
    # API endpoints for the dashboard screener
    path('api/indicators/', indicator_list, name='api_indicator_list'),
    path('api/run_screener/', run_screener, name='api_run_screener'), # Main endpoint for dashboard's "Run Scan"

    # URLs for saved scan CRUD operations (if you use them separately)
    path('scans/', ScanListView.as_view(), name='scan_list'),
    path('scan/new/', ScanCreateView.as_view(), name='scan_create'),
    path('scan/<int:pk>/edit/', ScanUpdateView.as_view(), name='scan_edit'),
    path('scan/<int:pk>/run/', ScanRunView.as_view(), name='scan_run_saved'), # For running saved scans from db

    # Other utility/test URLs from your file
    path('api/indicator_params/', indicator_params, name='api_indicator_params'),
    path('screener/', screener_builder, name='screener_builder_page'), # Example name if it's a page
]