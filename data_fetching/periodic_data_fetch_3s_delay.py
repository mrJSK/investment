import time
import datetime
import pandas as pd
from fyers_apiv3 import fyersModel
from datetime import timezone, timedelta
import concurrent.futures  # For multithreading

def load_access_token():
    with open("credentials/access_token.txt", "r") as file:
        return file.read().strip()

def load_client_id():
    with open("credentials/client_id.txt", "r") as file:
        return file.read().strip()

# Initialize Fyers API instance (synchronous mode)
fyers = fyersModel.FyersModel(
    client_id=load_client_id(), 
    is_async=False, 
    token=load_access_token(), 
    log_path=""
)

# Define IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# ---------------------------
# Logging Helper
# ---------------------------
def log_print(message: str):
    """
    Print a message with the current IST timestamp prefixed.
    """
    now_ist = datetime.datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_ist} IST] {message}")

# ---------------------------
# Helper Functions
# ---------------------------
def get_last_completed_candle_epoch(res_minutes, current_time=None):
    """
    Compute the Unix epoch timestamp for the last completed candle using UTC time.
    We subtract 'res_minutes' from the current time to avoid partial candles.
    """
    if current_time is None:
        current_time = datetime.datetime.now(timezone.utc)
    # Always subtract one resolution to avoid partial candle issues
    current_time -= timedelta(minutes=res_minutes)
    elapsed = (current_time.minute // res_minutes) * res_minutes
    last_candle = current_time.replace(minute=elapsed, second=0, microsecond=0)
    if last_candle >= current_time:
        last_candle -= timedelta(minutes=res_minutes)
    return int(last_candle.timestamp())

def epoch_to_ist_str(epoch_ts):
    """
    Convert a Unix epoch timestamp (UTC) to a string in IST (YYYY-MM-DD HH:MM:SS).
    """
    dt_utc = datetime.datetime.fromtimestamp(epoch_ts, tz=timezone.utc)
    dt_ist = dt_utc.astimezone(IST)
    return dt_ist.strftime("%Y-%m-%d %H:%M:%S")

def fetch_historical_data(symbol, resolution, days=4):
    """
    Fetch historical OHLC data for the last `days` days up to the last completed candle.
    
    Returns:
      (df, last_candle_epoch):
        df -> DataFrame with columns ["timestamp", "open", "high", "low", "close", "volume"]
              where 'timestamp' is in IST.
        last_candle_epoch -> The raw epoch (UTC) of the last complete candle.
    """
    log_print(f"Fetching historical data for symbol: {symbol} ...")
    res_minutes = int(resolution)
    expected_end_epoch = get_last_completed_candle_epoch(res_minutes)
    start_epoch = expected_end_epoch - days * 24 * 60 * 60

    log_print(f"Computed end epoch: {expected_end_epoch} ({epoch_to_ist_str(expected_end_epoch)})")
    log_print(f"Computed start epoch: {start_epoch} ({epoch_to_ist_str(start_epoch)})")

    data = {
        "symbol": symbol,
        "resolution": resolution,
        "date_format": "0",
        "range_from": str(start_epoch),
        "range_to": str(expected_end_epoch),
        "cont_flag": "1"
    }

    response = fyers.history(data=data)
    if response.get("code") == 200 and "candles" in response:
        candles = response["candles"]
        # Filter out candles with epoch > expected_end_epoch
        filtered_candles = [c for c in candles if c[0] <= expected_end_epoch]
        if not filtered_candles:
            log_print(f"No complete historical candles found for symbol: {symbol}")
            return None, None
        df = pd.DataFrame(filtered_candles, columns=["epoch", "open", "high", "low", "close", "volume"])
        df["timestamp"] = df["epoch"].apply(epoch_to_ist_str)
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        last_candle_epoch = filtered_candles[-1][0]
        log_print(f"Fetched historical data for {symbol} up to epoch {last_candle_epoch} ({epoch_to_ist_str(last_candle_epoch)})")
        return df, last_candle_epoch
    else:
        log_print(f"Error fetching historical data for {symbol}: {response}")
        return None, None

def fetch_candle_with_extra_wait(symbol, resolution, target_epoch):
    """
    Fetch a single completed candle that ends at 'target_epoch - resolution_seconds'.
    For example, if resolution=1 minute and target_epoch is a future boundary,
    the candle we want is for (target_epoch - 60).
    """
    res_minutes = int(resolution)
    resolution_seconds = res_minutes * 60
    # The actual candle we want is the one that ended one resolution period before target_epoch
    actual_candle_epoch = target_epoch - resolution_seconds

    log_print(f"Fetching candle for symbol: {symbol} for epoch {actual_candle_epoch} ({epoch_to_ist_str(actual_candle_epoch)})...")
    data = {
        "symbol": symbol,
        "resolution": resolution,
        "date_format": "0",
        "range_from": str(actual_candle_epoch),
        "range_to": str(actual_candle_epoch),
        "cont_flag": "1"
    }
    response = fyers.history(data=data)
    if response.get("code") == 200 and "candles" in response:
        candles = response["candles"]
        for c in candles:
            if c[0] == actual_candle_epoch:
                log_print(f"Found matching completed candle for symbol: {symbol}.")
                return c
        log_print(f"No matching candle found in response for symbol: {symbol}.")
    else:
        log_print(f"Error fetching candle for {symbol}: {response}")
    return None

def append_candle_to_csv(filename, candle, symbol):
    """
    Append a single candle to the CSV file with columns:
      ["timestamp", "open", "high", "low", "close", "volume"].
    """
    epoch_val = candle[0]
    ist_time = epoch_to_ist_str(epoch_val)
    row_data = [[
        ist_time,
        candle[1],
        candle[2],
        candle[3],
        candle[4],
        candle[5]
    ]]
    columns = ["timestamp", "open", "high", "low", "close", "volume"]
    df_candle = pd.DataFrame(row_data, columns=columns)
    df_candle.to_csv(filename, mode="a", index=False, header=False)
    log_print(f"Appended candle for {symbol} at {ist_time}")

def fetch_and_append(symbol, resolution, next_epoch, filename):
    """
    Worker function to:
      1) Fetch the completed candle for `symbol` at `next_epoch`
      2) Append to CSV
    """
    completed_candle = fetch_candle_with_extra_wait(symbol, resolution, next_epoch)
    if completed_candle:
        append_candle_to_csv(filename, completed_candle, symbol)
    else:
        log_print(f"No complete candle fetched for {symbol} at boundary {next_epoch}.")

# ---------------------------
# Main Execution for Continuous Live Market Data Fetch
# ---------------------------
if __name__ == "__main__":
    log_print("Script started.")
    symbols = [
        "NSE:NIFTYBANK-INDEX",
        "NSE:BANKNIFTY25FEB49100CE",
        "NSE:BANKNIFTY25FEB49100PE",
        "NSE:BANKNIFTY25FEB49200CE",
        "NSE:BANKNIFTY25FEB49200PE",
        "NSE:BANKNIFTY25FEB49300CE",
        "NSE:BANKNIFTY25FEB49300PE",
        "NSE:BANKNIFTY25FEB49400CE",
        "NSE:BANKNIFTY25FEB49400PE",
    ]
    resolution = "1"  # e.g., 1-minute resolution
    resolution_seconds = int(resolution) * 60

    # Dictionary to store CSV filenames and next expected candle epochs for each symbol
    symbol_info = {}

    # 1. Fetch historical data for each symbol and initialize the next expected epoch
    for sym in symbols:
        hist_df, last_candle_epoch = fetch_historical_data(sym, resolution, days=4)
        if hist_df is not None:
            safe_sym = sym.replace(":", "_")
            filename = f"historical_data_{safe_sym}_{resolution}min.csv"
            hist_df.to_csv(filename, index=False)
            log_print(f"Historical data for {sym} saved to {filename}")
            # Use an extra resolution period to ensure the new candle is fully complete
            next_expected_epoch = last_candle_epoch + (2 * resolution_seconds)
            symbol_info[sym] = {"filename": filename, "next_epoch": next_expected_epoch}
        else:
            log_print(f"Failed to fetch historical data for {sym}. Skipping symbol.")

    if not symbol_info:
        log_print("No symbols processed successfully. Exiting.")
        exit(1)

    # 2. Continuously fetch new candles until market close (16:00 IST)
    log_print("Starting continuous live market data fetch until market close (16:00 IST)...")
    while True:
        now_ist = datetime.datetime.now(IST)
        # Stop if current IST time is at or past 16:00
        if now_ist.time() >= datetime.time(16, 0):
            log_print("Reached 16:00 IST. Stopping live data fetch.")
            break

        now_utc_epoch = int(datetime.datetime.now(timezone.utc).timestamp())

        # Collect all symbols that are due for the next candle
        symbols_due = []
        for sym, info in symbol_info.items():
            if now_utc_epoch >= info["next_epoch"]:
                symbols_due.append(sym)

        if symbols_due:
            # Only do a single 3-second wait for all symbols that are due
            log_print(f"{len(symbols_due)} symbol(s) reached boundary. Waiting 3 seconds once to ensure candle completion...")
            time.sleep(3)

            # Fetch all symbols in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(symbols_due)) as executor:
                future_map = {}
                for sym in symbols_due:
                    next_epoch = symbol_info[sym]["next_epoch"]
                    filename = symbol_info[sym]["filename"]
                    future = executor.submit(fetch_and_append, sym, resolution, next_epoch, filename)
                    future_map[future] = sym

                # Wait for all tasks to complete
                for future in concurrent.futures.as_completed(future_map):
                    sym = future_map[future]
                    # Update the boundary for each completed symbol
                    symbol_info[sym]["next_epoch"] += resolution_seconds
                    new_epoch = symbol_info[sym]["next_epoch"]
                    log_print(f"Next fetch boundary for {sym} updated to {new_epoch} ({epoch_to_ist_str(new_epoch)})")
        else:
            # If no symbols are due, sleep briefly before checking again
            time.sleep(1)
    
    log_print("Script ended.")
