# fundamentals/services.py
from django.db.models import Max, Q
from asgiref.sync import sync_to_async # Import sync_to_async
from .models import Company, FundamentalData
from .utils import get_market_cap_category, calculate_fundamental_score
import logging

logger = logging.getLogger(__name__)

class FundamentalService:
    """
    Service class to encapsulate fundamental data retrieval and processing logic.
    This helps in making database operations async-compatible.
    """

    @sync_to_async
    def _get_latest_fundamental_data_sync(self):
        """
        Synchronous helper to fetch the latest fundamental data efficiently.
        """
        # First, get the latest date for each company that has fundamental data
        latest_dates_per_company = FundamentalData.objects.values('company_id').annotate(
            max_date=Max('date')
        )

        # Convert the subquery results into a list of (company_id, max_date) tuples
        latest_fundamental_filters = []
        for item in latest_dates_per_company:
            latest_fundamental_filters.append(Q(company_id=item['company_id']) & Q(date=item['max_date']))

        # Combine all Q objects with OR operator
        query_filter = Q()
        if not latest_fundamental_filters: # Handle case where there's no fundamental data at all
            return FundamentalData.objects.none() # Return empty queryset
            
        for q_obj in latest_fundamental_filters:
            query_filter |= q_obj

        # Fetch the FundamentalData objects corresponding to these latest dates.
        # Use select_related('company') to prefetch the related Company object
        # This avoids N+1 queries when accessing company details.
        latest_fundamentals = FundamentalData.objects.filter(query_filter).select_related('company')
        return list(latest_fundamentals) # Convert to list to avoid async iteration issues


    async def get_categorized_fundamental_companies(self):
        """
        Fetches the latest fundamental data for all companies,
        categorizes them by market cap, calculates a fundamental score,
        and returns top 20 companies per category, split by score (>=9 and <8).
        """
        companies_data = []

        # Call the synchronous helper in an async context
        latest_fundamentals = await self._get_latest_fundamental_data_sync()

        for fd in latest_fundamentals:
            if fd.market_cap is None:
                logger.warning(f"Skipping {fd.company.symbol} due to missing market cap data in its latest fundamental snapshot.")
                continue
                
            category = get_market_cap_category(fd.market_cap)
            score = calculate_fundamental_score(fd) # Pass the FundamentalData instance for scoring
            
            companies_data.append({
                'company_id': fd.company.id,
                'symbol': fd.company.symbol,
                'name': fd.company.name,
                'market_cap': fd.market_cap,
                'category': category,
                'fundamental_score': score,
                'roe': fd.roe,
                'roc': fd.roc,
                'debt_to_equity': fd.debt_to_equity,
                'stock_pe': fd.stock_pe,
                'profit_growth_3_years': fd.profit_growth_3_years,
                'current_price': fd.current_price, # Include current price from FundamentalData
                'high_52_week': fd.high_52_week,
                'low_52_week': fd.low_52_week,
            })

        # Group by category
        categorized_companies = {
            "Large Cap": [],
            "Mid Cap": [],
            "Small Cap": [],
            "Unknown": [], # For companies with missing market cap or unclassified
        }

        for company in companies_data:
            categorized_companies[company['category']].append(company)

        # Sort within each category by score (descending) and get top 20
        final_display_data = {}
        for category, companies in categorized_companies.items():
            companies.sort(key=lambda x: x['fundamental_score'], reverse=True)
            top_20 = companies[:20] # Get top 20 for this category

            # Split into 9+ and <8 scores
            score_9_plus = [c for c in top_20 if c['fundamental_score'] >= 9]
            score_8_below = [c for c in top_20 if c['fundamental_score'] < 8] 

            final_display_data[category] = {
                'score_9_plus': score_9_plus,
                'score_8_below': score_8_below,
            }
            
            logger.info(f"Category '{category}': {len(score_9_plus)} companies (Score 9+), {len(score_8_below)} companies (Score <8) from top 20.")

        return final_display_data

# Instantiate the service class for use in views
fundamental_service = FundamentalService()
