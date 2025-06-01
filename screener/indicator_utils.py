# screener/indicator_utils.py

import traceback
import talib
import inspect
import pandas as pd
import os
import numpy as np # For checking NaN values

# --------- Friendly Display Names (ensure this is comprehensive) ---------
TA_INDICATOR_LABELS = {
    "AD": "Chaikin A/D Line", "ADOSC": "Chaikin A/D Oscillator", "ADX": "Average Directional Movement Index",
    "ADXR": "Average Directional Movement Index Rating", "APO": "Absolute Price Oscillator", "AROON": "Aroon",
    "AROONOSC": "Aroon Oscillator", "ATR": "Average True Range", "AVGPRICE": "Average Price",
    "BBANDS": "Bollinger Bands", "BETA": "Beta", "BOP": "Balance Of Power", "CCI": "Commodity Channel Index",
    "CMO": "Chande Momentum Oscillator", "CORREL": "Pearson's Correlation Coefficient (r)",
    "DEMA": "Double Exponential Moving Average", "DX": "Directional Movement Index",
    "EMA": "Exponential Moving Average", "HT_DCPERIOD": "Hilbert Transform - Dominant Cycle Period",
    "HT_DCPHASE": "Hilbert Transform - Dominant Cycle Phase", "HT_PHASOR": "Hilbert Transform - Phasor Components",
    "HT_SINE": "Hilbert Transform - SineWave", "HT_TRENDLINE": "Hilbert Transform - Instantaneous Trendline",
    "HT_TRENDMODE": "Hilbert Transform - Trend vs Cycle Mode", "KAMA": "Kaufman Adaptive Moving Average",
    "LINEARREG": "Linear Regression", "LINEARREG_ANGLE": "Linear Regression Angle",
    "LINEARREG_INTERCEPT": "Linear Regression Intercept", "LINEARREG_SLOPE": "Linear Regression Slope",
    "MA": "Moving average", "MACD": "Moving Average Convergence/Divergence",
    "MACDEXT": "MACD with controllable MA type", "MACDFIX": "Moving Average Convergence/Divergence Fix 12/26",
    "MAMA": "MESA Adaptive Moving Average", "MAX": "Highest value over a specified period",
    "MAXINDEX": "Index of highest value over a specified period", "MEDPRICE": "Median Price",
    "MFI": "Money Flow Index", "MIDPOINT": "MidPoint over period", "MIDPRICE": "Midpoint Price over period",
    "MIN": "Lowest value over a specified period", "MININDEX": "Index of lowest value over a specified period",
    "MINMAX": "Lowest and highest values over a specified period",
    "MINMAXINDEX": "Indexes of lowest and highest values over a specified period",
    "MINUS_DI": "Minus Directional Indicator", "MINUS_DM": "Minus Directional Movement", "MOM": "Momentum",
    "NATR": "Normalized Average True Range", "OBV": "On Balance Volume", "PLUS_DI": "Plus Directional Indicator",
    "PLUS_DM": "Plus Directional Movement", "PPO": "Percentage Price Oscillator",
    "ROC": "Rate of change : ((price/prevPrice)-1)*100", "ROCP": "Rate of change Percentage: (price-prevPrice)/prevPrice",
    "ROCR": "Rate of change ratio: (price/prevPrice)", "ROCR100": "Rate of change ratio 100 scale: (price/prevPrice)*100",
    "RSI": "Relative Strength Index", "SAR": "Parabolic SAR", "SAREXT": "Parabolic SAR - Extended",
    "SMA": "Simple Moving Average", "STDDEV": "Standard Deviation", "STOCH": "Stochastic",
    "STOCHF": "Stochastic Fast", "STOCHRSI": "Stochastic Relative Strength Index", "SUM": "Summation",
    "T3": "Triple Exponential Moving Average (T3)", "TEMA": "Triple Exponential Moving Average",
    "TRANGE": "True Range", "TRIMA": "Triangular Moving Average",
    "TRIX": "1-day Rate-Of-Change (ROC) of a Triple Smooth EMA", "TSF": "Time Series Forecast",
    "TYPPRICE": "Typical Price", "ULTOSC": "Ultimate Oscillator", "VAR": "Variance",
    "WCLPRICE": "Weighted Close Price", "WILLR": "Williams' %R", "WMA": "Weighted Moving Average",
    # Add all your CDL patterns here if needed for labels
}


# --------- Indicator Introspection ---------
def get_talib_function_list():
    return sorted([fn for fn in dir(talib) if fn.isupper() and callable(getattr(talib, fn))])

def get_talib_params(fn_name):
    # ... (this function can remain as is) ...
    fn = getattr(talib, fn_name)
    sig = inspect.signature(fn)
    params = []
    for name, param in sig.parameters.items():
        param_type = 'series' if name in ['real', 'open', 'high', 'low', 'close', 'volume'] else 'required'
        if param.default is not inspect.Parameter.empty:
            if isinstance(param.default, int): param_type = 'int'
            elif isinstance(param.default, float): param_type = 'float'
            else: param_type = 'any'
        params.append({
            'name': name, 'type': param_type,
            'default': None if param.default is inspect.Parameter.empty else param.default
        })
    return params

def get_talib_grouped_indicators():
    # ... (this function can remain as is, ensure it correctly generates your groups) ...
    groups_data = getattr(talib, '__function_groups__', {})
    result = {}
    for group_name, fnames in groups_data.items():
        result[group_name] = []
        for fname in fnames:
            if hasattr(talib, fname): 
                param_list = ["timeframe", "field", "period"] # Simplified default
                # Add more sophisticated param discovery if needed, similar to your views.py
                if fname in ["MACD", "MACDEXT", "MACDFIX", "BBANDS", "STOCH", "STOCHF", "STOCHRSI", "ULTOSC", "MAMA"]:
                     param_list.extend(["fast_period", "slow_period", "signal_period"]) # Common multi-param
                elif fname.startswith("CDL"):
                    param_list = ["timeframe"] # Candlesticks usually just need OHLC

                result[group_name].append({
                    "value": fname,
                    "label": f"{TA_INDICATOR_LABELS.get(fname, fname)} ({fname})",
                    "params": param_list
                })
    if not result: 
        result["All Indicators"] = [{"value": fn, "label": TA_INDICATOR_LABELS.get(fn,fn), "params": ["timeframe", "field", "period"]} for fn in get_talib_function_list()]
    return result

# --------- Data Utilities ---------
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
PROJECT_ROOT = os.path.dirname(BASE_DIR) 
DATA_DIR = os.path.join(PROJECT_ROOT, 'ohlcv_data')
print(f"[indicator_utils] Initialized. PROJECT_ROOT: {PROJECT_ROOT}, DATA_DIR: {DATA_DIR}")


def list_symbols(timeframe="daily"):
    """Lists symbols based on actual filenames: SYMBOL_D.csv or SYMBOL_15.csv."""
    timeframe_lower = timeframe.lower()
    folder_name = ""
    expected_suffix = ""

    if timeframe_lower == "daily":
        folder_name = "daily"
        expected_suffix = "_D.csv"
    elif timeframe_lower == "15min":
        folder_name = "15min_stock" # Corrected folder name
        expected_suffix = "_15.csv"
    else:
        print(f"[list_symbols] Unsupported timeframe for listing: {timeframe}")
        return []

    tf_data_dir = os.path.join(DATA_DIR, folder_name)
    print(f"[list_symbols] Checking for symbols in: {tf_data_dir} with suffix {expected_suffix}")

    if not os.path.exists(tf_data_dir) or not os.path.isdir(tf_data_dir):
        print(f"[list_symbols] Directory NOT FOUND or is not a directory: {tf_data_dir}")
        return []
    
    symbols = []
    for f_name in os.listdir(tf_data_dir):
        if f_name.endswith(expected_suffix):
            # Extract symbol part, e.g., "NSE_ADANIENT-EQ" from "NSE_ADANIENT-EQ_D.csv"
            symbol_part = f_name[:-len(expected_suffix)] 
            symbols.append(symbol_part) 
    
    print(f"[list_symbols] Found {len(symbols)} symbols in {tf_data_dir}: {str(symbols[:10]) + ('...' if len(symbols) > 10 else '')}")
    return symbols

SYMBOLS = list_symbols("daily") 
if not SYMBOLS:
    print("[indicator_utils] WARNING: SYMBOLS list (daily) is empty. Scans may not find stocks unless symbols are loaded dynamically for other timeframes.")


def load_ohlcv(symbol, timeframe="daily"):
    """Load OHLCV data. Handles specific folder for 15min and _D/_15 suffixes."""
    timeframe_lower = timeframe.lower()
    folder_name = ""
    file_suffix = ""

    if timeframe_lower == "daily":
        folder_name = "daily"
        file_suffix = "_D.csv"
    elif timeframe_lower == "15min":
        folder_name = "15min_stock" # Corrected folder name
        file_suffix = "_15.csv"
    else:
        print(f"[load_ohlcv] Unsupported timeframe: {timeframe}")
        return None

    # The 'symbol' variable here is expected to be like "NSE_ADANIENT-EQ"
    file_path = os.path.join(DATA_DIR, folder_name, f"{symbol}{file_suffix}")
    
    print(f"[load_ohlcv] Attempting to load: {file_path} for symbol '{symbol}', timeframe '{timeframe_lower}'")
    
    if not os.path.exists(file_path):
        print(f"[load_ohlcv] ERROR: File NOT FOUND: {file_path}")
        return None
    try:
        df = pd.read_csv(file_path)
        df.columns = [col.lower() for col in df.columns] 
        
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        # Handle 'date' or 'timestamp' for index setting
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.set_index('date')
        elif 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.set_index('timestamp')
        # Add other potential date/timestamp column names if necessary

        if not all(col in df.columns for col in required_cols):
            print(f"[load_ohlcv] WARNING: File {file_path} is missing one or more required columns ({required_cols}). Found: {df.columns.tolist()}")
        
        for col in required_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.dropna(subset=required_cols, inplace=True)

        if df.empty:
            print(f"[load_ohlcv] WARNING: DataFrame became empty after loading and cleaning for {file_path}.")
            return None

        print(f"[load_ohlcv] Successfully loaded and processed: {file_path}, Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"[load_ohlcv] ERROR reading or processing CSV {file_path}: {e}")
        traceback.print_exc()
        return None

# --------- Indicator Application and Scan Logic (call_talib_indicator, evaluate_operation) ---------
# These functions from the previous version should largely work if data loading is correct.
# Ensure call_talib_indicator correctly maps AST arguments to TA-Lib parameters.

def call_talib_indicator(df, indicator_name, field_name, period=None, **kwargs):
    indicator_name_upper = indicator_name.upper() 
    field_name_lower = str(field_name).lower() # Ensure field_name is a string and lowercased

    if not hasattr(talib, indicator_name_upper):
        raise ValueError(f"Unknown TA-Lib indicator: {indicator_name_upper}")
    
    # For indicators that take OHLCV directly (like CDL patterns)
    if indicator_name_upper.startswith("CDL"):
        if not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            raise ValueError(f"CDL pattern {indicator_name_upper} requires 'open', 'high', 'low', 'close' columns.")
        fn_args = {
            'open': df['open'].astype(float).values, # Pass numpy arrays for performance
            'high': df['high'].astype(float).values,
            'low': df['low'].astype(float).values,
            'close': df['close'].astype(float).values
        }
    elif field_name_lower not in df.columns: # For indicators taking a single series like 'close'
        raise KeyError(f"Field '{field_name_lower}' not found in DataFrame columns: {df.columns.tolist()} for indicator {indicator_name_upper}")
    else:
        series = df[field_name_lower].astype(float)
        if series.isnull().all():
            raise ValueError(f"Field '{field_name_lower}' for {indicator_name_upper} contains all NaN values.")
        if len(series) < (int(period) if period else 1):
            raise ValueError(f"Insufficient data for {indicator_name_upper} (length {len(series)}, period {period})")
        fn_args = {'real': series.values} # Default to 'real' for single series input

    # Add period if applicable and expected by the TA-Lib function
    fn = getattr(talib, indicator_name_upper)
    fn_sig = inspect.signature(fn)

    if period is not None and 'timeperiod' in fn_sig.parameters:
        fn_args['timeperiod'] = int(period)
    
    # Add other kwargs if they are in the function signature
    for k, v in kwargs.items():
        if k in fn_sig.parameters:
            try:
                # Attempt to convert to int if it's a whole number float/str, else float
                num_v = float(v)
                fn_args[k] = int(num_v) if num_v == int(num_v) else num_v
            except (ValueError, TypeError):
                 fn_args[k] = v # Pass as is if not clearly numeric (e.g., matype for MA)

    # print(f"[call_talib_indicator] Calling {indicator_name_upper} with effective args keys: {list(fn_args.keys())}")
    # For series args, print shape: print({k: v.shape if hasattr(v, 'shape') else type(v) for k,v in fn_args.items()})

    try:
        result_np_array = fn(**fn_args) # TA-Lib functions return numpy arrays
    except Exception as e_talib_call:
        print(f"ERROR calling TA-Lib function {indicator_name_upper} with args keys {list(fn_args.keys())}: {e_talib_call}")
        # traceback.print_exc()
        raise

    if not isinstance(result_np_array, np.ndarray): # Some functions might return tuples of arrays (e.g. MACD, BBANDS)
        if isinstance(result_np_array, tuple) and len(result_np_array) > 0 and isinstance(result_np_array[0], np.ndarray):
            result_np_array = result_np_array[0] # Default to first array for simplicity
        else:
            raise TypeError(f"TA-Lib function {indicator_name_upper} did not return a NumPy array or tuple of arrays as expected.")

    if result_np_array.size == 0:
        return np.nan 
    
    latest_value = result_np_array[-1] # Get the last value
    return latest_value if pd.notna(latest_value) else np.nan


def evaluate_operation(left, op, right):
    if pd.isna(left) or pd.isna(right):
        return False 

    op_lower = str(op).lower() # Ensure op is string
    # print(f"Evaluating operation: {left} {op_lower} {right}")
    if op_lower == '>': return left > right
    if op_lower == '<': return left < right
    if op_lower == '>=': return left >= right
    if op_lower == '<=': return left <= right
    if op_lower == '==': return np.isclose(left, right) if isinstance(left, float) or isinstance(right, float) else left == right
    if op_lower == '!=': return not (np.isclose(left, right) if isinstance(left, float) or isinstance(right, float) else left == right)
    
    if op_lower == "crosses above":
        print("WARN: 'crosses above' operator is not fully supported in this simplified evaluation (needs historical values).")
        return False 
    if op_lower == "crosses below":
        print("WARN: 'crosses below' operator is not fully supported in this simplified evaluation.")
        return False
    raise ValueError(f"Unsupported operator: {op}")

