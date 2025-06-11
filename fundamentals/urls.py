from django.urls import path
from . import views

app_name = 'fundamentals'

urlpatterns = [
    # Main fundamentals page
    path('', views.FundamentalsView.as_view(), name='fundamentals_page'),

    # --- API Paths ---
    # API for the sidebar's simple company list
    path('api/companies/', views.company_list_api, name='api_company_list'),
    
    # API for the market cap tab's categorized data
    path('api/market-cap-data/', views.market_cap_api, name='api_market_cap_data'),

    # API for individual company details
    path('api/company/<str:symbol>/', views.company_detail_api, name='api_company_detail'),
]
