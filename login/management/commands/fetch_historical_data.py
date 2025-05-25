import pandas as pd
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from fyers_apiv3 import fyersModel
from login.models import Scrip
from pytz import timezone
from django.db import connection, IntegrityError
import os

ACCESS_TOKEN_FILE = r"credentials\access_token.txt"
CLIENT_ID = "7UFZ1IR3MR-100"

def load_access_token():
    """
    Load the access token from the text file.
    """
    if os.path.exists(ACCESS_TOKEN_FILE):
        with open(ACCESS_TOKEN_FILE, "r") as file:
            return file.read().strip()
    else:
        raise FileNotFoundError(f"Access token file '{ACCESS_TOKEN_FILE}' not found.")

def create_ohlc_table_for_symbol(symbol):
    """Dynamically create a separate OHLC table for a given symbol."""
    table_name = f"ohlc_{symbol.replace(':', '_').replace('-', '_').lower()}"
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    open FLOAT NOT NULL,
                    high FLOAT NOT NULL,
                    low FLOAT NOT NULL,
                    close FLOAT NOT NULL,
                    volume FLOAT NOT NULL,
                    UNIQUE (timestamp)
                );
            """)
            print(f"Table {table_name} created (or already exists).")
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")
            return None # Return None if table creation fails
    return table_name

def fetch_data_from_fyers(symbol, resolution, from_date, to_date):
    """
    Fetch historical data for a given symbol, resolution, and date range.
    """
    from_timestamp = int(from_date.timestamp())
    to_timestamp = int(to_date.timestamp())

    fyers = fyersModel.FyersModel(client_id=CLIENT_ID, token=load_access_token(), is_async=False)

    payload = {
        "symbol": symbol,
        "resolution": resolution,
        "date_format": 0,
        "range_from": from_timestamp,
        "range_to": to_timestamp,
        "cont_flag": "0",
    }

    try:
        response = fyers.history(data=payload)
        if response.get("s") == "ok" and "candles" in response:
            data = pd.DataFrame(response["candles"], columns=["timestamp", "open", "high", "low", "close", "volume"])
            return data
        else:
            print(f"Failed to fetch data for {symbol} at {resolution}: {response.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error fetching data for {symbol} at {resolution}: {e}")
        return None
    
def save_data_to_symbol_table(symbol, data):
    """Save data to the dynamically created table."""

    table_name = create_ohlc_table_for_symbol(symbol) # Create table first

    if table_name is None: # Check if table creation was successful
        print(f"Failed to save data for {symbol} due to table creation error.")
        return

    if data is not None:
        with connection.cursor() as cursor:
            for _, row in data.iterrows():
                try:
                    timestamp = datetime.fromtimestamp(row["timestamp"], tz=timezone("UTC")).astimezone(timezone("Asia/Kolkata"))
                    cursor.execute(f"""
                        INSERT INTO {table_name} (timestamp, open, high, low, close, volume)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (timestamp) DO NOTHING;
                    """, [timestamp, row["open"], row["high"], row["low"], row["close"], row["volume"]])
                except Exception as e:
                    print(f"Error saving data for {symbol} at {timestamp}: {e}")
            print(f"Data saved for {symbol} into table {table_name}")

class Command(BaseCommand):
    help = "Fetch 5-minute interval OHLC data for all symbols in the Scrip model and store in separate tables."

    def handle(self, *args, **kwargs):
        # Fetch symbols from the Scrip model
        symbols = Scrip.objects.values_list("symbol", flat=True)
        if not symbols:
            self.stdout.write(self.style.ERROR("No symbols found in the database."))
            return

        start_date = datetime(2022, 1, 1)
        end_date = datetime.now()
        resolution = "5"

        for symbol in symbols:
            self.stdout.write(f"Processing data for {symbol}...")

            # Create a dedicated table for the symbol
            create_ohlc_table_for_symbol(symbol)

            # Fetch and save new data
            current_start = start_date
            while current_start < end_date:
                current_end = min(current_start + timedelta(days=100), end_date)

                data = fetch_data_from_fyers(symbol, resolution, current_start, current_end)
                if data is not None:
                    save_data_to_symbol_table(symbol, data)
                    self.stdout.write(f"Fetched and saved data for {symbol} from {current_start} to {current_end}.")
                else:
                    self.stdout.write(f"No data fetched for {symbol} from {current_start} to {current_end}.")

                current_start = current_end + timedelta(days=1)
