from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from . import services
import random # Import the random module

class DashboardView(TemplateView):
    """
    Renders the main trading dashboard page.
    """
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Trading Dashboard'
        return context

# --- Main API Endpoint (Consolidated) ---

def live_data_api(request):
    """
    API endpoint to fetch all live dashboard data:
    open positions, closed trades, portfolio stats, and market news.
    """
    # --- Mock Trading Data ---
    mock_live_trades = [
        { "assetClass": "Stocks", "strategy": "Golden Crossover", "symbol": "RELIANCE-EQ", "qty": 100, "entryPrice": 2850.50, "dayOpen": 2845.00 },
        { "assetClass": "Stocks", "strategy": "RSI Bounce", "symbol": "HDFCBANK-EQ", "qty": 50, "entryPrice": 1595.00, "dayOpen": 1601.50 },
        { "assetClass": "Stocks", "strategy": "Golden Crossover", "symbol": "INFY-EQ", "qty": 200, "entryPrice": 1450.10, "dayOpen": 1448.20 },
        { "assetClass": "Index Options", "strategy": "Straddle King", "symbol": "NIFTY 22800 CE", "qty": 50, "entryPrice": 150.25, "dayOpen": 145.00 },
        { "assetClass": "Index Options", "strategy": "Straddle King", "symbol": "NIFTY 22800 PE", "qty": 50, "entryPrice": 180.50, "dayOpen": 190.10 },
        { "assetClass": "Futures", "strategy": "Trend Rider", "symbol": "BANKNIFTY JUN FUT", "qty": 15, "entryPrice": 49500.00, "dayOpen": 49450.00 },
        { "assetClass": "Stock Options", "strategy": "Bull Call Spread", "symbol": "RELIANCE 2900 CE", "qty": 250, "entryPrice": 45.50, "dayOpen": 42.00 }
    ]

    mock_closed_trades = [
        { "symbol": "TATAMOTORS-EQ", "pnl": 5230.50, "entryDate": "2025-06-02", "exitDate": "2025-06-06", "reason": "Take Profit" },
        { "symbol": "WIPRO-EQ", "pnl": -1890.00, "entryDate": "2025-05-28", "exitDate": "2025-06-05", "reason": "Stop Loss" },
    ]

    # Simulate live price ticks for the prototype
    for trade in mock_live_trades:
        # Using random for a slightly more realistic price fluctuation
        tick = (random.random() - 0.5) * (trade['entryPrice'] * 0.01)
        trade['currentPrice'] = round(trade['entryPrice'] + tick, 2)

    # --- Fetch Market News ---
    # We now call the news service directly from our main API view
    try:
        market_news = services.get_cached_or_fresh_news()
    except Exception as e:
        print(f"API Error fetching news in live_data_api: {e}")
        market_news = [] # Ensure we always return a list

    # --- Combine all data into a single response ---
    return JsonResponse({
        "live_trades": mock_live_trades,
        "closed_trades": mock_closed_trades,
        "market_news": market_news, # Add the news data to the response
    })


# We no longer need the separate market_news_api view,
# but you need to make sure your urls.py points to the correct view.
# Let's check urls.py next.

# This view is now obsolete, you can safely remove it.
# def market_news_api(request):
#     """
#     API endpoint for market news, using the caching service.
#     """
#     try:
#         news_data = services.get_cached_or_fresh_news()
#         return JsonResponse({"news": news_data})
#     except Exception as e:
#         print(f"API Error in market_news_api: {e}")
#         return JsonResponse({"error": "Could not retrieve market news."}, status=500)