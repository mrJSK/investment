# from django.http import JsonResponse
# import talib
# import inspect


# # screener/indicator_utils.py

# TA_INDICATOR_LABELS = {
#     "AD": "Chaikin A/D Line",
#     "ADOSC": "Chaikin A/D Oscillator",
#     "ADX": "Average Directional Movement Index",
#     "ADXR": "Average Directional Movement Index Rating",
#     "APO": "Absolute Price Oscillator",
#     "AROON": "Aroon",
#     "AROONOSC": "Aroon Oscillator",
#     "ATR": "Average True Range",
#     "AVGPRICE": "Average Price",
#     "BBANDS": "Bollinger Bands",
#     "BETA": "Beta",
#     "BOP": "Balance Of Power",
#     "CCI": "Commodity Channel Index",
#     # -- Candlestick Patterns (partial list, add all as needed)
#     "CDL2CROWS": "Two Crows",
#     "CDL3BLACKCROWS": "Three Black Crows",
#     "CDL3INSIDE": "Three Inside Up/Down",
#     "CDL3LINESTRIKE": "Three Outside Up/Down",
#     "CDL3STARSINSOUTH": "Three Stars In The South",
#     "CDL3WHITESOLDIERS": "Three Advancing White Soldiers",
#     "CDLABANDONEDBABY": "Abandoned Baby",
#     "CDLADVANCEBLOCK": "Advance Block",
#     "CDLBELTHOLD": "Belt-hold",
#     "CDLBREAKAWAY": "Breakaway",
#     "CDLCLOSINGMARUBOZU": "Closing Marubozu",
#     "CDLCONCEALBABYSWALL": "Concealing Baby Swallow",
#     "CDLCOUNTERATTACK": "Counterattack",
#     "CDLDARKCLOUDCOVER": "Dark Cloud Cover",
#     "CDLDOJI": "Doji",
#     "CDLDOJISTAR": "Doji Star",
#     "CDLDRAGONFLYDOJI": "Dragonfly Doji",
#     "CDLENGULFING": "Engulfing Pattern",
#     "CDLEVENINGDOJISTAR": "Evening Doji Star",
#     "CDLEVENINGSTAR": "Evening Star",
#     "CDLGAPSIDESIDEWHITE": "Up/Down-gap side-by-side white lines",
#     "CDLGRAVESTONEDOJI": "Gravestone Doji",
#     "CDLHAMMER": "Hammer",
#     "CDLHANGINGMAN": "Hanging Man",
#     "CDLHARAMI": "Harami Pattern",
#     "CDLHARAMICROSS": "Harami Cross Pattern",
#     "CDLHIGHWAVE": "High-Wave Candle",
#     "CDLHIKKAKE": "Hikkake Pattern",
#     "CDLHIKKAKEMOD": "Modified Hikkake Pattern",
#     "CDLHOMINGPIGEON": "Homing Pigeon",
#     "CDLIDENTICAL3CROWS": "Identical Three Crows",
#     "CDLINNECK": "In-Neck Pattern",
#     "CDLINVERTEDHAMMER": "Inverted Hammer",
#     "CDLKICKING": "Kicking",
#     "CDLKICKINGBYLENGTH": "Kicking - bull/bear determined by the longer marubozu",
#     "CDLLADDERBOTTOM": "Ladder Bottom",
#     "CDLLONGLEGGEDDOJI": "Long Legged Doji",
#     "CDLLONGLINE": "Long Line Candle",
#     "CDLMARUBOZU": "Marubozu",
#     "CDLMATCHINGLOW": "Matching Low",
#     "CDLMATHOLD": "Mat Hold",
#     "CDLMORNINGDOJISTAR": "Morning Doji Star",
#     "CDLMORNINGSTAR": "Morning Star",
#     "CDLONNECK": "On-Neck Pattern",
#     "CDLPIERCING": "Piercing Pattern",
#     "CDLRICKSHAWMAN": "Rickshaw Man",
#     "CDLRISEFALL3METHODS": "Rising/Falling Three Methods",
#     "CDLSEPARATINGLINES": "Separating Lines",
#     "CDLSHOOTINGSTAR": "Shooting Star",
#     "CDLSHORTLINE": "Short Line Candle",
#     "CDLSPINNINGTOP": "Spinning Top",
#     "CDLSTALLEDPATTERN": "Stalled Pattern",
#     "CDLSTICKSANDWICH": "Stick Sandwich",
#     "CDLTAKURI": "Takuri (Dragonfly Doji with very long lower shadow)",
#     "CDLTASUKIGAP": "Tasuki Gap",
#     "CDLTHRUSTING": "Thrusting Pattern",
#     "CDLTRISTAR": "Tristar Pattern",
#     "CDLUNIQUE3RIVER": "Unique 3 River",
#     "CDLUPSIDEGAP2CROWS": "Upside Gap Two Crows",
#     "CDLXSIDEGAP3METHODS": "Upside/Downside Gap Three Methods",
#     # -- Main indicators
#     "CMO": "Chande Momentum Oscillator",
#     "CORREL": "Pearson's Correlation Coefficient (r)",
#     "DEMA": "Double Exponential Moving Average",
#     "DX": "Directional Movement Index",
#     "EMA": "Exponential Moving Average",
#     "HT_DCPERIOD": "Hilbert Transform - Dominant Cycle Period",
#     "HT_DCPHASE": "Hilbert Transform - Dominant Cycle Phase",
#     "HT_PHASOR": "Hilbert Transform - Phasor Components",
#     "HT_SINE": "Hilbert Transform - SineWave",
#     "HT_TRENDLINE": "Hilbert Transform - Instantaneous Trendline",
#     "HT_TRENDMODE": "Hilbert Transform - Trend vs Cycle Mode",
#     "KAMA": "Kaufman Adaptive Moving Average",
#     "LINEARREG": "Linear Regression",
#     "LINEARREG_ANGLE": "Linear Regression Angle",
#     "LINEARREG_INTERCEPT": "Linear Regression Intercept",
#     "LINEARREG_SLOPE": "Linear Regression Slope",
#     "MA": "All Moving Average",
#     "MACD": "Moving Average Convergence/Divergence",
#     "MACDEXT": "MACD with controllable MA type",
#     "MACDFIX": "Moving Average Convergence/Divergence Fix 12/26",
#     "MAMA": "MESA Adaptive Moving Average",
#     "MAX": "Highest value over a specified period",
#     "MAXINDEX": "Index of highest value over a specified period",
#     "MEDPRICE": "Median Price",
#     "MFI": "Money Flow Index",
#     "MIDPOINT": "MidPoint over period",
#     "MIDPRICE": "Midpoint Price over period",
#     "MIN": "Lowest value over a specified period",
#     "MININDEX": "Index of lowest value over a specified period",
#     "MINMAX": "Lowest and highest values over a specified period",
#     "MINMAXINDEX": "Indexes of lowest and highest values over a specified period",
#     "MINUS_DI": "Minus Directional Indicator",
#     "MINUS_DM": "Minus Directional Movement",
#     "MOM": "Momentum",
#     "NATR": "Normalized Average True Range",
#     "OBV": "On Balance Volume",
#     "PLUS_DI": "Plus Directional Indicator",
#     "PLUS_DM": "Plus Directional Movement",
#     "PPO": "Percentage Price Oscillator",
#     "ROC": "Rate of change : ((price/prevPrice)-1)*100",
#     "ROCP": "Rate of change Percentage: (price-prevPrice)/prevPrice",
#     "ROCR": "Rate of change ratio: (price/prevPrice)",
#     "ROCR100": "Rate of change ratio 100 scale: (price/prevPrice)*100",
#     "RSI": "Relative Strength Index",
#     "SAR": "Parabolic SAR",
#     "SAREXT": "Parabolic SAR - Extended",
#     "SMA": "Simple Moving Average",
#     "STDDEV": "Standard Deviation",
#     "STOCH": "Stochastic",
#     "STOCHF": "Stochastic Fast",
#     "STOCHRSI": "Stochastic Relative Strength Index",
#     "SUM": "Summation",
#     "T3": "Triple Exponential Moving Average (T3)",
#     "TEMA": "Triple Exponential Moving Average",
#     "TRANGE": "True Range",
#     "TRIMA": "Triangular Moving Average",
#     "TRIX": "1-day Rate-Of-Change (ROC) of a Triple Smooth EMA",
#     "TSF": "Time Series Forecast",
#     "TYPPRICE": "Typical Price",
#     "ULTOSC": "Ultimate Oscillator",
#     "VAR": "Variance",
#     "WCLPRICE": "Weighted Close Price",
#     "WILLR": "Williams' %R",
#     "WMA": "Weighted Moving Average",
# }


# def get_talib_function_list():
#     """Returns a sorted list of all callable TA-Lib functions."""
#     return sorted([fn for fn in dir(talib) if fn.isupper() and callable(getattr(talib, fn))])

# def get_talib_params(fn_name):
#     """Returns parameter details for a TA-Lib function using introspection."""
#     fn = getattr(talib, fn_name)
#     sig = inspect.signature(fn)
#     params = []
#     for name, param in sig.parameters.items():
#         if name in ['real', 'open', 'high', 'low', 'close', 'volume']:
#             param_type = 'series'
#         elif param.default is inspect.Parameter.empty:
#             param_type = 'required'
#         elif isinstance(param.default, int):
#             param_type = 'int'
#         elif isinstance(param.default, float):
#             param_type = 'float'
#         else:
#             param_type = 'any'
#         params.append({
#             'name': name,
#             'type': param_type,
#             'default': None if param.default is inspect.Parameter.empty else param.default
#         })
#     return params

# def get_talib_grouped_indicators():
#     """
#     Returns a dict of { group_name: [{value, label}, ...], ... }
#     using TA-Lib's internal __function_groups__.
#     """
#     groups = getattr(talib, '__function_groups__', None)
#     result = {}
#     if groups:
#         for group_name, fnames in groups.items():
#             result[group_name] = [
#                 {
#                     "value": fname,
#                     "label": f"{TA_INDICATOR_LABELS.get(fname, fname)} ({fname})"
#                 }
#                 for fname in fnames
#             ]
#     else:
#         result["All"] = [
#             {
#                 "value": fname,
#                 "label": f"{TA_INDICATOR_LABELS.get(fname, fname)} ({fname})"
#             }
#             for fname in get_talib_function_list()
#         ]
#     return result

# # --- Django view (if you want a grouped API endpoint) ---
# def indicator_grouped_list(request):
#     # Usage: add to your urls.py as needed
#     return JsonResponse({"groups": get_talib_grouped_indicators()})

# # ---- Example usage (CLI test) ----
# if __name__ == '__main__':
#     print(get_talib_function_list())
#     print(get_talib_params('SMA'))
#     import json
#     print(json.dumps(get_talib_grouped_indicators(), indent=2))

# import pandas as pd
# import talib
# import os

# # --- List your data folder and symbols ---
# DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'ohlcv_data')
# SYMBOLS = [f.split('_')[0] for f in os.listdir(DATA_DIR) if f.endswith("_daily.csv")]

# def load_ohlcv(symbol, timeframe):
#     # For example: "data/RELIANCE_Daily.csv"
#     fname = os.path.join(DATA_DIR, f"{symbol}_{timeframe}.csv")
#     df = pd.read_csv(fname)
#     return df

# def call_talib_indicator(df, indicator, field, period, **kwargs):
#     # Map input fields for talib
#     if hasattr(talib, indicator):
#         series = df[field].astype(float)
#         fn = getattr(talib, indicator)
#         # MACD special case
#         if indicator.upper() in ['MACD']:
#             res = fn(series, fastperiod=kwargs.get('fastperiod',12), slowperiod=kwargs.get('slowperiod',26), signalperiod=kwargs.get('signalperiod',9))
#             return res[0].iloc[-1]
#         elif period:
#             return fn(series, timeperiod=int(period)).iloc[-1]
#         else:
#             return fn(series).iloc[-1]
#     raise ValueError(f"Unknown indicator: {indicator}")

# def evaluate_operation(left, op, right):
#     if op in ('>', 'gt'): return left > right
#     if op in ('<', 'lt'): return left < right
#     if op in ('>=', 'gte'): return left >= right
#     if op in ('<=', 'lte'): return left <= right
#     if op == "==": return left == right
#     # Cross logic: expects arrays of two values [prev, curr]
#     if op == "crosses above":
#         return left[0] < right and left[1] > right
#     if op == "crosses below":
#         return left[0] > right and left[1] < right
#     raise ValueError(f"Unsupported operator: {op}")

# def evaluate_filter_row(df, f):
#     # Left side: indicator with period, field, timeframe
#     indicator = f['indicator']
#     field = f['field']
#     period = int(f.get('period', 14))
#     left_val = call_talib_indicator(df, indicator, field, period)
#     op = f['mainOp']
#     # Right side: number or indicator
#     if f['rightType'] == "number":
#         right_val = float(f['rightValue'])
#     else:
#         right_val = call_talib_indicator(df, f['rightIndicator'], field, int(f.get('rightPeriod', 14)))
#     return evaluate_operation(left_val, op, right_val)
# screener/indicator_utils.py

import talib
import inspect
import pandas as pd
import os

# --------- Friendly Display Names ---------
TA_INDICATOR_LABELS = {
    "AD": "Chaikin A/D Line",
    "ADOSC": "Chaikin A/D Oscillator",
    "ADX": "Average Directional Movement Index",
    "ADXR": "Average Directional Movement Index Rating",
    "APO": "Absolute Price Oscillator",
    "AROON": "Aroon",
    "AROONOSC": "Aroon Oscillator",
    "ATR": "Average True Range",
    "AVGPRICE": "Average Price",
    "BBANDS": "Bollinger Bands",
    "BETA": "Beta",
    "BOP": "Balance Of Power",
    "CCI": "Commodity Channel Index",
    # -- Candlestick Patterns (partial list, add all as needed)
    "CDL2CROWS": "Two Crows",
    "CDL3BLACKCROWS": "Three Black Crows",
    "CDL3INSIDE": "Three Inside Up/Down",
    "CDL3LINESTRIKE": "Three Outside Up/Down",
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
    "CDLKICKINGBYLENGTH": "Kicking - bull/bear determined by the longer marubozu",
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
    "CDLTAKURI": "Takuri (Dragonfly Doji with very long lower shadow)",
    "CDLTASUKIGAP": "Tasuki Gap",
    "CDLTHRUSTING": "Thrusting Pattern",
    "CDLTRISTAR": "Tristar Pattern",
    "CDLUNIQUE3RIVER": "Unique 3 River",
    "CDLUPSIDEGAP2CROWS": "Upside Gap Two Crows",
    "CDLXSIDEGAP3METHODS": "Upside/Downside Gap Three Methods",
    # -- Main indicators
    "CMO": "Chande Momentum Oscillator",
    "CORREL": "Pearson's Correlation Coefficient (r)",
    "DEMA": "Double Exponential Moving Average",
    "DX": "Directional Movement Index",
    "EMA": "Exponential Moving Average",
    "HT_DCPERIOD": "Hilbert Transform - Dominant Cycle Period",
    "HT_DCPHASE": "Hilbert Transform - Dominant Cycle Phase",
    "HT_PHASOR": "Hilbert Transform - Phasor Components",
    "HT_SINE": "Hilbert Transform - SineWave",
    "HT_TRENDLINE": "Hilbert Transform - Instantaneous Trendline",
    "HT_TRENDMODE": "Hilbert Transform - Trend vs Cycle Mode",
    "KAMA": "Kaufman Adaptive Moving Average",
    "LINEARREG": "Linear Regression",
    "LINEARREG_ANGLE": "Linear Regression Angle",
    "LINEARREG_INTERCEPT": "Linear Regression Intercept",
    "LINEARREG_SLOPE": "Linear Regression Slope",
    "MA": "All Moving Average",
    "MACD": "Moving Average Convergence/Divergence",
    "MACDEXT": "MACD with controllable MA type",
    "MACDFIX": "Moving Average Convergence/Divergence Fix 12/26",
    "MAMA": "MESA Adaptive Moving Average",
    "MAX": "Highest value over a specified period",
    "MAXINDEX": "Index of highest value over a specified period",
    "MEDPRICE": "Median Price",
    "MFI": "Money Flow Index",
    "MIDPOINT": "MidPoint over period",
    "MIDPRICE": "Midpoint Price over period",
    "MIN": "Lowest value over a specified period",
    "MININDEX": "Index of lowest value over a specified period",
    "MINMAX": "Lowest and highest values over a specified period",
    "MINMAXINDEX": "Indexes of lowest and highest values over a specified period",
    "MINUS_DI": "Minus Directional Indicator",
    "MINUS_DM": "Minus Directional Movement",
    "MOM": "Momentum",
    "NATR": "Normalized Average True Range",
    "OBV": "On Balance Volume",
    "PLUS_DI": "Plus Directional Indicator",
    "PLUS_DM": "Plus Directional Movement",
    "PPO": "Percentage Price Oscillator",
    "ROC": "Rate of change : ((price/prevPrice)-1)*100",
    "ROCP": "Rate of change Percentage: (price-prevPrice)/prevPrice",
    "ROCR": "Rate of change ratio: (price/prevPrice)",
    "ROCR100": "Rate of change ratio 100 scale: (price/prevPrice)*100",
    "RSI": "Relative Strength Index",
    "SAR": "Parabolic SAR",
    "SAREXT": "Parabolic SAR - Extended",
    "SMA": "Simple Moving Average",
    "STDDEV": "Standard Deviation",
    "STOCH": "Stochastic",
    "STOCHF": "Stochastic Fast",
    "STOCHRSI": "Stochastic Relative Strength Index",
    "SUM": "Summation",
    "T3": "Triple Exponential Moving Average (T3)",
    "TEMA": "Triple Exponential Moving Average",
    "TRANGE": "True Range",
    "TRIMA": "Triangular Moving Average",
    "TRIX": "1-day Rate-Of-Change (ROC) of a Triple Smooth EMA",
    "TSF": "Time Series Forecast",
    "TYPPRICE": "Typical Price",
    "ULTOSC": "Ultimate Oscillator",
    "VAR": "Variance",
    "WCLPRICE": "Weighted Close Price",
    "WILLR": "Williams' %R",
    "WMA": "Weighted Moving Average",
}

# --------- Indicator Introspection ---------
def get_talib_function_list():
    """List all available TA-Lib indicator names."""
    return sorted([fn for fn in dir(talib) if fn.isupper() and callable(getattr(talib, fn))])

def get_talib_params(fn_name):
    """Parameter info for a TA-Lib function (for dynamic config UI)."""
    fn = getattr(talib, fn_name)
    sig = inspect.signature(fn)
    params = []
    for name, param in sig.parameters.items():
        param_type = 'series' if name in ['real', 'open', 'high', 'low', 'close', 'volume'] else 'required'
        if param.default is not inspect.Parameter.empty:
            if isinstance(param.default, int):
                param_type = 'int'
            elif isinstance(param.default, float):
                param_type = 'float'
            else:
                param_type = 'any'
        params.append({
            'name': name,
            'type': param_type,
            'default': None if param.default is inspect.Parameter.empty else param.default
        })
    return params

# --------- Custom Grouping for Chartink-style UI ---------
def get_talib_grouped_indicators():
    """Return { group_name: [indicator_dict, ...], ... } for Chartink-style categorized list."""
    groups = [
        ("Momentum", [
            'RSI', 'ADX', 'ADXR', 'APO', 'AROON', 'AROONOSC', 'BOP', 'CCI', 'CMO', 'DX', 'MACD',
            'MACDEXT', 'MACDFIX', 'MFI', 'MINUS_DI', 'MINUS_DM', 'MOM', 'PLUS_DI', 'PLUS_DM', 'PPO',
            'ROC', 'ROCP', 'ROCR', 'ROCR100', 'STOCH', 'STOCHF', 'STOCHRSI', 'TRIX', 'ULTOSC', 'WILLR'
        ]),
        ("Trend", [
            'SMA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'KAMA', 'T3', 'MIDPOINT', 'MIDPRICE', 'TRIMA',
            'BBANDS', 'MA', 'HT_TRENDLINE', 'MAVP', 'MAMA', 'SAR', 'SAREXT'
        ]),
        ("Volume", ['OBV', 'AD', 'ADOSC']),
        ("Volatility", ['ATR', 'NATR', 'TRANGE']),
        ("Candlestick Patterns", list(getattr(talib, '__function_groups__', {}).get('Pattern Recognition', []))),
        ("Math",   list(getattr(talib, '__function_groups__', {}).get('Math Operators', []))
                 + list(getattr(talib, '__function_groups__', {}).get('Math Transform', []))),
        ("Statistics", list(getattr(talib, '__function_groups__', {}).get('Statistic Functions', []))),
        ("Cycle", list(getattr(talib, '__function_groups__', {}).get('Cycle Indicators', []))),
        ("Price Transform", list(getattr(talib, '__function_groups__', {}).get('Price Transform', []))),
    ]
    def make_indicator_def(fname):
        label = TA_INDICATOR_LABELS.get(fname, fname)
        try:
            params = get_talib_params(fname)
            frontend_params = ["timeframe"]
            for p in params:
                pname = p['name']
                if pname == "timeperiod": frontend_params.append("period")
                elif pname == "fastperiod": frontend_params.append("fast_period")
                elif pname == "slowperiod": frontend_params.append("slow_period")
                elif pname == "signalperiod": frontend_params.append("signal_period")
                elif pname == "real": frontend_params.append("field")
            frontend_params = list(sorted(set(frontend_params)))
        except Exception:
            frontend_params = ["timeframe"]
        return {
            "value": fname,
            "label": f"{label} ({fname})",
            "params": frontend_params
        }
    result = {}
    for group_name, indicator_list in groups:
        result[group_name] = [make_indicator_def(fn) for fn in indicator_list if hasattr(talib, fn)]
    return result

# --------- Data Utilities ---------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'ohlcv_data')

def list_symbols():
    """Lists all available symbols (csv files)."""
    daily_dir = os.path.join(DATA_DIR, 'daily')
    if not os.path.exists(daily_dir): return []
    return [f.replace("_daily.csv", "") for f in os.listdir(daily_dir) if f.endswith("_daily.csv")]

SYMBOLS = list_symbols()

def load_ohlcv(symbol, timeframe="daily"):
    """Load OHLCV data for a symbol and timeframe ('daily' or '15min')."""
    path = os.path.join(DATA_DIR, timeframe, f"{symbol}_{timeframe}.csv")
    if not os.path.exists(path): return None
    return pd.read_csv(path)

# --------- Indicator Application and Scan Logic ---------
def call_talib_indicator(df, indicator, field, period=None, **kwargs):
    """Call a TA-Lib indicator on a DataFrame column."""
    if not hasattr(talib, indicator):
        raise ValueError(f"Unknown indicator: {indicator}")
    series = df[field].astype(float)
    fn = getattr(talib, indicator)
    # Special handling for MACD (3 outputs)
    if indicator.upper() == 'MACD':
        res = fn(series, fastperiod=kwargs.get('fastperiod',12), slowperiod=kwargs.get('slowperiod',26), signalperiod=kwargs.get('signalperiod',9))
        return res[0].iloc[-1]
    elif period:
        return fn(series, timeperiod=int(period)).iloc[-1]
    else:
        return fn(series).iloc[-1]

def evaluate_operation(left, op, right):
    """Performs logical/compare operations for scan conditions."""
    if op in ('>', 'gt'): return left > right
    if op in ('<', 'lt'): return left < right
    if op in ('>=', 'gte'): return left >= right
    if op in ('<=', 'lte'): return left <= right
    if op == "==": return left == right
    if op == "crosses above": return left[0] < right and left[1] > right
    if op == "crosses below": return left[0] > right and left[1] < right
    raise ValueError(f"Unsupported operator: {op}")

def evaluate_filter_row(df, f):
    """Evaluates a single filter condition on a DataFrame (for a stock)."""
    indicator = f['indicator']
    field = f['field']
    period = int(f.get('period', 14))
    left_val = call_talib_indicator(df, indicator, field, period)
    op = f['mainOp']
    if f['rightType'] == "number":
        right_val = float(f['rightValue'])
    else:
        right_val = call_talib_indicator(df, f['rightIndicator'], field, int(f.get('rightPeriod', 14)))
    return evaluate_operation(left_val, op, right_val)

# --- Django API View Example (use in urls.py if needed) ---
from django.http import JsonResponse

def indicator_grouped_list(request):
    return JsonResponse({"groups": get_talib_grouped_indicators()})
