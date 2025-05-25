from django.urls import path
from .views import fyers_login_view, fyers_callback # Import all required views

urlpatterns = [
    path('', fyers_login_view, name='fyers_login'),  # Login page
    path('callback/', fyers_callback, name='fyers_callback'),  # Callback after Fyers login
]

