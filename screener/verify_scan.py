import os
import pandas as pd
import numpy as np
import talib

# --- Configuration ---
# Set the path to your data directory.
# This script assumes it's being run from the 'E:\investment\' directory.
DATA_DIR = 'ohlcv_data'
DAILY_DIR = os.path.join(DATA_DIR, 'daily')
MIN15_DIR = os.path.join(DATA_DIR, '15min_stock')

def load_and_prepare_data(filepath):
    """
    Loads a CSV file into a pandas DataFrame, handling potential errors.
    - Standardizes column names to lowercase.
    - Sets a datetime index.
    - Converts OHLCV columns to numeric types.
    """
    if not os.path.exists(filepath):
        return None
    try:
        df = pd.read_csv(filepath)
        # Standardize column names
        df.columns = [c.lower() for c in df.columns]

        # Find and set the datetime index
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.set_index('timestamp')
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.set_index('date')
        else:
            return None # No valid time column found

        # Ensure required columns exist and are numeric
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            return None
            
        for col in required_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows with any NaN values in essential columns and sort by date
        df.dropna(subset=required_cols, inplace=True)
        df.sort_index(inplace=True)
        
        return df if not df.empty else None

    except Exception as e:
        print(f"  [Error] Could not process file {os.path.basename(filepath)}: {e}")
        return None


def run_standalone_scan():
    """
    Scans stocks based on hardcoded criteria, independent of the Django project.
    """
    print("--- Standalone Python Screener ---")

    # 1. Find all symbols that have BOTH daily and 15-minute data files.
    daily_files = {f.replace('_D.csv', '') for f in os.listdir(DAILY_DIR) if f.endswith('_D.csv')}
    min15_files = {f.replace('_15.csv', '') for f in os.listdir(MIN15_DIR) if f.endswith('_15.csv')}
    
    common_symbols = sorted(list(daily_files.intersection(min15_files)))

    if not common_symbols:
        print("No common symbols with both daily and 15-min data were found.")
        return

    print(f"Found {len(common_symbols)} symbols with both daily and 15-min data. Starting scan...")
    print("Query: 15min SMA(Open, 14) > 2000 AND Daily RSI(Open, 14) > 60")
    print("-" * 110)
    print(f"{'SYMBOL':<20} | {'15m SMA(Open,14)':<20} | {'Condition Met?':<15} | {'Daily RSI(Open,14)':<20} | {'Condition Met?':<15}")
    print("-" * 110)

    matched_stocks = []

    # 2. Loop through each common symbol and apply the logic.
    for symbol_base in common_symbols:
        # Construct file paths
        daily_filepath = os.path.join(DAILY_DIR, f"{symbol_base}_D.csv")
        min15_filepath = os.path.join(MIN15_DIR, f"{symbol_base}_15.csv")

        # Load data
        df_daily = load_and_prepare_data(daily_filepath)
        df_15min = load_and_prepare_data(min15_filepath)

        # Skip if either data file is missing or invalid
        if df_daily is None or df_15min is None:
            print(f"{symbol_base:<20} | {'DATA MISSING/INVALID':<55}")
            continue

        # 3. Calculate indicators and check conditions.
        
        # --- 15-minute SMA Condition ---
        sma_value = np.nan
        if len(df_15min) >= 14:
            # Use 'open' prices as per the query
            sma_series = talib.SMA(df_15min['open'], timeperiod=14)
            if not sma_series.empty:
                sma_value = sma_series.iloc[-1]
        
        sma_passes = sma_value > 2000 if pd.notna(sma_value) else False
        sma_display = f"{sma_value:.2f}" if pd.notna(sma_value) else "NaN"

        # --- Daily RSI Condition ---
        rsi_value = np.nan
        if len(df_daily) >= 14:
            # Use 'open' prices as per the query
            rsi_series = talib.RSI(df_daily['open'], timeperiod=14)
            if not rsi_series.empty:
                rsi_value = rsi_series.iloc[-1]
                
        rsi_passes = rsi_value > 60 if pd.notna(rsi_value) else False
        rsi_display = f"{rsi_value:.2f}" if pd.notna(rsi_value) else "NaN"

        # Print the diagnostic line for EVERY stock
        print(f"{symbol_base:<20} | {sma_display:<20} | {str(sma_passes):<15} | {rsi_display:<20} | {str(rsi_passes):<15}")
        
        # 4. If both conditions are met, add to the final list.
        if sma_passes and rsi_passes:
            matched_stocks.append(symbol_base)


    # 5. Print a summary of the results.
    print("-" * 110)
    if matched_stocks:
        print("\n--- Summary: Matched Stocks ---")
        for symbol in matched_stocks:
            print(symbol)
    else:
        print("\n--- Summary: No stocks matched both criteria. ---")


if __name__ == "__main__":
    run_standalone_scan()
