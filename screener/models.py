from django.db import models

class Scan(models.Model):
    """
    Represents a saved stock scan (screener) with a name, timeframe, and segment.
    The 'timeframe' and 'segment' determine which CSV files and tickers to scan.
    """
    TIMEFRAME_CHOICES = [
        ('15min', '15-Minute'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly')
    ]
    SEGMENT_CHOICES = [
        ('Nifty 50', 'Nifty 50'),
        ('Nifty 100', 'Nifty 100'),
        ('Nifty 500', 'Nifty 500'),
        ('All NSE', 'All NSE'),
        ('Custom', 'Custom')
    ]
    name = models.CharField(max_length=100)
    timeframe = models.CharField(max_length=10, choices=TIMEFRAME_CHOICES, default='daily')
    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES, default='Nifty 50')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.timeframe}, {self.segment})"


class Condition(models.Model):
    """
    A single condition in a scan. It compares left_indicator with right_indicator or a constant.
    The 'logic' field is the connector (AND/OR) to the next condition.
    """
    OPERATORS = [('>', '>'), ('<', '<'), ('>=', '>='), ('<=', '<='), ('==', '==')]
    LOGIC = [('AND', 'AND'), ('OR', 'OR')]

    scan = models.ForeignKey(Scan, related_name='conditions', on_delete=models.CASCADE)
    left_indicator = models.CharField(max_length=50)   # e.g. 'close', 'SMA', 'RSI', 'CDL_HAMMER', etc.
    operator = models.CharField(max_length=2, choices=OPERATORS)
    right_indicator = models.CharField(max_length=50, blank=True, null=True)
    constant = models.FloatField(blank=True, null=True)
    logic = models.CharField(max_length=3, choices=LOGIC, blank=True, null=True)

    def __str__(self):
        # Represent condition textually
        right = self.right_indicator if self.right_indicator else str(self.constant)
        logic = f" {self.logic} ..." if self.logic else ""
        return f"{self.left_indicator} {self.operator} {right}{logic}"
    
    # screener/models.py
from django.db import models

class SavedScan(models.Model):
    """
    Stores a named saved scan. 
    - name: the user‐provided name for the scan
    - filters_json: JSON stringified representation of filter structure
    - segment: which segment dropdown value was active ("Nifty 50", "Nifty 100", etc.)
    - created_at: timestamp for ordering
    """
    name = models.CharField(max_length=100)
    filters_json = models.JSONField()
    segment = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.segment})"

