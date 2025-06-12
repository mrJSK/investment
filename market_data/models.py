from django.db import models

# Note: The model for the 'fundamentals_company' table should only exist
# in your 'fundamentals' app. We do NOT redefine it here.
# We will import it in other files where it's needed.

class HistoricalData(models.Model):
    """
    Stores all the historical and live OHLCV (Open, High, Low, Close, Volume)
    candle data for all symbols and timeframes.
    """
    id = models.CharField(
        max_length=255, 
        primary_key=True,
        help_text="Unique ID for the candle record, e.g., 'NSE:SBIN-EQ_D_1690934400'."
    )
    
    symbol = models.CharField(
        max_length=100, 
        db_index=True,
        help_text="The full Fyers symbol format, e.g., 'NSE:SBIN-EQ'."
    )
    
    timeframe = models.CharField(
        max_length=10,
        help_text="The timeframe of the candle (e.g., '1', '5', '15', '60', 'D')."
    )
    
    datetime = models.DateTimeField(
        db_index=True,
        help_text="The timezone-aware timestamp for the start of the candle."
    )
    
    open = models.FloatField(help_text="The opening price of the candle.")
    high = models.FloatField(help_text="The highest price of the candle.")
    low = models.FloatField(help_text="The lowest price of the candle.")
    close = models.FloatField(help_text="The closing price of the candle.")
    volume = models.BigIntegerField(help_text="The volume traded during the candle's duration.")

    class Meta:
        unique_together = ('symbol', 'timeframe', 'datetime')
        verbose_name = "Historical Candle"
        verbose_name_plural = "Historical Data"
        db_table = 'historical_ohlcv'

    def __str__(self):
        return f"{self.symbol} ({self.timeframe}) - {self.datetime.strftime('%Y-%m-%d %H:%M')}"
