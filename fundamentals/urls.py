from django.urls import path
from . import views

app_name = 'fundamentals'

urlpatterns = [
    # The path for the main page is now an empty string, relative to '/fundamentals/'
    path('', views.FundamentalsView.as_view(), name='fundamentals_page'),

    # The API paths are now relative to '/fundamentals/'
    path('api/companies/', views.company_list_api, name='api_company_list'),
    path('api/company/<str:symbol>/', views.company_detail_api, name='api_company_detail'),
]
