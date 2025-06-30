# fundamentals/urls.py
from django.urls import path
from . import views # Import all views

app_name = 'fundamentals'

urlpatterns = [
    # Main fundamentals page (renders the HTML container)
    path('', views.FundamentalsView.as_view(), name='fundamentals_page'),

    # --- API Paths for JavaScript fetching ---
    # API for the sidebar's simple company list
    path('api/companies/', views.company_list_api, name='api_company_list'),
    
    # API for the categorized fundamental screener data
    path('api/fundamental-screener/', views.fundamental_screener_api, name='api_fundamental_screener'),

    # API for individual company details (Deep Dive)
    path('api/company/<str:symbol>/', views.company_detail_api, name='api_company_detail'),
]

