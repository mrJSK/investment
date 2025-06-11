# fundamentals/views.py

from django.views.generic import TemplateView
from django.http import JsonResponse
from .models import Company
import logging
import json
import requests # Used to make API calls

logger = logging.getLogger(__name__)

# Helper to convert Decimal to float for JSON serialization
def to_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def generate_analysis_with_ai(company_data):
    """
    Generates Pros and Cons from a local deepseek model using the /api/generate endpoint.
    On failure, it returns (None, None) to signal that a fallback is needed.
    """
    local_api_url = "http://localhost:11434/api/generate"
    full_dataset_json = json.dumps(company_data, indent=2)

    prompt = f"""
    You are an expert financial analyst. Your task is to perform a deep-dive analysis on the following company based on its complete financial dataset, presented in JSON format.

    **Complete Company Dataset:**
    ```json
    {full_dataset_json}
    ```

    **Instructions:**
    1.  Thoroughly analyze all provided data points.
    2.  Synthesize the most critical strengths (Pros) and weaknesses/risks (Cons).
    3.  Generate 3-5 key pros and 3-5 key cons. Each pro and con should be a string.
    4.  Return your final analysis ONLY in a valid JSON format with two keys: "pros" and "cons".
        Example: {{"pros": ["Good growth", "Low debt"], "cons": ["High P/E", "Low promoter holding"]}}
    """
    
    payload = {
        "model": "deepseek-coder:6.7b-instruct",
        "prompt": prompt, "stream": False, "format": "json" 
    }

    try:
        response = requests.post(local_api_url, json=payload, timeout=90)
        response.raise_for_status() 

        response_data = response.json()
        analysis_content_string = response_data.get('response')

        if not analysis_content_string:
            logger.error(f"AI response for {company_data.get('symbol')} was empty.")
            return None, None

        analysis = json.loads(analysis_content_string)
        
        if isinstance(analysis, dict) and 'pros' in analysis and 'cons' in analysis:
            logger.info(f"Successfully generated and parsed AI analysis for {company_data.get('symbol')}.")
            return analysis['pros'], analysis['cons']
        else:
            logger.warning(f"AI response for {company_data.get('symbol')} had an invalid JSON structure: {analysis_content_string}")
            return None, None

    except requests.exceptions.RequestException as e:
        logger.error(f"Could not connect to local AI model at {local_api_url}: {e}")
        return None, None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from AI response for {company_data.get('symbol')}: {e}\nRaw response: {analysis_content_string}")
        return None, None
    except (KeyError, IndexError) as e:
        logger.error(f"Error processing AI response structure for {company_data.get('symbol')}: {e}")
        return None, None

class FundamentalsView(TemplateView):
    template_name = 'fundamentals/fundamentals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Fundamental Analysis'
        return context

# API for the main sidebar's company list (flat list)
def company_list_api(request):
    try:
        companies = Company.objects.all().order_by('name').values('symbol', 'name')
        return JsonResponse(list(companies), safe=False)
    except Exception as e:
        logger.error(f"Error in company_list_api: {e}")
        return JsonResponse({'error': 'Could not retrieve company list.'}, status=500)

# API endpoint to provide categorized data for the new market cap tab
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
            market_cap = company.market_cap if company.market_cap is not None else 0
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
        }
        
        generated_pros, generated_cons = generate_analysis_with_ai(data)
        
        if generated_pros is not None and generated_cons is not None:
            data['pros'], data['cons'] = generated_pros, generated_cons
            company.pros, company.cons = generated_pros, generated_cons
            company.save(update_fields=['pros', 'cons'])
        else:
            data['pros'] = company.pros or []
            data['cons'] = company.cons or []

        return JsonResponse(data)

    except Company.DoesNotExist:
        return JsonResponse({'error': f'Company with symbol {symbol} not found.'}, status=404)
    except Exception as e:
        logger.error(f"An unexpected error occurred for symbol {symbol}: {e}")
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)
