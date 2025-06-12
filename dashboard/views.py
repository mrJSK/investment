# dashboard/views.py

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from django.http import JsonResponse
from . import services
import random

class DashboardView(TemplateView):
    """
    Renders the main HTML template for the dashboard.
    """
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Trading Dashboard'
        return context
    
class HomeView(TemplateView):
    """
    Renders the main Home/Launchpad page for the entire suite.
    """
    template_name = 'dashboard/home.html'

    def dispatch(self, request, *args, **kwargs):
        """
        This method runs before any other in the view.
        We use it to check if the user has a Fyers token in their session.
        If not, we redirect them to the login page.
        """
        if 'fyers_access_token' not in request.session:
            # If the token is missing, redirect to the login page
            return redirect(reverse('fyers_login')) 
            
        # If the token exists, proceed to render the page as normal
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ScreenerX'
        return context

# --- API VIEWS ---

def trading_data_api(request):
    """
    API endpoint ONLY for fast-loading mock trading data. This will respond instantly.
    """
    mock_live_trades = [
        { "assetClass": "Stocks", "strategy": "Golden Crossover", "symbol": "RELIANCE-EQ", "qty": 100, "entryPrice": 2850.50, "dayOpen": 2845.00 },
        { "assetClass": "Stocks", "strategy": "RSI Bounce", "symbol": "HDFCBANK-EQ", "qty": 50, "entryPrice": 1595.00, "dayOpen": 1601.50 },
    ]
    mock_closed_trades = [
        { "symbol": "TATAMOTORS-EQ", "pnl": 5230.50, "entryDate": "2025-06-02", "exitDate": "2025-06-12", "reason": "Take Profit" },
        { "symbol": "WIPRO-EQ", "pnl": -1890.00, "entryDate": "2025-05-28", "exitDate": "2025-06-11", "reason": "Stop Loss" },
    ]
    # Simulate price ticks
    for trade in mock_live_trades:
        tick = (random.random() - 0.5) * (trade['entryPrice'] * 0.01)
        trade['currentPrice'] = round(trade['entryPrice'] + tick, 2)

    return JsonResponse({
        "live_trades": mock_live_trades,
        "closed_trades": mock_closed_trades,
    })

def market_news_api(request):
    """
    API endpoint for market news. Calls the database-driven service function.
    This might be slow as it involves scraping, but it won't block other parts of the UI.
    """
    try:
        market_news = services.get_and_update_market_news()
    except Exception as e:
        print(f"API Error fetching news in market_news_api: {e}")
        market_news = {"regular": [], "watch_list": []}
    return JsonResponse(market_news)

def nse_announcements_api(request):
    """
    API endpoint for corporate announcements.
    """
    try:
        nse_announcements = services.get_cached_or_fresh_announcements()
    except Exception as e:
        print(f"API Error fetching NSE announcements in nse_announcements_api: {e}")
        nse_announcements = {}
    return JsonResponse(nse_announcements)

def financial_reports_api(request):
    """
    API endpoint for fetching processed ANNUAL financial reports from the database.
    """
    try:
        financial_reports = services.get_cached_or_fresh_financial_reports()
    except Exception as e:
        print(f"API Error fetching Annual Financial Reports in financial_reports_api: {e}")
        financial_reports = []
    return JsonResponse({"financial_reports": financial_reports})

def quarterly_financials_api(request):
    """
    API endpoint for fetching processed QUARTERLY financial reports from the database.
    """
    try:
        quarterly_reports = services.get_latest_quarterly_reports()
    except Exception as e:
        print(f"API Error fetching Quarterly Financials in quarterly_financials_api: {e}")
        quarterly_reports = []
    return JsonResponse({"quarterly_reports": quarterly_reports})

