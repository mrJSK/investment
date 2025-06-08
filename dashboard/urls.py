"""
URL configuration for the dashboard app.
"""
from django.urls import path
from . import views

# This is a common practice to namespace the URLs
app_name = 'dashboard'

urlpatterns = [
    # Main dashboard view (HTML page)
    path('', views.DashboardView.as_view(), name='main_dashboard'),

    # The single, consolidated API endpoint for all dashboard data
    path('api/live-data/', views.live_data_api, name='api_live_data'), #includes the live market news
]