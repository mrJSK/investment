import os
import pandas as pd
import talib

# Base directory where CSV files are stored, organized by timeframe subfolders
DATA_DIR = r'e:/investment/ohlcv_data'  # adjust to your local path

# Example tickers for segments (real lists should be populated with actual symbols)
SEGMENT_TICKERS = {
    'Nifty 50': ['RELIANCE', 'TCS', 'HDFCBANK'],
    'Nifty 100': ['INFY', 'WIPRO', 'HDFC'],
    'Nifty 500': ['LT', 'SBIN', 'ONGC'],
    'All NSE': [],       # empty means all available
    'Custom': []         # use Scan conditions to handle custom list if needed
}

TIMEFRAME_SUFFIX = {
    '15min': '15min',
    'daily': 'D',
    'weekly': 'W'
}

def load_stock_data(symbol, timeframe):
    """
    Load OHLCV data for the given symbol and timeframe from a CSV.
    Returns a pandas DataFrame or None if file not found.
    """
    suffix = TIMEFRAME_SUFFIX.get(timeframe, 'D')
    filename = f"NSE_{symbol}-EQ_{suffix}.csv"
    filepath = os.path.join(DATA_DIR, timeframe, filename)
    if not os.path.exists(filepath):
        return None
    df = pd.read_csv(filepath, parse_dates=['timestamp'])
    # Normalize column names to lower case for consistency
    df.columns = [col.lower() for col in df.columns]
    return df

def get_tickers_for_segment(segment):
    """Return the list of tickers for the given segment."""
    if segment == 'All NSE':
        # Load all available CSV files in the directory
        all_files = []
        for folder in [d for d in os.listdir(os.path.join(DATA_DIR, 'daily')) if os.path.isdir(os.path.join(DATA_DIR, 'daily', d))]:
            # just in case timeframes are folders; skip for now
            continue
        # If CSV files are directly under daily folder:
        for fname in os.listdir(os.path.join(DATA_DIR, 'daily')):
            if fname.startswith('NSE_') and fname.endswith('_EQ_D.csv'):
                all_files.append(fname.split('_')[1])
        return all_files
    return SEGMENT_TICKERS.get(segment, [])

def evaluate_conditions(df, conditions):
    """
    Given a DataFrame and a list of Condition objects (in order), return a boolean mask
    of rows where all conditions (with AND/OR) are met.
    """
    if df is None or df.empty:
        return pd.Series([False]*0)
    mask = pd.Series([True] * len(df), index=df.index)
    for cond in conditions:
        # Determine left-hand series
        if cond.left_indicator.lower() in ['open', 'high', 'low', 'close', 'volume']:
            left = df[cond.left_indicator.lower()]
        else:
            # TA-Lib function assumed (e.g. 'SMA', 'RSI', 'CDL_HAMMER', etc.)
            func = getattr(talib, cond.left_indicator.upper(), None)
            if func is None:
                # Unknown indicator
                continue
            if cond.left_indicator.startswith('CDL'):
                # Candlestick pattern functions take OHLC
                left = func(df['open'], df['high'], df['low'], df['close'])
            else:
                # Assume single-series indicator on close by default
                left = func(df['close'])
        # Determine right-hand series or constant
        if cond.right_indicator:
            if cond.right_indicator.lower() in ['open', 'high', 'low', 'close', 'volume']:
                right = df[cond.right_indicator.lower()]
            else:
                func2 = getattr(talib, cond.right_indicator.upper(), None)
                if func2:
                    right = func2(df['close'])
                else:
                    # If right_indicator not found, skip this condition
                    continue
        else:
            right = cond.constant

        # Apply operator
        if cond.operator == '>':
            cond_mask = left > right
        elif cond.operator == '<':
            cond_mask = left < right
        elif cond.operator == '>=':
            cond_mask = left >= right
        elif cond.operator == '<=':
            cond_mask = left <= right
        elif cond.operator == '==':
            cond_mask = left == right
        else:
            cond_mask = pd.Series([False]*len(df), index=df.index)

        # Combine with overall mask via AND/OR
        if cond.logic == 'OR':
            mask = mask | cond_mask
        else:
            mask = mask & cond_mask

    return mask.fillna(False)

def run_scan(scan, backtest=False):
    """
    Execute a Scan: load each ticker’s data, apply the scan conditions, and
    collect matches. If backtest=False, only the last row is checked. If True,
    all historical matches are returned.
    Returns a list of results: each a dict with symbol, date, close, pct_change, volume, matched_conditions.
    """
    results = []
    tickers = get_tickers_for_segment(scan.segment)
    for symbol in tickers:
        df = load_stock_data(symbol, scan.timeframe)
        if df is None or df.empty:
            continue
        df = df.sort_values('timestamp').reset_index(drop=True)
        # Compute percent change if needed
        df['pct_change'] = df['close'].pct_change() * 100

        mask = evaluate_conditions(df, list(scan.conditions.all()))
        if not backtest:
            # Only consider the last row
            if mask.iloc[-1]:
                row = df.iloc[-1]
                # Determine which conditions matched
                matched = []
                for cond in scan.conditions.all():
                    # Re-evaluate each condition for the last row
                    # (reuse evaluate_conditions logic on a single-row DataFrame)
                    temp_df = df.iloc[[-1]].reset_index(drop=True)
                    cond_mask = evaluate_conditions(temp_df, [cond])
                    if cond_mask.iloc[0]:
                        matched.append(str(cond))
                results.append({
                    'symbol': symbol,
                    'date': row['timestamp'].date(),
                    'close': row['close'],
                    'pct_change': round(row['pct_change'], 2),
                    'volume': row['volume'],
                    'matched': '; '.join(matched)
                })
        else:
            # Historical backtest: record each date where mask is True
            for idx, is_match in mask.items():
                if is_match:
                    row = df.loc[idx]
                    matched = []
                    for cond in scan.conditions.all():
                        temp_df = df.loc[[idx]].reset_index(drop=True)
                        cond_mask = evaluate_conditions(temp_df, [cond])
                        if cond_mask.iloc[0]:
                            matched.append(str(cond))
                    results.append({
                        'symbol': symbol,
                        'date': row['timestamp'].date(),
                        'close': row['close'],
                        'pct_change': round(row['pct_change'], 2),
                        'volume': row['volume'],
                        'matched': '; '.join(matched)
                    })
    return results
