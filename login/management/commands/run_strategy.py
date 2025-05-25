from django.core.management.base import BaseCommand
from ...models import OHLCData, OpenTrade, ClosedTrade, Scrip
from ta.trend import EMAIndicator
from fyers_apiv3 import fyersModel
from datetime import datetime, timedelta
from pytz import timezone
import pandas as pd
import numpy as np
import time


class Command(BaseCommand):
    help = "Run EMA-based strategy continuously during market hours, aggregate tick data, and place orders."

    tick_data = {}  # Store tick data temporarily for each symbol
    last_aggregation_time = datetime.now(timezone("Asia/Kolkata"))

    def handle(self, *args, **options):
        # Load credentials
        self.access_token = self.load_access_token()
        self.client_id = self.load_client_id()

        # Initialize Fyers API
        self.fyers = fyersModel.FyersModel(client_id=self.client_id, token=self.access_token, is_async=False)

        self.stdout.write("Running strategy...")

        try:
            while self.is_market_open():
                symbols = list(Scrip.objects.values_list("symbol", flat=True))
                for symbol in symbols:
                    self.stdout.write(f"Processing {symbol}...")
                    self.aggregate_tick_data(symbol)  # Aggregate tick data
                    self.run_strategy(symbol)  # Run strategy after aggregation
                time.sleep(5)  # Wait 5 seconds before re-checking
        except KeyboardInterrupt:
            self.stdout.write("Stopping strategy.")
        except Exception as e:
            self.stderr.write(f"Error: {str(e)}")

    def aggregate_tick_data(self, symbol):
        """
        Aggregate tick data into 5-minute OHLCV and store it in the database.
        """
        now = datetime.now(timezone("Asia/Kolkata"))
        if now - self.last_aggregation_time >= timedelta(minutes=5):  # Aggregate every 5 minutes
            self.stdout.write(f"Aggregating tick data for {symbol}...")

            if symbol in self.tick_data and self.tick_data[symbol]:
                # Convert tick data to DataFrame
                df = pd.DataFrame(self.tick_data[symbol])

                # Aggregate OHLCV
                ohlc = {
                    "open": df["ltp"].iloc[0],
                    "high": df["ltp"].max(),
                    "low": df["ltp"].min(),
                    "close": df["ltp"].iloc[-1],
                    "volume": df["volume"].sum(),
                }

                # Use the last tick's timestamp for the aggregation
                aggregation_time = df["timestamp"].iloc[-1]
                self.store_ohlcv(symbol, ohlc, aggregation_time)

                # Clear tick data
                self.tick_data[symbol] = []

            self.last_aggregation_time = now

    def store_ohlcv(self, symbol, ohlc, aggregation_time):
        """
        Store aggregated OHLCV data in the database.
        """
        scrip = Scrip.objects.filter(symbol=symbol).first()
        if not scrip:
            self.stderr.write(f"Symbol {symbol} not found in the Scrip table.")
            return

        OHLCData.objects.update_or_create(
            scrip=scrip,
            timestamp=aggregation_time,
            defaults={
                "open": ohlc["open"],
                "high": ohlc["high"],
                "low": ohlc["low"],
                "close": ohlc["close"],
                "volume": ohlc["volume"],
            },
        )
        self.stdout.write(f"OHLCV data stored for {symbol} at {aggregation_time}.")

    def run_strategy(self, symbol, ema_short_length=9, ema_long_length=26, swing_length=5, stop_loss_pct=1.0):
        """
        Run EMA-based trading strategy with swing high/low, stop loss, and trade tracking.
        """
        # Fetch historical OHLC data for the symbol
        historical_data = list(
            OHLCData.objects.filter(scrip__symbol=symbol)
            .order_by("timestamp")
            .values("timestamp", "open", "high", "low", "close")
        )

        if not historical_data:
            self.stdout.write(f"No historical data available for {symbol}.")
            return

        df = pd.DataFrame(historical_data)

        # Ensure there is enough data for EMA calculation
        if len(df) < max(ema_short_length, ema_long_length):
            self.stdout.write(f"Not enough data to calculate EMA for {symbol}.")
            return

        # Calculate EMAs
        df["ema_short"] = EMAIndicator(df["close"], window=ema_short_length).ema_indicator()
        df["ema_long"] = EMAIndicator(df["close"], window=ema_long_length).ema_indicator()

        # Identify swing highs and lows
        df["swing_high"] = df["close"][
            df["close"] == df["close"].rolling(swing_length, center=True).max()
        ]
        df["swing_low"] = df["close"][
            df["close"] == df["close"].rolling(swing_length, center=True).min()
        ]

        # Generate signals
        df["signal"] = 0
        df["signal"] = np.where(
            (df["ema_short"] > df["ema_long"]) & (df["swing_low"].notnull()), 1, df["signal"]
        )
        df["signal"] = np.where(
            (df["ema_short"] < df["ema_long"]) & (df["swing_high"].notnull()), -1, df["signal"]
        )

        # Fetch the most recent signal
        latest_signal = df.iloc[-1]["signal"]
        ohlc = df.iloc[-1].to_dict()

        if latest_signal == 0:
            self.stdout.write(f"Waiting for signal on {symbol}...")  # Prompt to show waiting
        else:
            # Handle trade logic and place orders
            self.manage_trade(symbol, latest_signal, ohlc, stop_loss_pct)

    def manage_trade(self, symbol, latest_signal, ohlc, stop_loss_pct):
        """
        Manage open trades based on the latest signal and OHLC data.
        """
        open_trade = OpenTrade.objects.filter(scrip__symbol=symbol).first()

        if open_trade is None:  # No open trade, check for entry signals
            if latest_signal == 1:  # Long entry
                self.stdout.write(f"Buy signal generated for {symbol}.")
                self.place_order(symbol, "BUY", ohlc["close"], stop_loss_pct)
            elif latest_signal == -1:  # Short entry
                self.stdout.write(f"Sell signal generated for {symbol}.")
                self.place_order(symbol, "SELL", ohlc["close"], stop_loss_pct)

        elif open_trade:  # Open trade exists, check for exit or reversal signals
            if open_trade.position_type == "LONG":
                if ohlc["low"] <= open_trade.stop_loss_price or latest_signal == -1:
                    self.close_trade(open_trade, ohlc["low"], "SELL")
            elif open_trade.position_type == "SHORT":
                if ohlc["high"] >= open_trade.stop_loss_price or latest_signal == 1:
                    self.close_trade(open_trade, ohlc["high"], "BUY")

    def place_order(self, symbol, side, price, stop_loss_pct):
        """
        Place an order using the Fyers API and update the database.
        """
        scrip = Scrip.objects.get(symbol=symbol)
        qty = 1  # Quantity can be adjusted dynamically

        # Place the order via Fyers API
        response = self.fyers.place_order(data={
            "symbol": symbol,
            "qty": qty,
            "type": 2,  # Market order
            "side": 1 if side == "BUY" else -1,
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": "False",
        })

        if response.get("code") == 200:
            entry_price = price
            stop_loss_price = (
                entry_price * (1 - stop_loss_pct / 100) if side == "BUY" else entry_price * (1 + stop_loss_pct / 100)
            )

            OpenTrade.objects.create(
                scrip=scrip,
                entry_price=entry_price,
                entry_time=datetime.now(),
                quantity=qty,
                stop_loss_price=stop_loss_price,
                position_type="LONG" if side == "BUY" else "SHORT",
            )
            self.stdout.write(f"{side} order placed for {symbol} at {entry_price} for {qty} qty.")
        else:
            self.stderr.write(f"Failed to place {side} order for {symbol}. Response: {response}")

    def close_trade(self, open_trade, exit_price, side):
        """
        Close an open trade and log it in the ClosedTrade table.
        """
        profit = (
            (exit_price - open_trade.entry_price) * open_trade.quantity
            if open_trade.position_type == "LONG"
            else (open_trade.entry_price - exit_price) * open_trade.quantity
        )

        ClosedTrade.objects.create(
            scrip=open_trade.scrip,
            entry_price=open_trade.entry_price,
            exit_price=exit_price,
            entry_time=open_trade.entry_time,
            exit_time=datetime.now(),
            quantity=open_trade.quantity,
            position_type=open_trade.position_type,
            profit=profit,
            strategy="EMA Crossover",
        )
        open_trade.delete()
        self.stdout.write(f"Trade closed for {open_trade.scrip.symbol}. Profit: {profit}")

    def is_market_open(self):
        """
        Check if the market is open based on the current time.
        """
        now = datetime.now(timezone("Asia/Kolkata"))
        market_open = now.replace(hour=9, minute=10, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=40, second=0, microsecond=0)
        return market_open <= now <= market_close

    def load_access_token(self):
        """
        Load the access token from a file.
        """
        access_token_path = "credentials/access_token.txt"
        if not access_token_path:
            raise FileNotFoundError("Access token file not found.")
        with open(access_token_path, "r") as file:
            return file.read().strip()

    def load_client_id(self):
        """
        Load the client ID from a file.
        """
        client_id_path = "credentials/client_id.txt"
        if not client_id_path:
            raise FileNotFoundError("Client ID file not found.")
        with open(client_id_path, "r") as file:
            return file.read().strip()
