"""
URL configuration for the dashboard app.
This file maps each API request to its corresponding view function.
"""
from django.urls import path
from . import views

# This is a common practice to namespace the URLs
app_name = 'dashboard'

urlpatterns = [
    # The main dashboard view is now at the root of this app's URL namespace.
    # To access it, you will go to /dashboard/ in the browser.
    path('', views.DashboardView.as_view(), name='main_dashboard'),
    
    # NOTE: The Home/Launchpad view has been moved to its own distinct path
    # to avoid conflicts. You can access it at /dashboard/home/
    path('home/', views.HomeView.as_view(), name='home'),

    # --- API ENDPOINTS ---
    # These paths are now correct and will be found at /dashboard/api/*
    path('api/trading-data/', views.trading_data_api, name='api_trading_data'),
    path('api/market-news/', views.market_news_api, name='api_market_news'),
    path('api/nse-announcements/', views.nse_announcements_api, name='api_nse_announcements'),
    path('api/financial-reports/', views.financial_reports_api, name='api_financial_reports'),
    path('api/quarterly-financials/', views.quarterly_financials_api, name='api_quarterly_financials'),
# This path connects the new corporate_actions_api view to a URL
    path('api/corporate-actions/', views.corporate_actions_api, name='api_corporate_actions'),
]