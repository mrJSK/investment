# screener/indicator_utils.py

import os
import inspect
import traceback

import pandas as pd
import numpy as np
import talib

# --------- Friendly Display Names (ensure this is comprehensive) ---------
TA_INDICATOR_LABELS = {
    "AD": "Chaikin A/D Line", "ADOSC": "Chaikin A/D Oscillator", "ADX": "Average Directional Movement Index",
    "ADXR": "Average Directional Movement Index Rating", "APO": "Absolute Price Oscillator", "AROON": "Aroon",
    "AROONOSC": "Aroon Oscillator", "ATR": "Average True Range", "AVGPRICE": "Average Price",
    "BBANDS": "Bollinger Bands (Base)", "BETA": "Beta", "BOP": "Balance Of Power", "CCI": "Commodity Channel Index",
    "CMO": "Chande Momentum Oscillator", "CORREL": "Pearson's Correlation Coefficient (r)",
    "DEMA": "Double Exponential Moving Average", "DX": "Directional Movement Index",
    "EMA": "Exponential Moving Average", "HT_DCPERIOD": "Hilbert Transform - Dominant Cycle Period",
    "HT_DCPHASE": "Hilbert Transform - Dominant Cycle Phase", "HT_PHASOR": "Hilbert Transform - Phasor Components",
    "HT_SINE": "Hilbert Transform - SineWave", "HT_TRENDLINE": "Hilbert Transform - Instantaneous Trendline",
    "HT_TRENDMODE": "Hilbert Transform - Trend vs Cycle Mode", "KAMA": "Kaufman Adaptive Moving Average",
    "LINEARREG": "Linear Regression", "LINEARREG_ANGLE": "Linear Regression Angle",
    "LINEARREG_INTERCEPT": "Linear Regression Intercept", "LINEARREG_SLOPE": "Linear Regression Slope",
    "MA": "Moving average", "MACD": "Moving Average Convergence/Divergence (Base)",
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
    "SMA": "Simple Moving Average", "STDDEV": "Standard Deviation", "STOCH": "Stochastic (Base)",
    "STOCHF": "Stochastic Fast", "STOCHRSI": "Stochastic Relative Strength Index", "SUM": "Summation",
    "T3": "Triple Exponential Moving Average (T3)", "TEMA": "Triple Exponential Moving Average",
    "TRANGE": "True Range", "TRIMA": "Triangular Moving Average",
    "TRIX": "1-day Rate-Of-Change (ROC) of a Triple Smooth EMA", "TSF": "Time Series Forecast",
    "TYPPRICE": "Typical Price", "ULTOSC": "Ultimate Oscillator", "VAR": "Variance",
    "WCLPRICE": "Weighted Close Price", "WILLR": "Williams' %R", "WMA": "Weighted Moving Average",
    "CLOSE": "Close Price", "OPEN": "Open Price", "HIGH": "High Price", "LOW": "Low Price", "VOLUME": "Volume",
    "EFI": "Elder's Force Index",
    "MY_CUSTOM_INDICATOR": "My Custom Indicator Example",
    "MACD_LINE": "MACD Line",
    "MACD_SIGNAL": "MACD Signal Line",
    "MACD_HIST": "MACD Histogram",
    "BB_UPPER": "Bollinger Band Upper",
    "BB_MIDDLE": "Bollinger Band Middle",
    "BB_LOWER": "Bollinger Band Lower",
    "STOCH_K": "Stochastic %K",
    "STOCH_D": "Stochastic %D",
}

# --- Custom Indicator Registry and Functions ---
CUSTOM_INDICATORS = {}

def register_custom_indicator(name):
    def decorator(func):
        CUSTOM_INDICATORS[name.upper()] = func
        return func
    return decorator

@register_custom_indicator("MY_CUSTOM_INDICATOR")
def my_custom_indicator(df, period=10, field='close'):
    # Confirm requested field exists
    if field not in df.columns:
        raise ValueError(f"Field '{field}' not found for MY_CUSTOM_INDICATOR. Available: {df.columns.tolist()}")
    if period <= 0:
        raise ValueError("Periods must be positive for MY_CUSTOM_INDICATOR")
    ema_period = max(1, int(period / 2))
    sma_period = max(1, int(period))
    series = df[field].astype(float)
    if len(series) < ema_period:
        return np.nan
    # Compute EMA then SMA of EMA
    ema_series = talib.EMA(series, timeperiod=ema_period)
    ema_series = ema_series.dropna()
    if ema_series.empty or len(ema_series) < sma_period:
        return np.nan
    sma_of_ema = talib.SMA(ema_series, timeperiod=sma_period)
    return sma_of_ema.iloc[-1] if not sma_of_ema.empty and pd.notna(sma_of_ema.iloc[-1]) else np.nan

@register_custom_indicator("EFI")
def elder_force_index(df, period=13):
    # Must have both 'close' and 'volume'
    if not all(col in df.columns for col in ['close', 'volume']):
        raise ValueError("DataFrame must contain 'close' and 'volume' columns for EFI.")
    if len(df) < 2:
        return np.nan
    if period <= 0:
        raise ValueError("Period for EFI must be positive.")
    close_prices = df['close'].astype(float)
    volume = df['volume'].astype(float)
    efi_1 = (close_prices - close_prices.shift(1)) * volume
    efi_1 = efi_1.dropna()
    if efi_1.empty or len(efi_1) < period:
        return np.nan
    efi_period = talib.EMA(efi_1, timeperiod=int(period))
    return efi_period.iloc[-1] if not efi_period.empty and pd.notna(efi_period.iloc[-1]) else np.nan

def _get_macd_part(df, part_index, field='close', fast_period=12, slow_period=26, signal_period=9):
    series_to_use = df[field].astype(float).values
    try:
        macd_tuple = talib.MACD(
            series_to_use,
            fastperiod=int(fast_period),
            slowperiod=int(slow_period),
            signalperiod=int(signal_period)
        )
        part_series = macd_tuple[part_index]
        return part_series[-1] if part_series.size > 0 and pd.notna(part_series[-1]) else np.nan
    except Exception:
        return np.nan

@register_custom_indicator("MACD_LINE")
def macd_line_custom(df, field='close', fast_period=12, slow_period=26, signal_period=9):
    return _get_macd_part(df, 0, field, fast_period, slow_period, signal_period)

@register_custom_indicator("MACD_SIGNAL")
def macd_signal_custom(df, field='close', fast_period=12, slow_period=26, signal_period=9):
    return _get_macd_part(df, 1, field, fast_period, slow_period, signal_period)

@register_custom_indicator("MACD_HIST")
def macd_hist_custom(df, field='close', fast_period=12, slow_period=26, signal_period=9):
    return _get_macd_part(df, 2, field, fast_period, slow_period, signal_period)

def _get_bbands_part(df, part_index, field='close', period=20, nbdev=2.0):
    series_to_use = df[field].astype(float).values
    try:
        bbands_tuple = talib.BBANDS(
            series_to_use,
            timeperiod=int(period),
            nbdevup=float(nbdev),
            nbdevdn=float(nbdev),
            matype=0  # SMA
        )
        part_series = bbands_tuple[part_index]
        return part_series[-1] if part_series.size > 0 and pd.notna(part_series[-1]) else np.nan
    except Exception:
        return np.nan

@register_custom_indicator("BB_UPPER")
def bb_upper_custom(df, field='close', period=20, nbdev=2.0):
    return _get_bbands_part(df, 0, field, period, nbdev)

@register_custom_indicator("BB_MIDDLE")
def bb_middle_custom(df, field='close', period=20, nbdev=2.0):
    return _get_bbands_part(df, 1, field, period, nbdev)

@register_custom_indicator("BB_LOWER")
def bb_lower_custom(df, field='close', period=20, nbdev=2.0):
    return _get_bbands_part(df, 2, field, period, nbdev)

def _get_stoch_part(df, part_index, fastk_period=14, slowk_period=3, slowd_period=3):
    high_prices = df['high'].astype(float).values
    low_prices = df['low'].astype(float).values
    close_prices = df['close'].astype(float).values
    try:
        stoch_tuple = talib.STOCH(
            high_prices, low_prices, close_prices,
            fastk_period=int(fastk_period),
            slowk_period=int(slowk_period),
            slowk_matype=0,
            slowd_period=int(slowd_period),
            slowd_matype=0
        )
        part_series = stoch_tuple[part_index]
        return part_series[-1] if part_series.size > 0 and pd.notna(part_series[-1]) else np.nan
    except Exception:
        return np.nan

@register_custom_indicator("STOCH_K")
def stoch_k_custom(df, fastk_period=14, slowk_period=3, slowd_period=3):
    return _get_stoch_part(df, 0, fastk_period, slowk_period, slowd_period)

@register_custom_indicator("STOCH_D")
def stoch_d_custom(df, fastk_period=14, slowk_period=3, slowd_period=3):
    return _get_stoch_part(df, 1, fastk_period, slowk_period, slowd_period)

# --------- Indicator Introspection ---------
def get_talib_function_list():
    price_fields = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
    custom_indicator_names = list(CUSTOM_INDICATORS.keys())
    superseded_talib_bases = {"MACD", "BBANDS", "STOCH"}  # We override base TA-Lib MACD/BBANDS/STOCH
    talib_funcs = sorted([
        fn for fn in dir(talib)
        if fn.isupper() and callable(getattr(talib, fn)) and fn not in superseded_talib_bases
    ])
    return sorted(list(set(talib_funcs + price_fields + custom_indicator_names)))

def get_talib_params(fn_name):
    """
    Returns a list of parameter definitions (dicts with 'name', 'type', 'default')
    for a given TA-Lib function or custom indicator. The dict keys match what
    the frontend (builder.js) expects (e.g. 'field', 'period', 'fast_period', etc.).
    """
    fn_name_upper = fn_name.upper()

    # --- Custom Indicators ---
    if fn_name_upper in CUSTOM_INDICATORS:
        # Some custom indicators accept 'field', others do not.
        # We match builder.js’s modal parameter naming conventions.
        if fn_name_upper in ["MACD_LINE", "MACD_SIGNAL", "MACD_HIST"]:
            return [
                {'name': 'field', 'type': 'str', 'default': 'close'},
                {'name': 'fast_period', 'type': 'int', 'default': 12},
                {'name': 'slow_period', 'type': 'int', 'default': 26},
                {'name': 'signal_period', 'type': 'int', 'default': 9}
            ]
        elif fn_name_upper in ["BB_UPPER", "BB_MIDDLE", "BB_LOWER"]:
            return [
                {'name': 'field', 'type': 'str', 'default': 'close'},
                {'name': 'period', 'type': 'int', 'default': 20},
                {'name': 'nbdev', 'type': 'float', 'default': 2.0}
            ]
        elif fn_name_upper in ["STOCH_K", "STOCH_D"]:
            return [
                {'name': 'fastk_period', 'type': 'int', 'default': 14},
                {'name': 'slowk_period', 'type': 'int', 'default': 3},
                {'name': 'slowd_period', 'type': 'int', 'default': 3}
            ]
        elif fn_name_upper == "EFI":
            return [{'name': 'period', 'type': 'int', 'default': 13}]
        elif fn_name_upper == "MY_CUSTOM_INDICATOR":
            return [
                {'name': 'period', 'type': 'int', 'default': 10},
                {'name': 'field', 'type': 'str', 'default': 'close'}
            ]
        else:
            return []

    # --- Price Fields (no extra parameters) ---
    if fn_name_upper in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]:
        return []

    # --- TA-Lib Native Functions ---
    if hasattr(talib, fn_name_upper):
        fn = getattr(talib, fn_name_upper)
        sig = inspect.signature(fn)
        params = []
        for name, param in sig.parameters.items():
            # Determine type by inspecting default
            default_val = None if param.default is inspect.Parameter.empty else param.default
            if name in ['real', 'open', 'high', 'low', 'close', 'volume']:
                param_type = 'series'
            else:
                if param.default is inspect.Parameter.empty:
                    param_type = 'required'
                else:
                    if isinstance(param.default, int):
                        param_type = 'int'
                    elif isinstance(param.default, float):
                        param_type = 'float'
                    else:
                        param_type = 'any'
            # Map TA-Lib param names to frontend-friendly names
            frontend_name = name
            if name == "timeperiod":
                frontend_name = "period"
            elif name == "fastperiod":
                frontend_name = "fast_period"
            elif name == "slowperiod":
                frontend_name = "slow_period"
            elif name == "signalperiod":
                frontend_name = "signal_period"
            elif name == "nbdevup":
                frontend_name = "nbdev"
            elif name == "nbdevdn":
                continue  # Skip, since 'nbdev' covers both up/down
            # Skip any 'matype' or other complex parameters not handled
            if "matype" in name.lower():
                continue

            params.append({'name': frontend_name, 'type': param_type, 'default': default_val})

        # Deduplicate params if front-end mapping caused duplicates
        unique_params = []
        seen = set()
        for p in params:
            if p['name'] not in seen:
                unique_params.append(p)
                seen.add(p['name'])
        return unique_params

    # If no match, return empty
    return []

def get_talib_grouped_indicators():
    """
    Groups TA-Lib functions (and custom/derived indicators) into categories
    that the frontend’s modal can render as dropdowns. We leverage talib’s
    __function_groups__ if available, otherwise fall back to a generic list.
    """
    result = {}

    # “Price & Volume” group
    result["Price & Volume"] = [
        {"value": "OPEN", "label": TA_INDICATOR_LABELS.get("OPEN", "Open Price"), "params": []},
        {"value": "HIGH", "label": TA_INDICATOR_LABELS.get("HIGH", "High Price"), "params": []},
        {"value": "LOW", "label": TA_INDICATOR_LABELS.get("LOW", "Low Price"), "params": []},
        {"value": "CLOSE", "label": TA_INDICATOR_LABELS.get("CLOSE", "Close Price"), "params": []},
        {"value": "VOLUME", "label": TA_INDICATOR_LABELS.get("VOLUME", "Volume"), "params": []},
    ]

    # “Custom & Derived Indicators” group
    custom_group = []
    for name in sorted(CUSTOM_INDICATORS.keys()):
        custom_group.append({
            "value": name,
            "label": TA_INDICATOR_LABELS.get(name, name),
            "params": [p['name'] for p in get_talib_params(name)]
        })
    if custom_group:
        result["Custom & Derived Indicators"] = custom_group

    # Other TA-Lib groups if talib provides them; otherwise, fallback
    fn_groups = getattr(talib, "__function_groups__", {})
    superseded_bases = {"MACD", "BBANDS", "STOCH"}  # We have custom replacements
    for group_name, fn_list in fn_groups.items():
        indicators = []
        for fname in fn_list:
            fname_upper = fname.upper()
            if fname_upper in superseded_bases:
                continue
            if not hasattr(talib, fname_upper):
                continue
            indicators.append({
                "value": fname_upper,
                "label": TA_INDICATOR_LABELS.get(fname_upper, fname_upper),
                "params": [p['name'] for p in get_talib_params(fname_upper)]
            })
        if indicators:
            result[group_name] = sorted(indicators, key=lambda x: x['label'])

    # Fallback if grouping was empty (besides Price & Volume and Custom & Derived)
    if len(result) <= 2:
        all_talib_funcs = [
            fn for fn in dir(talib)
            if fn.isupper() and callable(getattr(talib, fn)) and fn not in superseded_bases
        ]
        indicators = [{
            "value": fn,
            "label": TA_INDICATOR_LABELS.get(fn, fn),
            "params": [p['name'] for p in get_talib_params(fn)]
        } for fn in sorted(all_talib_funcs)]
        result["All TA-Lib Indicators (Fallback)"] = indicators

    return result

# --------- Data Utilities ---------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'ohlcv_data')

def list_symbols(timeframe="daily"):
    """
    Return a list of all symbols for which we have CSV files
    in ohlcv_data/<timeframe>/. 
    - For 'daily': look for files ending in '_D.csv' under DATA_DIR/daily/
    - For '15min': look for files ending in '_15.csv' under DATA_DIR/15min/
    """
    timeframe_lower = timeframe.lower()
    if timeframe_lower == "daily":
        folder_name = "daily"
        suffix = "_D.csv"
    elif timeframe_lower == "15min":
        folder_name = "15min_stock"
        suffix = "_15.csv"
    else:
        return []

    tf_data_dir = os.path.join(DATA_DIR, folder_name)
    if not os.path.isdir(tf_data_dir):
        return []

    symbols = []
    for fname in os.listdir(tf_data_dir):
        if fname.endswith(suffix):
            symbol_name = fname[: -len(suffix)]
            symbols.append(symbol_name)
    return symbols

SYMBOLS = list_symbols("daily")

def load_ohlcv(symbol, timeframe="daily"):
    """
    Load OHLCV data for a given symbol and timeframe.
    - timeframe == "daily": expects a file named "{symbol}_D.csv" under DATA_DIR/daily/
    - timeframe == "15min": expects "{symbol}_15.csv" under DATA_DIR/15min/
    Returns a pandas.DataFrame indexed by timestamp, with columns ['open','high','low','close','volume'],
    or None if the file is missing or corrupt.
    """
    timeframe_lower = timeframe.lower()
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
        # Standardize column names to lowercase
        df.columns = [c.lower() for c in df.columns]

        # Identify and set the date/time index
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.set_index('timestamp')
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.set_index('date')
        else:
            # No valid time column
            return None

        # Ensure the numeric columns exist
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            return None

        # Convert to numeric and drop rows with NaN in any OHLCV
        for col in required_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=required_cols)
        if df.empty:
            return None

        return df

    except Exception as e:
        # If anything goes wrong, return None
        # (the view will treat missing data as a “False” for that branch)
        return None

def call_indicator_logic(df, indicator_name, indicator_part=None, **kwargs_from_ast):
    """
    Compute a single indicator (or part of a composite indicator) on 'df' (a DataFrame of OHLCV).
    - indicator_name: string, e.g. "SMA", "RSI", "MACD_LINE", "BB_UPPER", "STOCH_K", etc.
    - indicator_part: for multi-output TA-Lib functions (like MACD, STOCH), indicates which part
      was requested (e.g. “macd”, “signal”, “hist” for MACD; “k” or “d” for STOCH).
      *In practice, we handle MACD_LINE, MACD_SIGNAL, etc. as separate custom indicators, so
      indicator_part is rarely used here.*
    - kwargs_from_ast: a dict of parameters extracted from the AST, e.g. field='close', period=14, etc.

    Returns either:
      - A scalar (float) if the indicator produces a single latest value (e.g. RSI’s last bar),
      - Or a pandas.Series/array if you want to return the full series (though our views usually expect a scalar).
      If any required data is missing or an error occurs, this function should raise an Exception
      (caught upstream and treated as “False” for that symbol/branch).
    """
    name_upper = indicator_name.upper()

    # 1) Custom indicators registered at top
    if name_upper in CUSTOM_INDICATORS:
        custom_func = CUSTOM_INDICATORS[name_upper]
        sig = inspect.signature(custom_func)
        valid_kwargs = {}
        for ast_param, ast_value in kwargs_from_ast.items():
            # Only pass parameters that the custom function accepts
            if ast_param in sig.parameters:
                valid_kwargs[ast_param] = ast_value
        try:
            return custom_func(df, **valid_kwargs)
        except Exception as e:
            # Bubble up so that eval_ast_node catches it as a missing-data scenario
            raise

    # 2) Price fields: OPEN, HIGH, LOW, CLOSE, VOLUME
    if name_upper in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]:
        fld = name_upper.lower()
        if fld not in df.columns:
            raise KeyError(f"Field '{fld}' not found in DataFrame for price indicator.")
        # Return the most recent scalar value
        return df[fld].iloc[-1]

    # 3) Any other TA-Lib native function
    if not hasattr(talib, name_upper):
        raise ValueError(f"Unknown TA-Lib indicator or unsupported custom name: {name_upper}")

    fn = getattr(talib, name_upper)
    fn_sig = inspect.signature(fn)
    expected_params = fn_sig.parameters.keys()

    # Build up a dict of series inputs (for open, high, low, close, volume, real)
    series_kwargs = {}
    if 'open' in expected_params:
        series_kwargs['open'] = df['open'].astype(float).values
    if 'high' in expected_params:
        series_kwargs['high'] = df['high'].astype(float).values
    if 'low' in expected_params:
        series_kwargs['low'] = df['low'].astype(float).values
    if 'close' in expected_params:
        series_kwargs['close'] = df['close'].astype(float).values
    if 'volume' in expected_params:
        series_kwargs['volume'] = df['volume'].astype(float).values

    # If the function expects a single “real” series (e.g. RSI takes real=close by default):
    if 'real' in expected_params and not any(k in series_kwargs for k in ['open','high','low','close']):
        # The AST should have provided a 'field' param if needed
        field_name = str(kwargs_from_ast.get('field', 'close')).lower()
        if field_name not in df.columns:
            raise KeyError(f"Field '{field_name}' for 'real' input not found for {name_upper}. Available: {df.columns.tolist()}")
        series_kwargs['real'] = df[field_name].astype(float).values

    # Collect numeric parameters from AST (like timeperiod=period, fastperiod=fast_period, etc.)
    numeric_kwargs = {}
    for ast_param, ast_value in kwargs_from_ast.items():
        # Only pass numeric params that exist in the TA-Lib function’s signature
        # Map frontend names back to TA-Lib argument names if needed
        # E.g. 'period' -> 'timeperiod'; 'fast_period' -> 'fastperiod'; etc.
        if ast_param in ['period', 'fast_period', 'slow_period', 'signal_period', 'nbdev', 'fastk_period', 'slowk_period', 'slowd_period']:
            # Convert frontend naming to TA-Lib naming
            ta_param = ast_param
            if ast_param == 'period':
                ta_param = 'timeperiod'
            elif ast_param == 'fast_period':
                ta_param = 'fastperiod'
            elif ast_param == 'slow_period':
                ta_param = 'slowperiod'
            elif ast_param == 'signal_period':
                ta_param = 'signalperiod'
            elif ast_param in ['fastk_period','slowk_period','slowd_period']:
                # These already match the TA-Lib names for STOCH’s fastk_period etc.
                ta_param = ast_param
            elif ast_param == 'nbdev':
                # TA-Lib expects both nbdevup and nbdevdn; but most TA-Lib functions share them, so we pass nbdevup=nbdev, nbdevdn=nbdev:
                if 'nbdevup' in expected_params and 'nbdevdn' in expected_params:
                    numeric_kwargs['nbdevup'] = ast_value
                    numeric_kwargs['nbdevdn'] = ast_value
                    continue
                else:
                    ta_param = 'nbdev'
            if ta_param in expected_params:
                numeric_kwargs[ta_param] = ast_value

    # Now call the TA-Lib function
    try:
        # Example: talib.SMA(close=array_of_closes, timeperiod=14)
        result = fn(**series_kwargs, **numeric_kwargs)
    except Exception as e:
        raise

    # If it returns multiple arrays (tuple), pick the first or the requested part
    if isinstance(result, tuple):
        # E.g. BBANDS returns (upper, middle, lower)
        # If indicator_part is provided, pick the correct index; otherwise default to first
        part_idx = 0
        if indicator_part:
            # Map 'upper' -> 0, 'middle'->1, 'lower'->2, 'macd'->0, 'signal'->1, 'hist'->2, etc.
            part_lower = indicator_part.lower()
            if 'upper' in part_lower:
                part_idx = 0
            elif 'middle' in part_lower:
                part_idx = 1
            elif 'lower' in part_lower:
                part_idx = 2
            elif 'macd' in part_lower:
                part_idx = 0
            elif 'signal' in part_lower:
                part_idx = 1
            elif 'hist' in part_lower:
                part_idx = 2
            else:
                part_idx = 0
        out_series = result[part_idx]
    else:
        out_series = result

    # Convert numpy array or pandas Series to a scalar (latest bar) if possible
    if isinstance(out_series, np.ndarray):
        if out_series.size == 0:
            return np.nan
        return out_series[-1]
    elif isinstance(out_series, (pd.Series, pd.Index)):
        if out_series.empty:
            return np.nan
        return out_series.iloc[-1]
    else:
        # Could already be a scalar
        return out_series

def evaluate_operation(symbol: str, indicator_name: str, indicator_part: str=None, **kwargs):
    """
    Convenience wrapper to load the DataFrame for a given symbol/timeframe,
    apply call_indicator_logic(), and return either a float or np.nan.
    """
    # This function may not be used directly, but is here for completeness
    raise NotImplementedError("Use eval_ast_node() in views.py instead.")

def evaluate_ast_for_symbol(symbol: str, ast_main: dict) -> bool:
    """
    This is a helper for views.py to catch exceptions from eval_ast_node.
    """
    from screener.views import eval_ast_node  # avoid circular import
    try:
        result = bool(eval_ast_node(symbol, ast_main, context={}))
        return result
    except Exception:
        return False

