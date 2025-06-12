from django.db import models
import uuid

class FinancialReport(models.Model):
    """
    Stores the structured financial data from a single Annual XBRL report.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=255)
    report_date = models.DateField()
    structured_data = models.JSONField()
    source_url = models.URLField(max_length=1000, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.report_date}"

    class Meta:
        ordering = ['-report_date', 'company_name']
        verbose_name = "Annual Financial Report"
        verbose_name_plural = "Annual Financial Reports"


class NewsArticle(models.Model):
    """
    Stores a single news article scraped from a source.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    headline = models.CharField(max_length=1000)
    link = models.URLField(max_length=1000, unique=True, db_index=True)
    source = models.CharField(max_length=100, default="CNBCTV18")
    publication_time_str = models.CharField(max_length=50, blank=True)
    full_text = models.TextField()
    sentiment = models.CharField(max_length=10, default="Neutral")
    confidence = models.FloatField(default=0.0)
    action = models.CharField(max_length=10, default="Hold")
    is_stocks_to_watch = models.BooleanField(default=False)
    scraped_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.headline

    class Meta:
        ordering = ['-updated_at']


class StockInFocus(models.Model):
    """
    Stores an individual stock snippet from a "Stocks to Watch" article.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(NewsArticle, related_name='stocks_in_focus', on_delete=models.CASCADE)
    stock_name = models.CharField(max_length=500, db_index=True)
    text = models.TextField()
    sentiment = models.CharField(max_length=10, default="Neutral")
    confidence = models.FloatField(default=0.0)
    action = models.CharField(max_length=10, default="Hold")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stock_name} in {self.article.headline}"

    class Meta:
        ordering = ['-updated_at']
        verbose_name_plural = "Stocks in Focus"


class ImportantAnnouncement(models.Model):
    """
    Stores high-priority corporate announcements (but is now superseded by the
    more detailed CorporateAction model for many use cases).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=500, db_index=True)
    link = models.URLField(max_length=1000, unique=True, db_index=True)
    category = models.CharField(max_length=500)
    description = models.TextField()
    publication_date_str = models.CharField(max_length=100)
    priority = models.IntegerField(default=99, db_index=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.priority}] {self.company_name}: {self.category}"

    class Meta:
        ordering = ['-scraped_at']


class QuarterlyFinancials(models.Model):
    """
    Stores the structured financial data from a single Quarterly XBRL report.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=50, db_index=True)
    company_name = models.CharField(max_length=255)
    period_end_date = models.DateField(db_index=True)
    structured_data = models.JSONField()
    source_url = models.URLField(max_length=1000, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} ({self.symbol}) - Qtr ending {self.period_end_date}"

    class Meta:
        ordering = ['-period_end_date', 'company_name']
        verbose_name_plural = "Quarterly Financials"

class CorporateAction(models.Model):
    """
    Stores all critical, price-sensitive corporate announcements, including
    new orders, contracts, and financial actions like dividends and splits.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=500, db_index=True)
    link = models.URLField(max_length=1000, db_index=True)
    category = models.CharField(max_length=50, default="Operational") # Operational vs Financial
    action_type = models.CharField(max_length=100) # e.g., "Order / Contract", "Dividend"
    subject = models.TextField() # Changed to TextField for safety
    description = models.TextField(blank=True)
    ex_date = models.DateField(null=True, blank=True, db_index=True)
    record_date = models.DateField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.action_type}] {self.company_name}"

    class Meta:
        ordering = ['-scraped_at']
        verbose_name = "Corporate Action"
        verbose_name_plural = "Corporate Actions"
        unique_together = ('link', 'subject')

