# screener/indicator_utils.py

import os
import inspect
import traceback

import pandas as pd
import numpy as np
import talib

from screener.utils import DATA_DIR

# --------- Friendly Display Names (ensure this is comprehensive) ---------

# --------- Data Utilities ---------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'ohlcv_data')

FOLDER_MAP = {
    "daily": ("daily", "_D.csv"),
    "weekly": ("weekly", "_W.csv"),
    "monthly": ("monthly", "_M.csv"),
    "1hour": ("1hour_stock", "_60.csv"),
    "30min": ("30min_stock", "_30.csv"),
    "15min": ("15min_stock", "_15.csv"),
    "5min": ("5min_stock", "_5.csv"),
    "1min": ("1min_stock", "_1.csv"),
}

TA_INDICATOR_LABELS = {
    # Overlap Studies
    "BBANDS": "Bollinger Bands",
    "DEMA": "Double Exponential Moving Average",
    "EMA": "Exponential Moving Average",
    "HT_TRENDLINE": "Hilbert Transform - Instantaneous Trendline",
    "KAMA": "Kaufman Adaptive Moving Average",
    "MA": "Moving Average",
    "MAMA": "MESA Adaptive Moving Average",
    "MIDPOINT": "MidPoint over period",
    "MIDPRICE": "Midpoint Price over period",
    "SAR": "Parabolic SAR",
    "SAREXT": "Parabolic SAR - Extended",
    "SMA": "Simple Moving Average",
    "T3": "Triple Exponential Moving Average (T3)",
    "TEMA": "Triple Exponential Moving Average",
    "TRIMA": "Triangular Moving Average",
    "WMA": "Weighted Moving Average",

    # Momentum Indicators
    "ADX": "Average Directional Movement Index",
    "ADXR": "Average Directional Movement Index Rating",
    "APO": "Absolute Price Oscillator",
    "AROON": "Aroon",
    "AROONOSC": "Aroon Oscillator",
    "BOP": "Balance Of Power",
    "CCI": "Commodity Channel Index",
    "CMO": "Chande Momentum Oscillator",
    "DX": "Directional Movement Index",
    "MACD": "Moving Average Convergence/Divergence",
    "MACDEXT": "MACD with controllable MA type",
    "MACDFIX": "Moving Average Convergence/Divergence Fix 12/26",
    "MFI": "Money Flow Index",
    "MINUS_DI": "Minus Directional Indicator",
    "MINUS_DM": "Minus Directional Movement",
    "MOM": "Momentum",
    "PLUS_DI": "Plus Directional Indicator",
    "PLUS_DM": "Plus Directional Movement",
    "PPO": "Percentage Price Oscillator",
    "ROC": "Rate of change : ((price/prevPrice)-1)*100",
    "ROCP": "Rate of change Percentage: (price-prevPrice)/prevPrice",
    "ROCR": "Rate of change ratio: (price/prevPrice)",
    "ROCR100": "Rate of change ratio 100 scale: (price/prevPrice)*100",
    "RSI": "Relative Strength Index",
    "STOCH": "Stochastic",
    "STOCHF": "Stochastic Fast",
    "STOCHRSI": "Stochastic Relative Strength Index",
    "TRIX": "1-day Rate-Of-Change (ROC) of a Triple Smooth EMA",
    "ULTOSC": "Ultimate Oscillator",
    "WILLR": "Williams' %R",

    # Volume Indicators
    "AD": "Chaikin A/D Line",
    "ADOSC": "Chaikin A/D Oscillator",
    "OBV": "On Balance Volume",

    # Volatility Indicators
    "ATR": "Average True Range",
    "NATR": "Normalized Average True Range",
    "TRANGE": "True Range",

    # Price Transform
    "AVGPRICE": "Average Price",
    "MEDPRICE": "Median Price",
    "TYPPRICE": "Typical Price",
    "WCLPRICE": "Weighted Close Price",

    # Cycle Indicators
    "HT_DCPERIOD": "Hilbert Transform - Dominant Cycle Period",
    "HT_DCPHASE": "Hilbert Transform - Dominant Cycle Phase",
    "HT_PHASOR": "Hilbert Transform - Phasor Components",
    "HT_SINE": "Hilbert Transform - SineWave",
    "HT_TRENDMODE": "Hilbert Transform - Trend vs Cycle Mode",

    # Statistic Functions
    "BETA": "Beta",
    "CORREL": "Pearson's Correlation Coefficient (r)",
    "LINEARREG": "Linear Regression",
    "LINEARREG_ANGLE": "Linear Regression Angle",
    "LINEARREG_INTERCEPT": "Linear Regression Intercept",
    "LINEARREG_SLOPE": "Linear Regression Slope",
    "STDDEV": "Standard Deviation",
    "TSF": "Time Series Forecast",
    "VAR": "Variance",

    # Math Transform & Operators
    "MAX": "Highest value over a specified period",
    "MAXINDEX": "Index of highest value over a specified period",
    "MIN": "Lowest value over a specified period",
    "MININDEX": "Index of lowest value over a specified period",
    "MINMAX": "Lowest and highest values over a specified period",
    "MINMAXINDEX": "Indexes of lowest and highest values over a specified period",
    "SUM": "Summation",

    # Pattern Recognition
    "CDL2CROWS": "Two Crows",
    "CDL3BLACKCROWS": "Three Black Crows",
    "CDL3INSIDE": "Three Inside Up/Down",
    "CDL3LINESTRIKE": "Three-Line Strike",
    "CDL3OUTSIDE": "Three Outside Up/Down",
    "CDL3STARSINSOUTH": "Three Stars In The South",
    "CDL3WHITESOLDIERS": "Three Advancing White Soldiers",
    "CDLABANDONEDBABY": "Abandoned Baby",
    "CDLADVANCEBLOCK": "Advance Block",
    "CDLBELTHOLD": "Belt-hold",
    "CDLBREAKAWAY": "Breakaway",
    "CDLCLOSINGMARUBOZU": "Closing Marubozu",
    "CDLCONCEALBABYSWALL": "Concealing Baby Swallow",
    "CDLCOUNTERATTACK": "Counterattack",
    "CDLDARKCLOUDCOVER": "Dark Cloud Cover",
    "CDLDOJI": "Doji",
    "CDLDOJISTAR": "Doji Star",
    "CDLDRAGONFLYDOJI": "Dragonfly Doji",
    "CDLENGULFING": "Engulfing Pattern",
    "CDLEVENINGDOJISTAR": "Evening Doji Star",
    "CDLEVENINGSTAR": "Evening Star",
    "CDLGAPSIDESIDEWHITE": "Up/Down-gap side-by-side white lines",
    "CDLGRAVESTONEDOJI": "Gravestone Doji",
    "CDLHAMMER": "Hammer",
    "CDLHANGINGMAN": "Hanging Man",
    "CDLHARAMI": "Harami Pattern",
    "CDLHARAMICROSS": "Harami Cross Pattern",
    "CDLHIGHWAVE": "High-Wave Candle",
    "CDLHIKKAKE": "Hikkake Pattern",
    "CDLHIKKAKEMOD": "Modified Hikkake Pattern",
    "CDLHOMINGPIGEON": "Homing Pigeon",
    "CDLIDENTICAL3CROWS": "Identical Three Crows",
    "CDLINNECK": "In-Neck Pattern",
    "CDLINVERTEDHAMMER": "Inverted Hammer",
    "CDLKICKING": "Kicking",
    "CDLKICKINGBYLENGTH": "Kicking - bull/bear by longer marubozu",
    "CDLLADDERBOTTOM": "Ladder Bottom",
    "CDLLONGLEGGEDDOJI": "Long Legged Doji",
    "CDLLONGLINE": "Long Line Candle",
    "CDLMARUBOZU": "Marubozu",
    "CDLMATCHINGLOW": "Matching Low",
    "CDLMATHOLD": "Mat Hold",
    "CDLMORNINGDOJISTAR": "Morning Doji Star",
    "CDLMORNINGSTAR": "Morning Star",
    "CDLONNECK": "On-Neck Pattern",
    "CDLPIERCING": "Piercing Pattern",
    "CDLRICKSHAWMAN": "Rickshaw Man",
    "CDLRISEFALL3METHODS": "Rising/Falling Three Methods",
    "CDLSEPARATINGLINES": "Separating Lines",
    "CDLSHOOTINGSTAR": "Shooting Star",
    "CDLSHORTLINE": "Short Line Candle",
    "CDLSPINNINGTOP": "Spinning Top",
    "CDLSTALLEDPATTERN": "Stalled Pattern",
    "CDLSTICKSANDWICH": "Stick Sandwich",
    "CDLTAKURI": "Takuri (Dragonfly Doji with long shadow)",
    "CDLTASUKIGAP": "Tasuki Gap",
    "CDLTHRUSTING": "Thrusting Pattern",
    "CDLTRISTAR": "Tristar Pattern",
    "CDLUNIQUE3RIVER": "Unique 3 River",
    "CDLUPSIDEGAP2CROWS": "Upside Gap Two Crows",
    "CDLXSIDEGAP3METHODS": "Upside/Downside Gap Three Methods",

    # Your Custom Indicators & Price Fields (preserved)
    "CLOSE": "Close Price",
    "OPEN": "Open Price",
    "HIGH": "High Price",
    "LOW": "Low Price",
    "VOLUME": "Volume",
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
    if field not in df.columns:
        raise ValueError(f"Field '{field}' not found for MY_CUSTOM_INDICATOR.")
    if not isinstance(period, (int, float)) or period <= 0:
        raise ValueError("Period must be a positive number.")
    series = df[field].astype(float)
    if len(series) < period:
        return np.nan
    ema_series = talib.EMA(series, timeperiod=int(period / 2))
    sma_of_ema = talib.SMA(ema_series, timeperiod=int(period))
    return sma_of_ema.iloc[-1] if not sma_of_ema.empty else np.nan

# --- FIX FOR EFI: Added 'field' parameter to match UI builder ---
@register_custom_indicator("EFI")
def elder_force_index(df, field='close', period=13):
    if not all(col in df.columns for col in ['close', 'volume']):
        raise ValueError("DataFrame must contain 'close' and 'volume' for EFI.")
    if not isinstance(period, (int, float)) or period <= 0:
        raise ValueError("Period for EFI must be a positive number.")
    
    close_prices = df['close'].astype(float)
    volume = df['volume'].astype(float)
    
    if len(close_prices) < 2: return np.nan
        
    efi_1 = (close_prices - close_prices.shift(1)) * volume
    efi_1 = efi_1.dropna()
    
    if efi_1.empty or len(efi_1) < period: return np.nan
        
    efi_period = talib.EMA(efi_1, timeperiod=int(period))
    return efi_period.iloc[-1] if not efi_period.empty and pd.notna(efi_period.iloc[-1]) else np.nan

# Other custom indicators for MACD, BBANDS, STOCH parts... (code is unchanged)
def _get_macd_part(df, part_index, field='close', fast_period=12, slow_period=26, signal_period=9):
    series_to_use = df[field].astype(float).values
    try:
        macd_tuple = talib.MACD(series_to_use, fastperiod=int(fast_period), slowperiod=int(slow_period), signalperiod=int(signal_period))
        part_series = macd_tuple[part_index]
        return part_series[-1] if part_series.size > 0 and pd.notna(part_series[-1]) else np.nan
    except Exception: return np.nan

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
        bbands_tuple = talib.BBANDS(series_to_use, timeperiod=int(period), nbdevup=float(nbdev), nbdevdn=float(nbdev), matype=0)
        part_series = bbands_tuple[part_index]
        return part_series[-1] if part_series.size > 0 and pd.notna(part_series[-1]) else np.nan
    except Exception: return np.nan

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
    high, low, close = df['high'].astype(float).values, df['low'].astype(float).values, df['close'].astype(float).values
    try:
        stoch_tuple = talib.STOCH(high, low, close, fastk_period=int(fastk_period), slowk_period=int(slowk_period), slowk_matype=0, slowd_period=int(slowd_period), slowd_matype=0)
        part_series = stoch_tuple[part_index]
        return part_series[-1] if part_series.size > 0 and pd.notna(part_series[-1]) else np.nan
    except Exception: return np.nan

@register_custom_indicator("STOCH_K")
def stoch_k_custom(df, fastk_period=14, slowk_period=3, slowd_period=3):
    return _get_stoch_part(df, 0, fastk_period, slowk_period, slowd_period)

@register_custom_indicator("STOCH_D")
def stoch_d_custom(df, fastk_period=14, slowk_period=3, slowd_period=3):
    return _get_stoch_part(df, 1, fastk_period, slowk_period, slowd_period)


# --- Introspection and Grouping Functions ---
def get_talib_params(fn_name):
    fn_name_upper = fn_name.upper()

    if fn_name_upper in CUSTOM_INDICATORS:
        if fn_name_upper in ["MACD_LINE", "MACD_SIGNAL", "MACD_HIST"]:
            return [{'name': 'field', 'type': 'str', 'default': 'close'}, {'name': 'fast_period', 'type': 'int', 'default': 12}, {'name': 'slow_period', 'type': 'int', 'default': 26}, {'name': 'signal_period', 'type': 'int', 'default': 9}]
        elif fn_name_upper in ["BB_UPPER", "BB_MIDDLE", "BB_LOWER"]:
            return [{'name': 'field', 'type': 'str', 'default': 'close'}, {'name': 'period', 'type': 'int', 'default': 20}, {'name': 'nbdev', 'type': 'float', 'default': 2.0}]
        elif fn_name_upper in ["STOCH_K", "STOCH_D"]:
            return [{'name': 'fastk_period', 'type': 'int', 'default': 14}, {'name': 'slowk_period', 'type': 'int', 'default': 3}, {'name': 'slowd_period', 'type': 'int', 'default': 3}]
        # --- FIX FOR EFI: Added 'field' to the parameter schema ---
        elif fn_name_upper == "EFI":
            return [{'name': 'field', 'type': 'str', 'default': 'close'}, {'name': 'period', 'type': 'int', 'default': 13}]
        elif fn_name_upper == "MY_CUSTOM_INDICATOR":
            return [{'name': 'period', 'type': 'int', 'default': 10}, {'name': 'field', 'type': 'str', 'default': 'close'}]
        else: return []

    if fn_name_upper in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]: return []
    if fn_name_upper.startswith('CDL'): return []

    if hasattr(talib, fn_name_upper):
        fn = getattr(talib, fn_name_upper)
        sig = inspect.signature(fn)
        params = []
        for name, param in sig.parameters.items():
            default_val = None if param.default is inspect.Parameter.empty else param.default
            param_type = 'series' if name in ['real', 'open', 'high', 'low', 'close', 'volume'] else 'any'
            if param_type != 'series':
                if isinstance(default_val, int): param_type = 'int'
                elif isinstance(default_val, float): param_type = 'float'

            frontend_name = name
            if name == "timeperiod": frontend_name = "period"
            elif name == "real": frontend_name = "field"
            elif name == "fastperiod": frontend_name = "fast_period"
            elif name == "slowperiod": frontend_name = "slow_period"
            elif name == "signalperiod": frontend_name = "signal_period"
            elif name == "nbdevup": frontend_name = "nbdev"
            elif name == "nbdevdn" or "matype" in name.lower(): continue
            params.append({'name': frontend_name, 'type': param_type, 'default': default_val})
        
        unique_params, seen = [], set()
        for p in params:
            if p['name'] not in seen:
                unique_params.append(p); seen.add(p['name'])
        return unique_params
        
    return []

def get_talib_grouped_indicators():
    result = {}
    result["Price & Volume"] = [
        {"value": "OPEN", "label": TA_INDICATOR_LABELS.get("OPEN", "Open Price"), "params": []},
        {"value": "HIGH", "label": TA_INDICATOR_LABELS.get("HIGH", "High Price"), "params": []},
        {"value": "LOW", "label": TA_INDICATOR_LABELS.get("LOW", "Low Price"), "params": []},
        {"value": "CLOSE", "label": TA_INDICATOR_LABELS.get("CLOSE", "Close Price"), "params": []},
        {"value": "VOLUME", "label": TA_INDICATOR_LABELS.get("VOLUME", "Volume"), "params": []},
    ]
    custom_group = []
    for name in sorted(CUSTOM_INDICATORS.keys()):
        custom_group.append({"value": name, "label": TA_INDICATOR_LABELS.get(name, name), "params": [p['name'] for p in get_talib_params(name)]})
    if custom_group: result["Custom & Derived Indicators"] = custom_group

    fn_groups = talib.get_function_groups()
    superseded_bases = {"MACD", "BBANDS", "STOCH"}
    for group_name, fn_list in fn_groups.items():
        indicators = []
        for fname in fn_list:
            fname_upper = fname.upper()
            if fname_upper in superseded_bases: continue
            params_list = get_talib_params(fname_upper)
            indicators.append({"value": fname_upper, "label": TA_INDICATOR_LABELS.get(fname_upper, fname_upper), "params": [p['name'] for p in params_list]})
        if indicators: result[group_name] = sorted(indicators, key=lambda x: x['label'])
    return result

# --- Data Loading and Calculation Dispatcher ---
def list_symbols(timeframe="daily"):
    """
    Return a list of all symbols for a given timeframe by checking its data folder.
    """
    timeframe_lower = timeframe.lower()
    if timeframe_lower not in FOLDER_MAP:
        return [] # Return empty list if timeframe is not supported

    folder_name, suffix = FOLDER_MAP[timeframe_lower]
    tf_data_dir = os.path.join(DATA_DIR, folder_name)

    if not os.path.isdir(tf_data_dir):
        return []

    return [fname[:-len(suffix)] for fname in os.listdir(tf_data_dir) if fname.endswith(suffix)]

# The global SYMBOLS list is generated from daily data by default.
# The run_screener view can dynamically get symbols for other timeframes if needed.
SYMBOLS = list_symbols("daily")

def load_ohlcv(symbol, timeframe="daily"):
    """
    Load OHLCV data for a given symbol and timeframe.
    Returns a pandas.DataFrame, or None if the file is missing or corrupt.
    """
    timeframe_lower = timeframe.lower()
    if timeframe_lower not in FOLDER_MAP:
        return None # Return None if timeframe is not supported

    folder_name, file_suffix = FOLDER_MAP[timeframe_lower]
    file_path = os.path.join(DATA_DIR, folder_name, f"{symbol}{file_suffix}")

    if not os.path.exists(file_path):
        return None

    try:
        df = pd.read_csv(file_path)
        # Standardize column names to lowercase
        df.columns = [c.lower() for c in df.columns]

        # Identify and set the date/time index
        time_col = 'timestamp' if 'timestamp' in df.columns else 'date'
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        df = df.set_index(time_col)
        
        # Ensure the required OHLCV columns exist and drop rows with invalid data
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        df = df.dropna(subset=required_cols)
        
        return df if not df.empty else None

    except Exception:
        # If anything goes wrong during file processing, return None
        return None

def call_indicator_logic(df, indicator_name, indicator_part=None, **kwargs_from_ast):
    name_upper = indicator_name.upper()

    if name_upper in CUSTOM_INDICATORS:
        custom_func = CUSTOM_INDICATORS[name_upper]
        sig = inspect.signature(custom_func)
        valid_kwargs = {k: v for k, v in kwargs_from_ast.items() if k in sig.parameters}
        return custom_func(df, **valid_kwargs)

    if name_upper in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]:
        return df[name_upper.lower()].iloc[-1]

    if not hasattr(talib, name_upper):
        raise ValueError(f"Unknown TA-Lib indicator: {name_upper}")

    fn = getattr(talib, name_upper)
    fn_sig = inspect.signature(fn)
    expected_params = fn_sig.parameters.keys()

    series_kwargs, numeric_kwargs = {}, {}
    series_map = {'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close', 'volume': 'volume', 'real': 'field'}
    for ta_param, df_col in series_map.items():
        if ta_param in expected_params:
            if df_col == 'field': # single series input
                field_name = str(kwargs_from_ast.get('field', 'close')).lower()
                series_kwargs['real'] = df[field_name].astype(float).values
                break # 'real' is exclusive
            else: # OHLCV input
                series_kwargs[ta_param] = df[df_col].astype(float).values
    
    param_map = {'period': 'timeperiod', 'fast_period': 'fastperiod', 'slow_period': 'slowperiod', 'signal_period': 'signalperiod', 'nbdev': 'nbdevup'}
    for ast_param, ast_value in kwargs_from_ast.items():
        ta_param = param_map.get(ast_param, ast_param)
        if ta_param in expected_params:
            numeric_kwargs[ta_param] = ast_value
            if ta_param == 'nbdevup': numeric_kwargs['nbdevdn'] = ast_value
    
    result = fn(**series_kwargs, **numeric_kwargs)
    
    if isinstance(result, tuple):
        # Default to first part if no specific part requested
        part_idx_map = {'upper': 0, 'middle': 1, 'lower': 2, 'macd': 0, 'signal': 1, 'hist': 2, 'k':0, 'd':1}
        part_idx = part_idx_map.get(indicator_part.lower() if indicator_part else '', 0)
        out_series = result[part_idx]
    else:
        out_series = result

    return out_series[-1] if hasattr(out_series, '__len__') and len(out_series) > 0 else np.nan

# Convenience wrapper, though not directly used by views anymore
def evaluate_operation(symbol: str, indicator_name: str, indicator_part: str=None, **kwargs):
    raise NotImplementedError("Use eval_ast_node() in views.py instead.")