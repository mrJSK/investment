from django.db import models

class Screener(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ScreenerCondition(models.Model):
    INDICATORS = [
        ('close', 'Close'),
        ('sma', 'SMA'),
        ('ema', 'EMA'),
        ('rsi', 'RSI'),
        ('macd', 'MACD'),
        ('atr', 'ATR'),
        ('volume', 'Volume'),
    ]
    OPERATORS = [
        ('>', '>'),
        ('<', '<'),
        ('>=', '>='),
        ('<=', '<='),
        ('==', '=='),
    ]
    LOGIC = [('AND', 'AND'), ('OR', 'OR')]

    screener = models.ForeignKey(Screener, related_name='conditions', on_delete=models.CASCADE)
    left_indicator = models.CharField(max_length=20, choices=INDICATORS)
    operator = models.CharField(max_length=3, choices=OPERATORS)
    right_indicator = models.CharField(max_length=20, choices=INDICATORS, blank=True, null=True)
    constant = models.FloatField(blank=True, null=True)
    logic_with_next = models.CharField(max_length=3, choices=LOGIC, blank=True, null=True)

    def __str__(self):
        right = self.right_indicator or self.constant
        return f"{self.left_indicator} {self.operator} {right}"
