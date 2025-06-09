# dashboard/views.py

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from . import services
import random

class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Trading Dashboard'
        return context

def live_data_api(request):
    """
    API endpoint to fetch all live dashboard data: positions, trades, news, and announcements.
    """
    # --- Mock Trading Data (Unchanged) ---
    mock_live_trades = [
        { "assetClass": "Stocks", "strategy": "Golden Crossover", "symbol": "RELIANCE-EQ", "qty": 100, "entryPrice": 2850.50, "dayOpen": 2845.00 },
        { "assetClass": "Stocks", "strategy": "RSI Bounce", "symbol": "HDFCBANK-EQ", "qty": 50, "entryPrice": 1595.00, "dayOpen": 1601.50 },
        { "assetClass": "Index Options", "strategy": "Straddle King", "symbol": "NIFTY 22800 CE", "qty": 50, "entryPrice": 150.25, "dayOpen": 145.00 },
        { "assetClass": "Index Options", "strategy": "Straddle King", "symbol": "NIFTY 22800 PE", "qty": 50, "entryPrice": 180.50, "dayOpen": 190.10 },
    ]
    mock_closed_trades = [
        { "symbol": "TATAMOTORS-EQ", "pnl": 5230.50, "entryDate": "2025-06-02", "exitDate": "2025-06-06", "reason": "Take Profit" },
        { "symbol": "WIPRO-EQ", "pnl": -1890.00, "entryDate": "2025-05-28", "exitDate": "2025-06-05", "reason": "Stop Loss" },
    ]
    for trade in mock_live_trades:
        tick = (random.random() - 0.5) * (trade['entryPrice'] * 0.01)
        trade['currentPrice'] = round(trade['entryPrice'] + tick, 2)

    # --- Fetch Market News & Announcements ---
    try:
        market_news = services.get_cached_or_fresh_news()
    except Exception as e:
        print(f"API Error fetching news in live_data_api: {e}")
        market_news = {"regular": [], "watch_list": []}

    try:
        # NEW: Fetch categorized NSE announcements
        nse_announcements = services.get_cached_or_fresh_announcements()
    except Exception as e:
        print(f"API Error fetching NSE announcements in live_data_api: {e}")
        nse_announcements = {}

    # --- Combine all data into a single response ---
    return JsonResponse({
        "live_trades": mock_live_trades,
        "closed_trades": mock_closed_trades,
        "market_news": market_news,
        "nse_announcements": nse_announcements, # ADDED
    })