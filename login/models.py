from django.db import models
from django.utils.timezone import now

class Scrip(models.Model):
    symbol = models.CharField(max_length=50, unique=True, db_index=True)
    company_name = models.CharField(max_length=255)

    def __str__(self):
        return self.symbol


class OHLCData(models.Model):
    # Relate each OHLCData entry to a Scrip using ForeignKey
    scrip = models.ForeignKey(Scrip, on_delete=models.CASCADE, related_name="ohlc_data")
    timestamp = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()

    def __str__(self):
        return f"{self.scrip.symbol} - {self.timestamp}"


class OpenTrade(models.Model):
    """
    Model to store details of currently open trades.
    """
    scrip = models.ForeignKey(Scrip, on_delete=models.CASCADE, related_name="open_trades")
    entry_price = models.FloatField()
    entry_time = models.DateTimeField(default=now)
    quantity = models.IntegerField()
    stop_loss_price = models.FloatField(null=True, blank=True)
    position_type = models.CharField(max_length=10, choices=[("LONG", "Long"), ("SHORT", "Short")])

    def __str__(self):
        return f"{self.scrip.symbol} ({self.position_type}) - Entry: {self.entry_price}"


class ClosedTrade(models.Model):
    """
    Model to store details of completed (closed) trades.
    """
    scrip = models.ForeignKey(Scrip, on_delete=models.CASCADE, related_name="closed_trades")
    entry_price = models.FloatField()
    exit_price = models.FloatField()
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField(default=now)
    quantity = models.IntegerField()
    position_type = models.CharField(max_length=10, choices=[("LONG", "Long"), ("SHORT", "Short")])
    profit = models.FloatField()
    strategy = models.CharField(max_length=255, null=True, blank=True)  # Optional: Track the strategy used

    def __str__(self):
        return f"{self.scrip.symbol} ({self.position_type}) - Profit: {self.profit:.2f}"
