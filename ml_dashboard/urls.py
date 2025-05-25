from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='ml_dashboard'),
    path('train/', views.train_model, name='ml_train_model'),
    path('ajax_get_features/', views.ajax_get_features, name='ml_get_features'),
]
