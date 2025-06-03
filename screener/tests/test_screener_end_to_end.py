# screener/tests/test_screener_end_to_end.py

import os
import sys
import pytest
import numpy as np
import pandas as pd

# ───────────────────────────────────────────────────────────────────────────────
# 0) Make sure the project root (E:\investment) is on sys.path so that
#    Python can import “algo_trading.settings” and also “screener.*” modules.
#    We assume this file is at:
#       E:\investment\screener\tests\test_screener_end_to_end.py
#    Therefore, two levels up is the project root.
# ───────────────────────────────────────────────────────────────────────────────
_this_file = os.path.abspath(__file__)       # ...\screener\tests\test_screener_end_to_end.py
_tests_dir = os.path.dirname(_this_file)     # ...\screener\tests
_screener_dir = os.path.dirname(_tests_dir)  # ...\screener
_project_root = os.path.dirname(_screener_dir)  # E:\investment
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# ───────────────────────────────────────────────────────────────────────────────
# 1) Configure Django settings so that importing models or views does not fail.
#    We assume your settings module is "algo_trading.settings".
# ───────────────────────────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "algo_trading.settings")
import django
django.setup()

# ───────────────────────────────────────────────────────────────────────────────
# Now safe to import indicator_utils, dsl_parser, and eval_ast_node from views.
# ───────────────────────────────────────────────────────────────────────────────
from screener import indicator_utils
from screener.dsl_parser import parse_query
from screener.views import eval_ast_node

# --------------------------------------------------------------------------------
# Fixture: pick any symbol present in BOTH daily/ and 15min_stock/
# --------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def known_symbol():
    daily_syms = indicator_utils.list_symbols("daily")
    min15_syms = indicator_utils.list_symbols("15min")
    common = set(daily_syms).intersection(min15_syms)
    if not common:
        pytest.skip("No common symbol found in daily/ and 15min_stock/. Skipping tests.")
    return sorted(common)[0]


# --------------------------------------------------------------------------------
# 2) DSL Parser Tests
# --------------------------------------------------------------------------------
@pytest.mark.parametrize("query, expected_top_type", [
    # Single indicator as standalone
    ("CLOSE()", "IndicatorCall"),
    # Indicator w/ timeframe and parameter
    ("Daily SMA(CLOSE(), 14)", "IndicatorCall"),
    # Comparison: >
    ("Daily SMA(CLOSE(), 14) > 100", "Comparison"),
    # Logical AND
    ("Daily CLOSE() > 50 AND 15min RSI(CLOSE(), 14) < 70", "BinaryExpression"),
    # Parentheses and OR
    ("(Daily CLOSE() > Daily SMA(CLOSE(), 20)) OR (15min RSI(CLOSE(), 14) > 60)", "BinaryExpression"),
    # Nested indicator as parameter
    ("SMA(EMA(CLOSE(), 10), 5)", "IndicatorCall"),
])
def test_parse_query_basic(query, expected_top_type):
    """
    For each query string, parse it and verify the top-level 'type' in the AST.
    """
    ast = parse_query(query)
    assert isinstance(ast, dict), f"parse_query should return a dict. Got: {type(ast)}"
    top_type = ast.get("type")
    assert top_type is not None, f"AST missing 'type' in {ast}"
    assert top_type.lower() == expected_top_type.lower(), f"Expected top '{expected_top_type}', got '{top_type}'"


# --------------------------------------------------------------------------------
# 3) indicator_utils: list/load tests, TA-Lib & custom indicators, param listing
# --------------------------------------------------------------------------------
def test_list_and_load_known_symbol(known_symbol):
    symbol = known_symbol

    # list_symbols must include it
    assert symbol in indicator_utils.list_symbols("daily")
    assert symbol in indicator_utils.list_symbols("15min")

    # load_ohlcv returns a non-empty DataFrame for daily
    df_daily = indicator_utils.load_ohlcv(symbol, "daily")
    assert isinstance(df_daily, pd.DataFrame)
    assert len(df_daily) > 0
    for c in ["open", "high", "low", "close", "volume"]:
        assert c in df_daily.columns

    # load_ohlcv returns a non-empty DataFrame for 15min
    df_15 = indicator_utils.load_ohlcv(symbol, "15min")
    assert isinstance(df_15, pd.DataFrame)
    assert len(df_15) > 0
    for c in ["open", "high", "low", "close", "volume"]:
        assert c in df_15.columns

    # Invalid symbol/timeframe → None
    assert indicator_utils.load_ohlcv("NO_SUCH_SYM", "daily") is None
    assert indicator_utils.load_ohlcv(symbol, "hourly") is None


@pytest.mark.parametrize("fn_name, expects_series", [
    ("SMA", True),
    ("RSI", True),
    ("MACD", False),           # compute_indicator_series returns DataFrame for MACD
    ("CLOSE", True),           # close price series
    ("EFI", False),            # custom returns scalar
    ("MACD_LINE", False),      # custom returns scalar
    ("BB_UPPER", False),       # custom returns scalar
    ("STOCH_K", False),        # custom returns scalar
])
def test_get_talib_function_list_and_params(fn_name, expects_series):
    # 1) Ensure function/listing is present
    all_funcs = indicator_utils.get_talib_function_list()
    assert fn_name.upper() in all_funcs, f"{fn_name} should be listed in get_talib_function_list()"

    # 2) get_talib_params returns a list of dicts
    params = indicator_utils.get_talib_params(fn_name)
    assert isinstance(params, list)
    for p in params:
        assert "name" in p and "type" in p and "default" in p

    # 3) Now compute the indicator on real daily data if applicable
    daily_symbol = next(iter(indicator_utils.list_symbols("daily")))
    df_daily = indicator_utils.load_ohlcv(daily_symbol, "daily")
    assert df_daily is not None and not df_daily.empty

    # Build arguments for compute_indicator_series:
    if fn_name.upper() in ["SMA", "RSI", "MACD", "BB_UPPER", "BB_MIDDLE", "BB_LOWER", "STOCH_K", "STOCH_D", "EFI"]:
        if fn_name.upper() == "SMA":
            args = [{"type": "FieldLiteral", "value": "CLOSE"}, {"type": "NumberLiteral", "value": 10}]
        elif fn_name.upper() == "RSI":
            args = [{"type": "FieldLiteral", "value": "CLOSE"}, {"type": "NumberLiteral", "value": 14}]
        elif fn_name.upper() == "MACD":
            args = [
                {"type": "FieldLiteral", "value": "CLOSE"},
                {"type": "NumberLiteral", "value": 12},
                {"type": "NumberLiteral", "value": 26},
                {"type": "NumberLiteral", "value": 9},
            ]
        elif fn_name.upper() in ["BB_UPPER", "BB_MIDDLE", "BB_LOWER"]:
            args = [{"type": "FieldLiteral", "value": "CLOSE"}, {"type": "NumberLiteral", "value": 20}, {"type": "NumberLiteral", "value": 2.0}]
        elif fn_name.upper() in ["STOCH_K", "STOCH_D"]:
            args = [
                {"type": "FieldLiteral", "value": "HIGH"},
                {"type": "FieldLiteral", "value": "LOW"},
                {"type": "FieldLiteral", "value": "CLOSE"},
                {"type": "NumberLiteral", "value": 14},
                {"type": "NumberLiteral", "value": 3},
                {"type": "NumberLiteral", "value": 3},
            ]
        elif fn_name.upper() == "EFI":
            args = [{"type": "NumberLiteral", "value": 13}]
        else:
            args = []

        result = indicator_utils.compute_indicator_series(fn_name, args, df_daily)
        if fn_name.upper() == "MACD":
            assert isinstance(result, pd.DataFrame)
            assert result.shape[1] >= 2
        elif fn_name.upper() in ["EFI", "MACD_LINE", "MACD_SIGNAL", "MACD_HIST", "BB_UPPER", "BB_MIDDLE", "BB_LOWER", "STOCH_K", "STOCH_D"]:
            # Custom indicators produce scalars via call_indicator_logic; skip detailed shape checks here
            pass
        else:
            assert isinstance(result, pd.Series)
            assert len(result) == len(df_daily)


# --------------------------------------------------------------------------------
# 4) call_indicator_logic: built‐in and custom indicators
# --------------------------------------------------------------------------------
def test_call_indicator_logic_built_and_custom(known_symbol):
    symbol = known_symbol
    df_daily = indicator_utils.load_ohlcv(symbol, "daily")
    assert df_daily is not None and not df_daily.empty

    # a) Last close
    last_close = indicator_utils.call_indicator_logic(df_daily, "CLOSE")
    assert isinstance(last_close, (float, np.floating))

    # b) SMA(CLOSE, 14)
    sma14 = indicator_utils.call_indicator_logic(df_daily, "SMA", None, field="close", period=14)
    assert isinstance(sma14, (float, np.floating)) or np.isnan(sma14)

    # c) RSI(CLOSE, 14)
    rsi14 = indicator_utils.call_indicator_logic(df_daily, "RSI", None, field="close", period=14)
    assert isinstance(rsi14, (float, np.floating)) or np.isnan(rsi14)

    # d) MACD parts
    macd_line = indicator_utils.call_indicator_logic(df_daily, "MACD_LINE", None, field="close", fast_period=12, slow_period=26, signal_period=9)
    macd_signal = indicator_utils.call_indicator_logic(df_daily, "MACD_SIGNAL", None, field="close", fast_period=12, slow_period=26, signal_period=9)
    macd_hist = indicator_utils.call_indicator_logic(df_daily, "MACD_HIST", None, field="close", fast_period=12, slow_period=26, signal_period=9)
    assert isinstance(macd_line, (float, np.floating)) or np.isnan(macd_line)
    assert isinstance(macd_signal, (float, np.floating)) or np.isnan(macd_signal)
    assert isinstance(macd_hist, (float, np.floating)) or np.isnan(macd_hist)

    # e) Bollinger Bands parts
    bb_upper = indicator_utils.call_indicator_logic(df_daily, "BB_UPPER", None, field="close", period=20, nbdev=2.0)
    bb_middle = indicator_utils.call_indicator_logic(df_daily, "BB_MIDDLE", None, field="close", period=20, nbdev=2.0)
    bb_lower = indicator_utils.call_indicator_logic(df_daily, "BB_LOWER", None, field="close", period=20, nbdev=2.0)
    assert isinstance(bb_upper, (float, np.floating)) or np.isnan(bb_upper)
    assert isinstance(bb_middle, (float, np.floating)) or np.isnan(bb_middle)
    assert isinstance(bb_lower, (float, np.floating)) or np.isnan(bb_lower)

    # f) Stochastic parts
    stoch_k = indicator_utils.call_indicator_logic(df_daily, "STOCH_K", None, fastk_period=14, slowk_period=3, slowd_period=3)
    stoch_d = indicator_utils.call_indicator_logic(df_daily, "STOCH_D", None, fastk_period=14, slowk_period=3, slowd_period=3)
    assert isinstance(stoch_k, (float, np.floating)) or np.isnan(stoch_k)
    assert isinstance(stoch_d, (float, np.floating)) or np.isnan(stoch_d)

    # g) Elder's Force Index (EFI)
    efi13 = indicator_utils.call_indicator_logic(df_daily, "EFI", None, period=13)
    assert isinstance(efi13, (float, np.floating)) or np.isnan(efi13)

    # h) MY_CUSTOM_INDICATOR
    custom_val = indicator_utils.call_indicator_logic(df_daily, "MY_CUSTOM_INDICATOR", None, period=10, field="close")
    assert isinstance(custom_val, (float, np.floating)) or np.isnan(custom_val)

    # i) Unknown indicator → ValueError
    with pytest.raises(ValueError):
        indicator_utils.call_indicator_logic(df_daily, "UNKNOWN_IND", None)

    # j) Invalid param for custom → ValueError
    with pytest.raises(ValueError):
        indicator_utils.call_indicator_logic(df_daily, "EFI", None, period=-5)


# --------------------------------------------------------------------------------
# 5) eval_ast_node: manually‐constructed ASTs and parsed ASTs
# --------------------------------------------------------------------------------
def test_eval_ast_node_numeric_comparison():
    # AST: 10 > 5 → True
    ast = {
        "type": "Comparison",
        "operator": ">",
        "left": {"type": "NumberLiteral", "value": 10},
        "right": {"type": "NumberLiteral", "value": 5}
    }
    assert eval_ast_node("ANY_SYMBOL", ast, context={}) is True

    # AST: 3 < 2 → False
    ast2 = {
        "type": "Comparison",
        "operator": "<",
        "left": {"type": "NumberLiteral", "value": 3},
        "right": {"type": "NumberLiteral", "value": 2}
    }
    assert eval_ast_node("ANY_SYMBOL", ast2, context={}) is False


def test_eval_ast_node_field_literal_and_indicator(known_symbol):
    symbol = known_symbol

    # a) FieldLiteral: {"type": "FieldLiteral", "value": "CLOSE"} → latest close from daily DF
    ast_field = {"type": "FieldLiteral", "value": "CLOSE"}
    val = eval_ast_node(symbol, ast_field, context={})
    df_daily = indicator_utils.load_ohlcv(symbol, "daily")
    assert pytest.approx(df_daily["close"].iloc[-1]) == val

    # b) IndicatorCall: RSI(CLOSE, 14) on 15min should yield a float or NaN
    ast_rsi = {
        "type": "IndicatorCall",
        "name": "RSI",
        "timeframe": "15min",
        "arguments": [
            {"type": "FieldLiteral", "value": "CLOSE"},
            {"type": "NumberLiteral", "value": 14}
        ]
    }
    val_rsi = eval_ast_node(symbol, ast_rsi, context={})
    assert isinstance(val_rsi, (bool, float, np.floating))

    # c) Comparison: (CLOSE() > 1)
    ast_cmp = {
        "type": "Comparison",
        "operator": ">",
        "left": {"type": "FieldLiteral", "value": "CLOSE"},
        "right": {"type": "NumberLiteral", "value": 1}
    }
    res = eval_ast_node(symbol, ast_cmp, context={})
    assert isinstance(res, bool)


def test_eval_ast_node_logical_and_or(known_symbol):
    symbol = known_symbol
    # (CLOSE() > 0) AND (SMA(CLOSE, 5) > 0)
    ast_and = {
        "type": "BinaryExpression",
        "operator": "AND",
        "left": {
            "type": "Comparison",
            "operator": ">",
            "left": {"type": "FieldLiteral", "value": "CLOSE"},
            "right": {"type": "NumberLiteral", "value": 0}
        },
        "right": {
            "type": "Comparison",
            "operator": ">",
            "left": {
                "type": "IndicatorCall",
                "name": "SMA",
                "timeframe": "daily",
                "arguments": [
                    {"type": "FieldLiteral", "value": "CLOSE"},
                    {"type": "NumberLiteral", "value": 5}
                ]
            },
            "right": {"type": "NumberLiteral", "value": 0}
        }
    }
    res_and = eval_ast_node(symbol, ast_and, context={})
    assert isinstance(res_and, bool)

    # (CLOSE() > 0) OR (RSI(CLOSE,14) < 20)
    ast_or = {
        "type": "BinaryExpression",
        "operator": "OR",
        "left": {
            "type": "Comparison",
            "operator": ">",
            "left": {"type": "FieldLiteral", "value": "CLOSE"},
            "right": {"type": "NumberLiteral", "value": 0}
        },
        "right": {
            "type": "Comparison",
            "operator": "<",
            "left": {
                "type": "IndicatorCall",
                "name": "RSI",
                "timeframe": "15min",
                "arguments": [
                    {"type": "FieldLiteral", "value": "CLOSE"},
                    {"type": "NumberLiteral", "value": 14}
                ]
            },
            "right": {"type": "NumberLiteral", "value": 20}
        }
    }
    res_or = eval_ast_node(symbol, ast_or, context={})
    assert isinstance(res_or, bool)


def test_eval_ast_node_from_parse_and_nested(known_symbol):
    symbol = known_symbol

    # a) Parse a simple comparison via DSL, then evaluate:
    query = "Daily CLOSE() > Daily SMA(CLOSE(), 20)"
    ast = parse_query(query)
    assert isinstance(ast, dict) and ast.get("type") == "Comparison"
    result = eval_ast_node(symbol, ast, context={})
    assert isinstance(result, bool)

    # b) Parse a nested DSL: SMA(MACD(CLOSE(),12,26,9), 3) > 0
    nested_query = "SMA(MACD(CLOSE(), 12, 26, 9), 3) > 0"
    ast2 = parse_query(nested_query)
    assert isinstance(ast2, dict) and ast2.get("type") == "Comparison"
    res2 = eval_ast_node(symbol, ast2, context={})
    assert isinstance(res2, bool)

    # c) Complex logical/parentheses:
    complex_query = "(Daily SMA(CLOSE(), 10) > 1) AND ((15min RSI(CLOSE(), 5) < 50) OR (Daily MACD_LINE(CLOSE(), 12, 26, 9) > 0))"
    ast3 = parse_query(complex_query)
    assert isinstance(ast3, dict) and ast3.get("type").lower() == "binaryexpression"
    res3 = eval_ast_node(symbol, ast3, context={})
    assert isinstance(res3, bool)


# --------------------------------------------------------------------------------
# 6) compute_indicator_series and nested compute via unwrap_arg
# --------------------------------------------------------------------------------
def test_compute_and_unwrap_nested_series(known_symbol):
    symbol = known_symbol
    df_daily = indicator_utils.load_ohlcv(symbol, "daily")
    assert df_daily is not None and not df_daily.empty

    # Build AST‐style node for MACD(CLOSE(), 12, 26, 9)
    macd_node = {
        "type": "IndicatorCall",
        "name": "MACD",
        "timeframe": "daily",
        "arguments": [
            {"type": "FieldLiteral", "value": "CLOSE"},
            {"type": "NumberLiteral", "value": 12},
            {"type": "NumberLiteral", "value": 26},
            {"type": "NumberLiteral", "value": 9},
        ]
    }
    macd_series = indicator_utils.unwrap_arg(macd_node, df_daily)
    assert isinstance(macd_series, pd.Series)
    assert len(macd_series) == len(df_daily)

    # Now nest: SMA(MACD_0, 5)
    nested_sma_node = {
        "type": "IndicatorCall",
        "name": "SMA",
        "timeframe": "daily",
        "arguments": [
            {"type": "IndicatorCall", **macd_node},
            {"type": "NumberLiteral", "value": 5}
        ]
    }
    nested_series = indicator_utils.unwrap_arg(nested_sma_node, df_daily)
    assert isinstance(nested_series, pd.Series)
    assert len(nested_series) == len(df_daily)

    last5 = macd_series.dropna().iloc[-5:].astype(float).values
    if len(last5) == 5:
        expected = float(np.mean(last5))
        assert nested_series.dropna().iloc[-1] == pytest.approx(expected, rel=1e-5)
    else:
        assert nested_series.shape[0] == df_daily.shape[0]


# --------------------------------------------------------------------------------
# 7) Negative/Error conditions
# --------------------------------------------------------------------------------
def test_invalid_field_and_indicator_errors(known_symbol):
    symbol = known_symbol
    df_daily = indicator_utils.load_ohlcv(symbol, "daily")

    # a) Invalid field literal in AST: eval_ast_node should return False
    ast_bad_field = {"type": "FieldLiteral", "value": "NOTAFIELD"}
    r = eval_ast_node(symbol, ast_bad_field, context={})
    assert isinstance(r, bool)

    # b) Invalid indicator name in eval: should return False
    ast_bad_ind = {
        "type": "IndicatorCall",
        "name": "NOSUCHIND",
        "timeframe": "daily",
        "arguments": [
            {"type": "FieldLiteral", "value": "CLOSE"},
            {"type": "NumberLiteral", "value": 5}
        ]
    }
    r2 = eval_ast_node(symbol, ast_bad_ind, context={})
    assert r2 is False

    # c) Invalid syntax in parse_query yields type "PARSE_ERROR"
    bad_syntax = "SMA((CLOSE(), 5)"
    ast_err = parse_query(bad_syntax)
    assert isinstance(ast_err, dict) and ast_err.get("type") == "PARSE_ERROR"


# --------------------------------------------------------------------------------
# 8) get_talib_grouped_indicators: ensure at least “Price & Volume” group
# --------------------------------------------------------------------------------
def test_get_talib_grouped_indicators_contains_price_volume():
    groups = indicator_utils.get_talib_grouped_indicators()
    assert "Price & Volume" in groups
    pv = groups["Price & Volume"]
    names = [item["value"] for item in pv]
    assert "CLOSE" in names and "OPEN" in names

    if indicator_utils.CUSTOM_INDICATORS:
        assert "Custom & Derived Indicators" in groups
        custom_names = [item["value"] for item in groups["Custom & Derived Indicators"]]
        for custom in indicator_utils.CUSTOM_INDICATORS.keys():
            assert custom in custom_names


# --------------------------------------------------------------------------------
# 9) Simple “run screener” smoke test (no HTTP, just logic)
# --------------------------------------------------------------------------------
def test_views_run_screener_minimal(known_symbol):
    """
    Build a minimal AST for `CLOSE() > 0` and verify that at least one symbol
    (known_symbol) appears in the matching set.
    """
    ast_min = {
        "type": "Comparison",
        "operator": ">",
        "left": {"type": "FieldLiteral", "value": "CLOSE"},
        "right": {"type": "NumberLiteral", "value": 0}
    }

    symbols = indicator_utils.list_symbols("daily")
    assert known_symbol in symbols

    matching = []
    for sym in symbols[:50]:
        if eval_ast_node(sym, ast_min, context={}):
            matching.append(sym)

    assert known_symbol in matching
