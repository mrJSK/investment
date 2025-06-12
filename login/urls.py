from django.urls import path
from .views import fyers_login_view, fyers_callback, fyers_logout_view # Import all required views

urlpatterns = [
    path('', fyers_login_view, name='fyers_login'),  # Login page
    path('callback/', fyers_callback, name='fyers_callback'),  # Callback after Fyers login
    path('logout/', fyers_logout_view, name='fyers_logout'),  # Logout
]

