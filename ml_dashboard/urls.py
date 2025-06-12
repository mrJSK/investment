# ml_dashboard/urls.py

from django.urls import path
from . import views

# Add this line if you plan to use namespacing like 'ml:ml_dashboard'
app_name = 'ml'

urlpatterns = [
    # FIX: Changed 'views.dashboard' to the correct function name 'views.ml_dashboard'
    path('', views.ml_dashboard, name='ml_dashboard'),

    # These other URLs are correct and remain unchanged
    path('train/', views.train_model, name='ml_train_model'),
    path('ajax_get_features/', views.ajax_get_features, name='ml_get_features'),
]
