# screener/indicator_utils.py

import talib
import inspect
import pandas as pd
import os
import numpy as np # For checking NaN values
import traceback

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
    "CLOSE": "Close Price", "OPEN": "Open Price", "HIGH": "High Price", "LOW": "Low Price", "VOLUME": "Volume",
    "EFI": "Elder's Force Index" # Added EFI
}


# --------- Indicator Introspection ---------
def get_talib_function_list():
    price_fields = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
    custom_indicator_names = list(CUSTOM_INDICATORS.keys()) # Add custom indicator names
    talib_funcs = sorted([fn for fn in dir(talib) if fn.isupper() and callable(getattr(talib, fn))])
    return sorted(list(set(talib_funcs + price_fields + custom_indicator_names)))


def get_talib_params(fn_name):
    # If it's a custom indicator, define its parameters here or use a more dynamic system
    if fn_name.upper() in CUSTOM_INDICATORS:
        if fn_name.upper() == "EFI":
            return [
                # Parameters expected by the EFI custom function for frontend configuration
                {'name': 'period', 'type': 'int', 'default': 13} 
                # EFI implicitly uses 'close' and 'volume', so 'field' is not listed here,
                # but the custom function will access them from the DataFrame.
            ]
        elif fn_name.upper() == "MY_CUSTOM_INDICATOR": # Example from before
            return [
                {'name': 'period', 'type': 'int', 'default': 10},
                {'name': 'field', 'type': 'str', 'default': 'close'}
            ]
        # Add more custom indicator param definitions here
        return [] # Default empty params for other custom indicators

    if fn_name in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]:
        return []
    if not hasattr(talib, fn_name):
        print(f"Warning: TA-Lib function {fn_name} not found during param lookup.")
        return []

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
    groups_data = getattr(talib, '__function_groups__', {})
    result = {}
    
    result["Price & Volume"] = [
        {"value": "OPEN", "label": "Open Price (OPEN)", "params": ["timeframe"]},
        {"value": "HIGH", "label": "High Price (HIGH)", "params": ["timeframe"]},
        {"value": "LOW", "label": "Low Price (LOW)", "params": ["timeframe"]},
        {"value": "CLOSE", "label": "Close Price (CLOSE)", "params": ["timeframe"]},
        {"value": "VOLUME", "label": "Volume (VOLUME)", "params": ["timeframe"]},
    ]

    # Add Custom Indicators to a specific group or their own
    result["Custom Indicators"] = [
        {"value": "EFI", "label": "Elder's Force Index (EFI)", "params": ["timeframe", "period"]},
        {"value": "MY_CUSTOM_INDICATOR", "label": "My Custom Indicator Example", "params": ["timeframe", "field", "period"]},
        # Add more custom indicators here
    ]


    for group_name, fnames in groups_data.items():
        if group_name not in result:
            result[group_name] = []
        for fname in fnames:
            if hasattr(talib, fname): 
                actual_params = get_talib_params(fname)
                frontend_params = ["timeframe"]
                has_field_param = False 

                for p_info in actual_params:
                    p_name = p_info['name']
                    if p_name in ['open', 'high', 'low', 'close', 'volume', 'prices', 'inprice', 'real']:
                        has_field_param = True
                        continue 
                    
                    fe_param_name = p_name
                    if p_name == "timeperiod": fe_param_name = "period"
                    elif p_name == "fastperiod": fe_param_name = "fast_period"
                    elif p_name == "slowperiod": fe_param_name = "slow_period"
                    elif p_name == "signalperiod": fe_param_name = "signal_period"
                    elif p_name == "nbdevup": fe_param_name = "nbdev"
                    elif p_name == "nbdevdn": continue 
                    elif p_name == "fastk_period": fe_param_name = "fastk_period"
                    elif p_name == "slowk_period": fe_param_name = "slowk_period"
                    elif p_name == "slowd_period": fe_param_name = "slowd_period"
                    elif "matype" in p_name.lower(): continue 
                    
                    if fe_param_name not in frontend_params:
                         frontend_params.append(fe_param_name)
                
                if has_field_param and "field" not in frontend_params and not fname.startswith("CDL"):
                    is_ohlc_specific = any(p in fname for p in ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME'])
                    if not is_ohlc_specific:
                         frontend_params.insert(1, "field")

                result[group_name].append({
                    "value": fname,
                    "label": f"{TA_INDICATOR_LABELS.get(fname, fname)} ({fname})",
                    "params": sorted(list(set(frontend_params)))
                })

    if not result or "Overlap Studies" not in result : 
        all_talib_funcs = [fn for fn in dir(talib) if fn.isupper() and callable(getattr(talib, fn))]
        result["All TA-Lib Indicators"] = [{"value": fn, "label": TA_INDICATOR_LABELS.get(fn,fn), "params": ["timeframe", "field", "period"]} for fn in all_talib_funcs]
    return result

# --------- Data Utilities ---------
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
PROJECT_ROOT = os.path.dirname(BASE_DIR) 
DATA_DIR = os.path.join(PROJECT_ROOT, 'ohlcv_data')
print(f"[indicator_utils] Initialized. PROJECT_ROOT: {PROJECT_ROOT}, DATA_DIR: {DATA_DIR}")


def list_symbols(timeframe="daily"):
    timeframe_lower = timeframe.lower()
    folder_name = ""
    expected_suffix = ""

    if timeframe_lower == "daily":
        folder_name = "daily"
        expected_suffix = "_D.csv"
    elif timeframe_lower == "15min":
        folder_name = "15min_stock"
        expected_suffix = "_15.csv"
    else:
        print(f"[list_symbols] Unsupported timeframe for listing: {timeframe}")
        return []

    tf_data_dir = os.path.join(DATA_DIR, folder_name)
    if not os.path.exists(tf_data_dir) or not os.path.isdir(tf_data_dir):
        print(f"[list_symbols] Directory NOT FOUND or is not a directory: {tf_data_dir}")
        return []
    
    symbols = []
    for f_name in os.listdir(tf_data_dir):
        if f_name.endswith(expected_suffix):
            symbol_part = f_name[:-len(expected_suffix)] 
            symbols.append(symbol_part) 
    
    print(f"[list_symbols] Found {len(symbols)} symbols in {tf_data_dir}: {str(symbols[:5]) + ('...' if len(symbols) > 5 else '')}")
    return symbols

SYMBOLS = list_symbols("daily") 
if not SYMBOLS:
    print("[indicator_utils] WARNING: SYMBOLS list (daily) is empty. Scans may not find stocks unless symbols are loaded dynamically for other timeframes.")


def load_ohlcv(symbol, timeframe="daily"):
    timeframe_lower = timeframe.lower()
    folder_name = ""
    file_suffix = ""

    if timeframe_lower == "daily":
        folder_name = "daily"
        file_suffix = "_D.csv"
    elif timeframe_lower == "15min":
        folder_name = "15min_stock"
        file_suffix = "_15.csv"
    else:
        return None

    file_path = os.path.join(DATA_DIR, folder_name, f"{symbol}{file_suffix}")
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_csv(file_path)
        df.columns = [col.lower() for col in df.columns] 
        
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        date_col_found = False
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.set_index('date')
            date_col_found = True
        elif 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.set_index('timestamp')
            date_col_found = True
        
        if not all(col in df.columns for col in required_cols):
            pass 
        
        for col in required_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.dropna(subset=required_cols, inplace=True)

        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"[load_ohlcv] ERROR reading or processing CSV {file_path}: {e}")
        return None

# --------- Custom Indicator Registry and Functions ---------
CUSTOM_INDICATORS = {}

def register_custom_indicator(name):
    def decorator(func):
        CUSTOM_INDICATORS[name.upper()] = func
        print(f"[Custom Indicator] Registered: {name.upper()}")
        return func
    return decorator

@register_custom_indicator("MY_CUSTOM_INDICATOR")
def my_custom_indicator(df, period=10, field='close'):
    """Example custom indicator: SMA(EMA(field, period/2), period)"""
    if field not in df.columns:
        raise ValueError(f"Field '{field}' not found for MY_CUSTOM_INDICATOR. Available: {df.columns.tolist()}")
    if period <= 0:
        raise ValueError("Periods must be positive for MY_CUSTOM_INDICATOR")
    
    # Ensure periods are integers and at least 1
    ema_period = max(1, int(period / 2))
    sma_period = max(1, int(period))

    series = df[field].astype(float)
    if len(series) < ema_period: return np.nan # Not enough data for EMA
    
    ema_series = talib.EMA(series, timeperiod=ema_period)
    ema_series.dropna(inplace=True) 
    if ema_series.empty or len(ema_series) < sma_period:
        return np.nan 

    sma_of_ema = talib.SMA(ema_series, timeperiod=sma_period)
    return sma_of_ema.iloc[-1] if not sma_of_ema.empty and pd.notna(sma_of_ema.iloc[-1]) else np.nan

@register_custom_indicator("EFI")
def elder_force_index(df, period=13):
    """
    Calculates Elder's Force Index (EFI).
    EFI(1) = (Current Close - Previous Close) * Current Volume
    EFI(period) = EMA(EFI(1), period)
    """
    if not all(col in df.columns for col in ['close', 'volume']):
        raise ValueError("DataFrame must contain 'close' and 'volume' columns for EFI.")
    if len(df) < 2: # Need at least 2 data points for previous close
        return np.nan 
    if period <= 0:
        raise ValueError("Period for EFI must be positive.")

    close_prices = df['close'].astype(float)
    volume = df['volume'].astype(float)

    # EFI(1)
    efi_1 = (close_prices - close_prices.shift(1)) * volume
    efi_1.dropna(inplace=True) # Remove the first NaN due to shift(1)

    if efi_1.empty or len(efi_1) < period:
        return np.nan # Not enough data for EMA after calculating EFI(1)

    efi_period = talib.EMA(efi_1, timeperiod=int(period))
    
    return efi_period.iloc[-1] if not efi_period.empty and pd.notna(efi_period.iloc[-1]) else np.nan


# --------- Indicator Application Logic ---------
def call_indicator_logic(df, indicator_name, indicator_part=None, **kwargs_from_ast):
    indicator_name_upper = indicator_name.upper()
    
    if indicator_name_upper in CUSTOM_INDICATORS:
        custom_func = CUSTOM_INDICATORS[indicator_name_upper]
        # print(f"[call_indicator_logic] Calling CUSTOM indicator: {indicator_name_upper} with {kwargs_from_ast}")
        # Filter kwargs_from_ast to only those expected by the custom function
        sig = inspect.signature(custom_func)
        valid_kwargs = {k: v for k, v in kwargs_from_ast.items() if k in sig.parameters}
        try:
            return custom_func(df, **valid_kwargs)
        except Exception as e_custom:
            print(f"ERROR calling CUSTOM indicator {indicator_name_upper} with args {valid_kwargs}: {e_custom}")
            # traceback.print_exc()
            raise 

    if indicator_name_upper in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]:
        field_to_get = indicator_name_upper.lower()
        if field_to_get not in df.columns:
            raise KeyError(f"Field '{field_to_get}' not found in DataFrame for price indicator.")
        return df[field_to_get].iloc[-1]

    if not hasattr(talib, indicator_name_upper):
        raise ValueError(f"Unknown TA-Lib indicator: {indicator_name_upper}")

    fn = getattr(talib, indicator_name_upper)
    fn_sig = inspect.signature(fn)
    talib_params_expected = fn_sig.parameters.keys()
    
    series_inputs = {} 
    numeric_params = {} 

    if 'open' in talib_params_expected: series_inputs['open'] = df['open'].astype(float).values
    if 'high' in talib_params_expected: series_inputs['high'] = df['high'].astype(float).values
    if 'low' in talib_params_expected: series_inputs['low'] = df['low'].astype(float).values
    if 'close' in talib_params_expected: series_inputs['close'] = df['close'].astype(float).values
    if 'volume' in talib_params_expected: series_inputs['volume'] = df['volume'].astype(float).values
    
    if 'real' in talib_params_expected and not any(k in series_inputs for k in ['open','high','low','close']):
        field_name = str(kwargs_from_ast.get('field', 'close')).lower()
        if field_name not in df.columns:
            raise KeyError(f"Field '{field_name}' for 'real' input not found for {indicator_name_upper}. Avail: {df.columns.tolist()}")
        series_inputs['real'] = df[field_name].astype(float).values

    for ast_param_name, ast_param_value in kwargs_from_ast.items():
        talib_param_name = ast_param_name
        if ast_param_name == 'period': talib_param_name = 'timeperiod'
        elif ast_param_name == 'fast_period': talib_param_name = 'fastperiod'
        elif ast_param_name == 'slow_period': talib_param_name = 'slowperiod'
        elif ast_param_name == 'signal_period': talib_param_name = 'signalperiod'
        
        if talib_param_name in talib_params_expected:
            try:
                num_v = float(ast_param_value)
                numeric_params[talib_param_name] = int(num_v) if num_v == int(num_v) else num_v
            except (ValueError, TypeError):
                if talib_param_name == 'matype': 
                     numeric_params[talib_param_name] = int(ast_param_value) if isinstance(ast_param_value, (int, float, str)) and str(ast_param_value).isdigit() else 0
                # else:
                    # print(f"Warning: Could not convert param {talib_param_name} value {ast_param_value} to numeric for {indicator_name_upper}")


    if indicator_name_upper == "BBANDS":
        nbdev_val = float(kwargs_from_ast.get('nbdev', 2.0)) 
        if 'nbdevup' in talib_params_expected: numeric_params['nbdevup'] = nbdev_val
        if 'nbdevdn' in talib_params_expected: numeric_params['nbdevdn'] = nbdev_val
        if 'matype' not in numeric_params and 'matype' in talib_params_expected: 
            numeric_params['matype'] = 0


    final_talib_args = {**series_inputs, **numeric_params}
    # print(f"[call_indicator_logic] TA-Lib {indicator_name_upper} with args keys: {final_talib_args.keys()}")

    try:
        result_tuple_or_array = fn(**final_talib_args)
    except Exception as e_talib_call:
        print(f"ERROR calling TA-Lib function {indicator_name_upper} with args keys {list(final_talib_args.keys())}: {e_talib_call}")
        raise

    output_index = 0 
    if indicator_part: 
        indicator_part_lower = indicator_part.lower()
        if indicator_name_upper == "MACD":
            if indicator_part_lower == "signal" or indicator_part_lower == "macdsignal": output_index = 1
            elif indicator_part_lower == "hist" or indicator_part_lower == "macdhist": output_index = 2
            elif indicator_part_lower == "macd": output_index = 0 
            else: raise ValueError(f"Unknown part '{indicator_part}' for MACD. Use 'macd', 'signal', or 'hist'.")
        elif indicator_name_upper == "BBANDS":
            if indicator_part_lower == "upper" or indicator_part_lower == "upperband": output_index = 0
            elif indicator_part_lower == "middle" or indicator_part_lower == "middleband": output_index = 1
            elif indicator_part_lower == "lower" or indicator_part_lower == "lowerband": output_index = 2
            else: raise ValueError(f"Unknown part '{indicator_part}' for BBANDS. Use 'upper', 'middle', or 'lower'.")
        elif indicator_name_upper == "STOCH": 
            if indicator_part_lower == "slowk": output_index = 0
            elif indicator_part_lower == "slowd": output_index = 1
            else: raise ValueError(f"Unknown part '{indicator_part}' for STOCH. Use 'slowk' or 'slowd'.")
        else:
            print(f"Warning: Indicator part '{indicator_part}' specified for {indicator_name_upper}, but part handling not defined. Defaulting to first output.")

    selected_array = result_tuple_or_array
    if isinstance(result_tuple_or_array, tuple):
        if output_index < len(result_tuple_or_array):
            selected_array = result_tuple_or_array[output_index]
        else:
            raise ValueError(f"Requested part index {output_index} out of bounds for {indicator_name_upper} (outputs: {len(result_tuple_or_array)})")
    
    if not isinstance(selected_array, np.ndarray):
         raise TypeError(f"Selected output for {indicator_name_upper} (part: {indicator_part}, index: {output_index}) is not a NumPy array as expected.")

    return selected_array[-1] if selected_array.size > 0 and pd.notna(selected_array[-1]) else np.nan


def evaluate_operation(left, op, right):
    if pd.isna(left) or pd.isna(right):
        return False 

    op_lower = str(op).lower()
    if op_lower == '>': return left > right
    if op_lower == '<': return left < right
    if op_lower == '>=': return left >= right
    if op_lower == '<=': return left <= right
    if op_lower == '==': return np.isclose(left, right) if isinstance(left, float) or isinstance(right, float) else left == right
    if op_lower == '!=': return not (np.isclose(left, right) if isinstance(left, float) or isinstance(right, float) else left == right)
    
    if op_lower == "crosses above":
        print(f"WARN: '{op}' operator is complex. Current simplified eval might not be accurate.")
        return False 
    if op_lower == "crosses below":
        print(f"WARN: '{op}' operator is complex. Current simplified eval might not be accurate.")
        return False
        
    raise ValueError(f"Unsupported operator: {op}")

