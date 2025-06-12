"""
URL configuration for the dashboard app.
This file maps each API request to its corresponding view function.
"""
from django.urls import path
from . import views

# This is a common practice to namespace the URLs
app_name = 'dashboard'

urlpatterns = [
    # Main dashboard view (the HTML page itself)
    path('dashboard/', views.DashboardView.as_view(), name='main_dashboard'),
    path('', views.HomeView.as_view(), name='home'),

    # --- REFACTORED API ENDPOINTS ---
    # Each endpoint is now separate to allow for asynchronous loading on the frontend.

    # 1. Endpoint for fast-loading mock trading data
    path('api/trading-data/', views.trading_data_api, name='api_trading_data'),
    
    # 2. Endpoint for slower, scraped market news
    path('api/market-news/', views.market_news_api, name='api_market_news'),

    # 3. Endpoint for corporate announcements from the NSE feed
    path('api/nse-announcements/', views.nse_announcements_api, name='api_nse_announcements'),

    # 4. Endpoint for ANNUAL financial reports from the database
    path('api/financial-reports/', views.financial_reports_api, name='api_financial_reports'),

    # 5. Endpoint for QUARTERLY financial results from the database
    path('api/quarterly-financials/', views.quarterly_financials_api, name='api_quarterly_financials'),
]
