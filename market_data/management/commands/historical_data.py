import os
import time
import hashlib
import requests
import json
from datetime import datetime, timedelta
import pytz

from django.core.management.base import BaseCommand
from fyers_apiv3 import fyersModel
from fundamentals.models import Company
from market_data.models import HistoricalData

# --- Helper Functions for Credentials (largely unchanged) ---
CREDENTIALS_DIR = "credentials"
ACCESS_TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "access_token.txt")
REFRESH_TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "refresh_token.txt")
CLIENT_ID_FILE = os.path.join(CREDENTIALS_DIR, "client_id.txt")
SECRET_KEY_FILE = os.path.join(CREDENTIALS_DIR, "secret_key.txt")
PIN_FILE = os.path.join(CREDENTIALS_DIR, "pin.txt")
FYERS_REFRESH_ENDPOINT = "https://api-t1.fyers.in/api/v3/validate-refresh-token"

# (Include the same credential helper functions: load_file, save_file, etc.)
def load_file(path):
    try:
        with open(path, "r") as f: return f.read().strip()
    except FileNotFoundError:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f: f.write("")
        return ""

# --- Django Management Command ---

class Command(BaseCommand):
    help = 'Fetches and stores historical OHLCV data from Fyers API.'

    def handle(self, *args, **options):
        client_id = load_file(CLIENT_ID_FILE)
        access_token = load_file(ACCESS_TOKEN_FILE)

        if not client_id or not access_token:
            self.stderr.write(self.style.ERROR("Client ID or Access Token not found."))
            return

        fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

        symbols_from_db = Company.objects.values_list('symbol', flat=True)
        timeframes = ["D", "60", "15", "5", "3", "1"] # Daily first, then intraday
        
        indian_tz = pytz.timezone('Asia/Kolkata')

        for symbol in symbols_from_db:
            formatted_symbol = f"NSE:{symbol}-EQ"
            self.stdout.write(self.style.SUCCESS(f"--- Processing symbol: {formatted_symbol} ---"))

            for tf in timeframes:
                self.stdout.write(f"  Fetching timeframe: {tf}")

                # Determine date range based on timeframe
                range_to = datetime.now(indian_tz)
                if tf == "D":
                    range_from = range_to - timedelta(days=200)
                else:
                    range_from = range_to - timedelta(days=100)
                
                data = {
                    "symbol": formatted_symbol,
                    "resolution": tf,
                    "date_format": "1", # Using "1" for epoch timestamp
                    "range_from": range_from.strftime('%Y-%m-%d'),
                    "range_to": range_to.strftime('%Y-%m-%d'),
                    "cont_flag": "1"
                }

                try:
                    response = fyers.history(data=data)

                    if response.get("s") != "ok" or not response.get("candles"):
                        self.stderr.write(self.style.ERROR(f"    Error fetching data for {formatted_symbol} ({tf}): {response.get('message', 'No candles found')}"))
                        continue

                    candles = response["candles"]
                    candles_to_create = []

                    for c in candles:
                        # Convert epoch timestamp to timezone-aware datetime object
                        candle_dt = datetime.fromtimestamp(c[0], tz=indian_tz)

                        # Create a unique ID for each record
                        record_id = f"{formatted_symbol}_{tf}_{c[0]}"

                        # Prepare the object for bulk creation
                        candles_to_create.append(
                            HistoricalData(
                                id=record_id,
                                symbol=formatted_symbol,
                                timeframe=tf,
                                datetime=candle_dt,
                                open=c[1],
                                high=c[2],
                                low=c[3],
                                close=c[4],
                                volume=c[5]
                            )
                        )
                    
                    # Use bulk_create with ignore_conflicts to efficiently insert new data
                    if candles_to_create:
                        HistoricalData.objects.bulk_create(candles_to_create, ignore_conflicts=True)
                        self.stdout.write(self.style.SUCCESS(f"    Successfully saved {len(candles_to_create)} candles for {tf} timeframe."))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"    An exception occurred for {formatted_symbol} ({tf}): {e}"))
                
                # Fyers API has rate limits, a small delay is good practice
                time.sleep(1) 
            
            self.stdout.write(self.style.SUCCESS(f"--- Finished processing symbol: {formatted_symbol} ---\n"))

