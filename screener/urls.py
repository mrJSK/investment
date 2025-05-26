from django.urls import path
from .views import ScanListView, ScanCreateView, ScanUpdateView, ScanRunView

urlpatterns = [
    path('', ScanListView.as_view(), name='scan_list'),
    path('scan/new/', ScanCreateView.as_view(), name='scan_create'),
    path('scan/<int:pk>/edit/', ScanUpdateView.as_view(), name='scan_edit'),
    path('scan/<int:pk>/run/', ScanRunView.as_view(), name='scan_run'),
]
