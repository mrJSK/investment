# # fundamentals/models.py

# from django.db import models

# class Company(models.Model):
#     # Core Info
#     name = models.CharField(max_length=255)
#     symbol = models.CharField(max_length=100, unique=True, primary_key=True)
#     about = models.TextField(null=True, blank=True)
#     website = models.URLField(null=True, blank=True)

#     # Key Ratios
#     market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
#     current_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
#     high_low = models.CharField(max_length=100, null=True, blank=True)
#     stock_pe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     book_value = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
#     dividend_yield = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     roce = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     roe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     face_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

#     # Ensure this field is added
#     industry_classification = models.CharField(max_length=500, null=True, blank=True, db_index=True)

#     # Analysis
#     pros = models.JSONField(default=list, null=True, blank=True)
#     cons = models.JSONField(default=list, null=True, blank=True)

#     # Financial Data Tables (as JSON)
#     peer_comparison = models.JSONField(default=list, null=True, blank=True)
#     quarterly_results = models.JSONField(default=list, null=True, blank=True)
#     profit_loss_statement = models.JSONField(default=list, null=True, blank=True)
#     balance_sheet = models.JSONField(default=list, null=True, blank=True)
#     cash_flow_statement = models.JSONField(default=list, null=True, blank=True)
#     ratios = models.JSONField(default=list, null=True, blank=True)

#     # Growth Tables & Shareholding (as JSON)
#     compounded_sales_growth = models.JSONField(default=dict, null=True, blank=True)
#     compounded_profit_growth = models.JSONField(default=dict, null=True, blank=True)
#     stock_price_cagr = models.JSONField(default=dict, null=True, blank=True)
#     return_on_equity = models.JSONField(default=dict, null=True, blank=True)
#     shareholding_pattern = models.JSONField(default=dict, null=True, blank=True)

#     # Timestamps
#     last_updated = models.DateTimeField(auto_now=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name} ({self.symbol})"

#     class Meta:
#         verbose_name_plural = "Companies"
#         ordering = ['name']

# fundamentals/models.py

from django.db import models

class IndustryClassification(models.Model):
    """
    Stores industry classifications in a hierarchical structure.
    e.g., 'Industrial Minerals' -> 'Minerals & Mining' -> 'Commodities'
    """
    name = models.CharField(max_length=255)
    # Self-referencing key to create the parent-child tree structure.
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = "Industry Classifications"
        # Ensures no duplicate categories under the same parent.
        unique_together = ('name', 'parent') 

    def __str__(self):
        """
        Builds the full breadcrumb path for display in the Django admin.
        e.g., "Commodities > Metals & Mining > Industrial Minerals"
        """
        path = [self.name]
        p = self.parent
        while p:
            path.insert(0, p.name)
            p = p.parent
        return ' > '.join(path)

class Company(models.Model):
    # Core Info
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=100, unique=True, primary_key=True)
    about = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    bse_code = models.CharField(max_length=50, null=True, blank=True)
    nse_code = models.CharField(max_length=50, null=True, blank=True)

    # Key Ratios
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    high_low = models.CharField(max_length=100, null=True, blank=True)
    stock_pe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    book_value = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    dividend_yield = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    roce = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    roe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    face_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Links each company to its most specific industry category.
    industry_classification = models.ForeignKey(
        IndustryClassification, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    # Analysis
    pros = models.JSONField(default=list, null=True, blank=True)
    cons = models.JSONField(default=list, null=True, blank=True)

    # Financial Data Tables (as JSON)
    peer_comparison = models.JSONField(default=list, null=True, blank=True)
    quarterly_results = models.JSONField(default=list, null=True, blank=True)
    profit_loss_statement = models.JSONField(default=list, null=True, blank=True)
    balance_sheet = models.JSONField(default=list, null=True, blank=True)
    cash_flow_statement = models.JSONField(default=list, null=True, blank=True)
    ratios = models.JSONField(default=list, null=True, blank=True)

    # Growth Tables & Shareholding (as JSON)
    compounded_sales_growth = models.JSONField(default=dict, null=True, blank=True)
    compounded_profit_growth = models.JSONField(default=dict, null=True, blank=True)
    stock_price_cagr = models.JSONField(default=dict, null=True, blank=True)
    return_on_equity = models.JSONField(default=dict, null=True, blank=True)
    shareholding_pattern = models.JSONField(default=dict, null=True, blank=True)

    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']