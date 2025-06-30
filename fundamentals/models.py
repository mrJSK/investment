# fundamentals/models.py
from django.db import models

class IndustryClassification(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_industries')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Industry Classifications"

class Company(models.Model):
    name = models.CharField(max_length=255)
    # CORRECTED: Added primary_key=True to the symbol field
    symbol = models.CharField(max_length=50, unique=True, primary_key=True)
    about = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    bse_code = models.CharField(max_length=20, blank=True, null=True)
    nse_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Financial metrics - using DecimalField for precision
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    high_low = models.CharField(max_length=50, blank=True, null=True) # Max/Min price over a period
    stock_pe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    book_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dividend_yield = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    roce = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Return on Capital Employed
    roe = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Return on Equity
    face_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Pros and Cons (JSON data from scraping)
    pros = models.JSONField(null=True, blank=True)
    cons = models.JSONField(null=True, blank=True)
    
    # Peer Comparison (complex JSON structure)
    peer_comparison = models.JSONField(null=True, blank=True)
    
    # Quarterly Results, P&L, Balance Sheet, Cash Flow (complex JSON structures)
    quarterly_results = models.JSONField(null=True, blank=True)
    profit_loss_statement = models.JSONField(null=True, blank=True)
    balance_sheet = models.JSONField(null=True, blank=True)
    cash_flow_statement = models.JSONField(null=True, blank=True)
    ratios = models.JSONField(null=True, blank=True)

    # Compounded Growth and Return on Equity (JSON strings with periods like "3 Years", "5 Years")
    compounded_sales_growth = models.JSONField(null=True, blank=True)
    compounded_profit_growth = models.JSONField(null=True, blank=True)
    stock_price_cagr = models.JSONField(null=True, blank=True)
    return_on_equity = models.JSONField(null=True, blank=True)
    
    shareholding_pattern = models.JSONField(null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Foreign key to IndustryClassification
    industry_classification = models.ForeignKey(
        IndustryClassification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='companies'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"
        # ordering = ['name'] # You had this in a previous version, keep if desired