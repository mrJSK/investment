import pandas as pd
from fyers_apiv3 import fyersModel
from datetime import datetime, timedelta
import os

# Constants
ACCESS_TOKEN_FILE = "credentials\\access_token.txt"  # Path to access token file
CLIENT_ID = "7UFZ1IR3MR-100"  # Replace with your client ID


SYMBOLS = ["NSE:NIFTYBANK-INDEX",
            "NSE:BANKNIFTY25APR49500CE", "NSE:BANKNIFTY25APR49500PE",
            "NSE:BANKNIFTY25APR50000CE", "NSE:BANKNIFTY25APR50000PE",
            "NSE:BANKNIFTY25APR50500CE", "NSE:BANKNIFTY25APR50500PE",
            "NSE:BANKNIFTY25APR51000CE", "NSE:BANKNIFTY25APR51000PE",
            "NSE:BANKNIFTY25APR51500CE", "NSE:BANKNIFTY25APR51500PE",]

def load_access_token():
    """
    Load the access token from the text file.
    """
    if os.path.exists(ACCESS_TOKEN_FILE):
        with open(ACCESS_TOKEN_FILE, "r") as file:
            return file.read().strip()
    else:
        raise FileNotFoundError(f"Access token file '{ACCESS_TOKEN_FILE}' not found.")

def fetch_data_from_fyers(symbol, resolution, from_date, to_date):
    """
    Fetch historical data for a given symbol, resolution, and date range.
    """
    fyers = fyersModel.FyersModel(client_id=CLIENT_ID, token=load_access_token(), is_async=False)

    payload = {
        "symbol": symbol,
        "resolution": resolution,
        "date_format": 0,
        "range_from": int(from_date.timestamp()),
        "range_to": int(to_date.timestamp()),
        "cont_flag": "0",
    }
    
    try:
        response = fyers.history(data=payload)
        if response.get("s") == "ok" and "candles" in response:
            data = pd.DataFrame(response["candles"], 
                                columns=["timestamp", "open", "high", "low", "close", "volume"])
            return data
        else:
            print(f"Failed to fetch data for {symbol} at {resolution}: {response.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error fetching data for {symbol} at {resolution}: {e}")
        return None

def fetch_and_save_daily_data(symbols):
    """
    Fetch daily (1-minute resolution) data for all symbols from a start date to today and save locally.
    The timestamp is converted to IST.
    """
    start_date = datetime(2025,4, 1)  # Start date
    end_date = datetime.now()           # End date: today
    resolution = "1"

    for symbol in symbols:
        print(f"Fetching daily data for {symbol} from {start_date} to {end_date}...")
        current_start = start_date
        data_frames = []

        # Loop to fetch data in chunks (e.g., 100-day chunks)
        while current_start < end_date:
            current_end = min(current_start + timedelta(days=100), end_date)

            # Fetch data for the current range
            data = fetch_data_from_fyers(symbol, resolution, current_start, current_end)
            if data is not None:
                # Convert timestamp to IST time (assuming original timestamp is in UTC)
                data["timestamp"] = (pd.to_datetime(data["timestamp"], unit="s")
                                     .dt.tz_localize('UTC')
                                     .dt.tz_convert('Asia/Kolkata')
                                     .dt.strftime('%Y-%m-%d %H:%M:%S'))
                data_frames.append(data)
                print(f"Fetched data from {current_start} to {current_end} for {symbol}.")
            else:
                print(f"No data fetched for {symbol} from {current_start} to {current_end}.")

            # Move to the next range
            current_start = current_end + timedelta(days=1)

        # Combine all fetched data and save
        if data_frames:
            combined_data = pd.concat(data_frames, ignore_index=True)
            filename = f"ohlcv_{symbol.replace(':', '_')}.csv"
            combined_data.to_csv(filename, index=False)
            print(f"Saved daily data for {symbol} to {filename}.")
        else:
            print(f"No data available for {symbol}.")

# Main function
if __name__ == "__main__":
    try:
        print("Starting the data fetching process...")
        fetch_and_save_daily_data(SYMBOLS)
        print("Data fetching process completed.")
    except Exception as e:
        print(f"An error occurred: {e}")
