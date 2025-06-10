# fundamentals/views.py

from django.views.generic import TemplateView
from django.http import JsonResponse
from .models import Company
import logging

# It's good practice to have a logger
logger = logging.getLogger(__name__)

# Helper to convert Decimal to float for JSON serialization
def to_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

class FundamentalsView(TemplateView):
    """Renders the main HTML page."""
    template_name = 'fundamentals/fundamentals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Fundamental Analysis'
        return context

def company_list_api(request):
    """API endpoint to get the list of all companies."""
    try:
        companies = Company.objects.all().order_by('name').values('symbol', 'name')
        return JsonResponse(list(companies), safe=False)
    except Exception as e:
        logger.error(f"Error in company_list_api: {e}")
        return JsonResponse({'error': 'Could not retrieve company list.'}, status=500)

def company_detail_api(request, symbol):
    """
    API endpoint to get detailed data for a single company,
    including a dynamically generated list of industry peers.
    """
    try:
        company = Company.objects.get(symbol__iexact=symbol)

        # --- DYNAMIC PEER GENERATION LOGIC ---
        peers_data = []
        # Check if the company is associated with an industry
        if company.industry_classification:
            # Find other companies in the same industry, excluding the current one.
            # Order by market cap descending to get the most relevant peers.
            # Limit to the top 10 for performance and relevance.
            peers = Company.objects.filter(
                industry_classification=company.industry_classification
            ).exclude(symbol=company.symbol).order_by('-market_cap')[:10]
            
            # Format the peer data for the frontend
            for peer in peers:
                peers_data.append({
                    'symbol': peer.symbol,
                    'Name': peer.name,
                    'CMP': to_float(peer.current_price),
                    'P/E': to_float(peer.stock_pe),
                    'Mar Cap': to_float(peer.market_cap),
                    'Div Yld': to_float(peer.dividend_yield),
                    'ROCE': to_float(peer.roce),
                })
        # --- END OF DYNAMIC PEER LOGIC ---

        data = {
            'symbol': company.symbol,
            'name': company.name,
            'website': company.website,
            'about': company.about,
            'market_cap': to_float(company.market_cap),
            'current_price': to_float(company.current_price),
            'high_low': company.high_low,
            'stock_pe': to_float(company.stock_pe),
            'book_value': to_float(company.book_value),
            'dividend_yield': to_float(company.dividend_yield),
            'roce': to_float(company.roce),
            'roe': to_float(company.roe),
            'face_value': to_float(company.face_value),
            'pros': company.pros,
            'cons': company.cons,
            # This now sends our newly generated list of peers
            'peer_comparison': peers_data,
            'quarterly_results': company.quarterly_results,
            'profit_loss_statement': company.profit_loss_statement,
            'balance_sheet': company.balance_sheet,
            'cash_flow_statement': company.cash_flow_statement,
            'ratios': company.ratios,
            'compounded_sales_growth': company.compounded_sales_growth,
            'compounded_profit_growth': company.compounded_profit_growth,
            'stock_price_cagr': company.stock_price_cagr,
            'return_on_equity': company.return_on_equity,
            'shareholding_pattern': company.shareholding_pattern,
        }
        return JsonResponse(data)

    except Company.DoesNotExist:
        return JsonResponse({'error': f'Company with symbol {symbol} not found.'}, status=404)
    except Exception as e:
        logger.error(f"An unexpected error occurred for symbol {symbol}: {e}")
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)
