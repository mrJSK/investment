# fundamentals/urls.py
from django.urls import path
from . import views

app_name = 'fundamentals'

urlpatterns = [
    # Main fundamentals page (renders the default strong companies table)
    path('', views.FundamentalsView.as_view(), name='fundamentals_page'),

    # API for the sidebar's simple company list (still exists, though sidebar is removed from main page)
    path('api/companies/', views.company_list_api, name='api_company_list'),
    
    # API for the categorized market cap data (original purpose, if still needed)
    path('api/market-cap/', views.market_cap_api, name='api_market_cap'),

    # API for fundamentally strong companies by market cap for the main fundamentals page
    path('api/strong-companies-by-market-cap/', views.strong_companies_market_cap_api, name='api_strong_companies_market_cap'),

    # NEW: API for undervalued companies for a new table on the main fundamentals page
    path('api/undervalued-companies/', views.undervalued_companies_api, name='api_undervalued_companies'),

    # API for individual company details (Deep Dive)
    path('api/company/<str:symbol>/', views.company_detail_api, name='api_company_detail'),

    # URL for the dedicated custom screener page
    path('screener/', views.CustomScreenerView.as_view(), name='custom_screener_page'),
    # API for the custom screener (with user-defined filters)
    path('api/custom-screener/', views.fundamental_screener_api, name='api_custom_screener'),
]