# fundamentals/views.py

from django.views.generic import TemplateView
from django.http import JsonResponse
from .models import Company, IndustryClassification
import logging
import json
import decimal
from django.db.models import Q, F

logger = logging.getLogger(__name__)

# Helper to convert Decimal to float for JSON serialization
def to_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError, decimal.InvalidOperation):
        return None

# Helper function to safely get value from JSONField, handling potential errors
def get_json_value(json_field, key):
    if json_field and isinstance(json_field, dict):
        value_str = json_field.get(key)
        if value_str is not None: # Check if key exists (even if value is empty string)
            value_str = value_str.replace('%', '').strip()
            if value_str == '': # Handle explicit empty string case
                return None # Treat empty string as None
            try:
                return decimal.Decimal(value_str)
            except (decimal.InvalidOperation, TypeError, ValueError):
                logger.warning(f"Could not convert JSON value '{value_str}' for key '{key}' to Decimal.")
                return None
    return None

class FundamentalsView(TemplateView):
    template_name = 'fundamentals/fundamentals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Fundamental Analysis Dashboard'
        context['industries'] = IndustryClassification.objects.all().order_by('name')
        return context

class CustomScreenerView(TemplateView):
    template_name = 'fundamentals/custom_screener.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Advanced Company Screener'
        context['industries'] = IndustryClassification.objects.all().order_by('name')
        return context


def company_list_api(request):
    try:
        companies = Company.objects.all().order_by('name').values('symbol', 'name')
        return JsonResponse(list(companies), safe=False)
    except Exception as e:
        logger.error(f"Error in company_list_api: {e}")
        return JsonResponse({'error': 'Could not retrieve company list.'}, status=500)

def market_cap_api(request):
    """
    Categorizes all companies into large, mid, and small cap.
    """
    try:
        companies = Company.objects.all().order_by('-market_cap')
        large_cap_threshold = 100000
        mid_cap_threshold = 10000

        large_caps, mid_caps, small_caps = [], [], []

        for company in companies:
            market_cap = company.market_cap if company.market_cap is not None else decimal.Decimal(0)
            company_data = {'symbol': company.symbol, 'name': company.name, 'market_cap': to_float(market_cap)}

            if market_cap > large_cap_threshold:
                large_caps.append(company_data)
            elif mid_cap_threshold < market_cap <= large_cap_threshold:
                mid_caps.append(company_data)
            else:
                small_caps.append(company_data)

        return JsonResponse({
            'large_caps': large_caps, 'mid_caps': mid_caps, 'small_caps': small_caps
        }, safe=False)
        
    except Exception as e:
        logger.error(f"Error in market_cap_api: {e}")
        return JsonResponse({'error': 'Could not retrieve market cap data.'}, status=500)


def company_detail_api(request, symbol):
    try:
        company = Company.objects.get(symbol__iexact=symbol)
        
        peers_data = []
        if company.industry_classification:
            peers = Company.objects.filter(
                industry_classification=company.industry_classification
            ).exclude(symbol=company.symbol).order_by('-market_cap')[:10]
            for peer in peers:
                peers_data.append({
                    'symbol': peer.symbol, 'Name': peer.name, 'CMP': to_float(peer.current_price),
                    'P/E': to_float(peer.stock_pe), 'Mar Cap': to_float(peer.market_cap),
                    'Div Yld': to_float(peer.dividend_yield), 'ROCE': to_float(peer.roce),
                })

        data = {
            'symbol': company.symbol, 'name': company.name, 'website': company.website,
            'about': company.about, 'market_cap': to_float(company.market_cap),
            'current_price': to_float(company.current_price), 'high_low': company.high_low,
            'stock_pe': to_float(company.stock_pe), 'book_value': to_float(company.book_value),
            'dividend_yield': to_float(company.dividend_yield), 'roce': to_float(company.roce),
            'roe': to_float(company.roe), 'face_value': to_float(company.face_value),
            'peer_comparison': peers_data, 'quarterly_results': company.quarterly_results,
            'profit_loss_statement': company.profit_loss_statement, 'balance_sheet': company.balance_sheet,
            'cash_flow_statement': company.cash_flow_statement, 'ratios': company.ratios,
            'compounded_sales_growth': company.compounded_sales_growth,
            'compounded_profit_growth': company.compounded_profit_growth,
            'stock_price_cagr': company.stock_price_cagr, 'return_on_equity': company.return_on_equity,
            'shareholding_pattern': company.shareholding_pattern,
            'pros': company.pros or [],
            'cons': company.cons or []
        }
        
        return JsonResponse(data)

    except Company.DoesNotExist:
        return JsonResponse({'error': f'Company with symbol {symbol} not found.'}, status=404)
    except Exception as e:
        logger.error(f"An unexpected error occurred for symbol {symbol}: {e}")
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)


def strong_companies_market_cap_api(request):
    """
    Returns a list of fundamentally strong companies, categorized by market cap.
    Applies default strong/undervalued filters.
    """
    filters = Q()

    filters &= Q(roce__gte=decimal.Decimal(15))
    filters &= Q(roe__gte=decimal.Decimal(15))
    filters &= Q(stock_pe__lte=decimal.Decimal(20))
    filters &= Q(market_cap__isnull=False)

    companies_queryset = Company.objects.filter(filters).order_by('name')

    strong_companies_categorized = []
    large_cap_threshold = decimal.Decimal(100000)
    mid_cap_threshold = decimal.Decimal(10000)

    for company in companies_queryset:
        price_to_book = None
        if company.current_price is not None and company.book_value is not None and company.book_value != 0:
            try:
                price_to_book = company.current_price / company.book_value
            except decimal.InvalidOperation:
                pass
        
        if price_to_book is None or price_to_book > decimal.Decimal(3):
            continue

        profit_growth_5yr_val = get_json_value(company.compounded_profit_growth, '5 Years')
        if profit_growth_5yr_val is None or profit_growth_5yr_val < decimal.Decimal(10):
            continue

        market_cap_category = "Small Cap"
        if company.market_cap >= large_cap_threshold:
            market_cap_category = "Large Cap"
        elif company.market_cap >= mid_cap_threshold:
            market_cap_category = "Mid Cap"

        strong_companies_categorized.append({
            'name': company.name,
            'symbol': company.symbol,
            'market_cap': to_float(company.market_cap),
            'current_price': to_float(company.current_price),
            'stock_pe': to_float(company.stock_pe),
            'book_value': to_float(company.book_value),
            'price_to_book': to_float(price_to_book),
            'dividend_yield': to_float(company.dividend_yield),
            'roce': to_float(company.roce),
            'roe': to_float(company.roe),
            'compounded_profit_growth_5yr': to_float(profit_growth_5yr_val),
            'industry': company.industry_classification.name if company.industry_classification else 'N/A',
            'market_cap_category': market_cap_category,
        })

    strong_companies_categorized.sort(key=lambda x: (
        {'Large Cap': 0, 'Mid Cap': 1, 'Small Cap': 2}.get(x['market_cap_category'], 3),
        x['market_cap'] if x['market_cap'] is not None else float('-inf')
    ), reverse=True)

    return JsonResponse(strong_companies_categorized, safe=False)


# NEW API endpoint for Undervalued Stocks
def undervalued_companies_api(request):
    """
    Returns a list of companies identified as undervalued based on default criteria.
    """
    filters = Q()

    # Default "Undervalued" criteria
    filters &= Q(stock_pe__lte=decimal.Decimal(15)) # Lower P/E
    filters &= Q(dividend_yield__gte=decimal.Decimal(1.0)) # Decent dividend yield
    filters &= Q(market_cap__isnull=False) # Ensure market cap exists for basic context

    companies_queryset = Company.objects.filter(filters).order_by('name')

    undervalued_list = []
    for company in companies_queryset:
        price_to_book = None
        if company.current_price is not None and company.book_value is not None and company.book_value != 0:
            try:
                price_to_book = company.current_price / company.book_value
            except decimal.InvalidOperation:
                pass
        
        # Apply Price to Book filter for Undervalued
        if price_to_book is None or price_to_book > decimal.Decimal(2): # P/B < 2
            continue

        undervalued_list.append({
            'name': company.name,
            'symbol': company.symbol,
            'market_cap': to_float(company.market_cap),
            'current_price': to_float(company.current_price),
            'stock_pe': to_float(company.stock_pe),
            'book_value': to_float(company.book_value),
            'price_to_book': to_float(price_to_book),
            'dividend_yield': to_float(company.dividend_yield),
            'roce': to_float(company.roce), # Include for context
            'roe': to_float(company.roe),   # Include for context
            'industry': company.industry_classification.name if company.industry_classification else 'N/A',
        })
    
    # Sort by P/E ascending for undervalued stocks
    undervalued_list.sort(key=lambda x: x['stock_pe'] if x['stock_pe'] is not None else float('inf'))

    return JsonResponse(undervalued_list, safe=False)


# Consolidating the comprehensive screener API into fundamentals/views.py
def fundamental_screener_api(request):
    """
    API endpoint to filter companies based on user-defined fundamental criteria.
    This is for the dedicated custom screener page within the fundamentals app.
    """
    filters = Q()

    min_roce_str = request.GET.get('min_roce')
    if min_roce_str:
        try:
            min_roce_val = decimal.Decimal(min_roce_str)
            filters &= Q(roce__gte=min_roce_val)
        except decimal.InvalidOperation:
            pass

    min_roe_str = request.GET.get('min_roe')
    if min_roe_str:
        try:
            min_roe_val = decimal.Decimal(min_roe_str)
            filters &= Q(roe__gte=min_roe_val)
        except decimal.InvalidOperation:
            pass

    max_pe_str = request.GET.get('max_pe')
    if max_pe_str:
        try:
            max_pe_val = decimal.Decimal(max_pe_str)
            filters &= Q(stock_pe__lte=max_pe_val)
        except decimal.InvalidOperation:
            pass
    
    industry_id = request.GET.get('industry')
    if industry_id:
        try:
            filters &= Q(industry_classification__id=int(industry_id))
        except ValueError:
            pass

    companies_queryset = Company.objects.filter(filters).order_by('symbol')

    results = []
    for company in companies_queryset:
        price_to_book = None
        if company.current_price is not None and company.book_value is not None and company.book_value != 0:
            try:
                price_to_book = company.current_price / company.book_value
            except decimal.InvalidOperation:
                pass
        
        max_pb_str = request.GET.get('max_pb')
        if max_pb_str:
            try:
                max_pb_val = decimal.Decimal(max_pb_str)
                if price_to_book is None or price_to_book > max_pb_val:
                    continue
            except decimal.InvalidOperation:
                pass

        profit_growth_5yr_val = get_json_value(company.compounded_profit_growth, '5 Years')
        min_profit_growth_5yr_str = request.GET.get('min_profit_growth_5yr')
        if min_profit_growth_5yr_str:
            try:
                min_profit_growth_5yr_val_dec = decimal.Decimal(min_profit_growth_5yr_str)
                if profit_growth_5yr_val is None or profit_growth_5yr_val < min_profit_growth_5yr_val_dec:
                    continue
            except decimal.InvalidOperation:
                pass

        results.append({
            'name': company.name,
            'symbol': company.symbol,
            'market_cap': to_float(company.market_cap),
            'current_price': to_float(company.current_price),
            'stock_pe': to_float(company.stock_pe),
            'book_value': to_float(company.book_value),
            'price_to_book': to_float(price_to_book),
            'dividend_yield': to_float(company.dividend_yield),
            'roce': to_float(company.roce),
            'roe': to_float(company.roe),
            'compounded_profit_growth_5yr': to_float(profit_growth_5yr_val),
            'industry': company.industry_classification.name if company.industry_classification else 'N/A',
        })
    
    sort_by = request.GET.get('sort_by')
    order = request.GET.get('order', 'asc')

    if sort_by:
        sortable_fields = {
            'name': 'name', 'symbol': 'symbol', 'market_cap': 'market_cap',
            'current_price': 'current_price', 'stock_pe': 'stock_pe',
            'book_value': 'book_value', 'price_to_book': 'price_to_book',
            'dividend_yield': 'dividend_yield', 'roce': 'roce', 'roe': 'roe',
            'compounded_profit_growth_5yr': 'compounded_profit_growth_5yr',
        }
        
        if sort_by in sortable_fields:
            if order == 'asc':
                results.sort(key=lambda x: x.get(sortable_fields[sort_by]) if x.get(sortable_fields[sort_by]) is not None else float('inf'))
            else:
                results.sort(key=lambda x: x.get(sortable_fields[sort_by]) if x.get(sortable_fields[sort_by]) is not None else float('-inf'), reverse=True)
                
    return JsonResponse(results, safe=False)