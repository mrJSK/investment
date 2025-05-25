import pandas as pd
import talib
import psycopg2
from django.conf import settings
from .models import Screener, ScreenerCondition
from .utils import clean_table_name

def fetch_ohlcv(table, limit=100):
    conn = psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )
    df = pd.read_sql(f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT %s", conn, params=(limit,))
    conn.close()
    return df.sort_values("timestamp")

def apply_ta_indicators(df):
    df['sma'] = talib.SMA(df['close'], timeperiod=20)
    df['ema'] = talib.EMA(df['close'], timeperiod=20)
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], _, _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    return df

def run_screener(screener_id):
    screener = Screener.objects.get(id=screener_id)
    conditions = screener.conditions.all()
    symbols = pd.read_csv("midcap150.csv")['symbol'].dropna().tolist()

    matches = []

    for symbol in symbols:
        try:
            table = clean_table_name(symbol)
            df = fetch_ohlcv(table)
            df = apply_ta_indicators(df)
            row = df.iloc[-1]

            exprs = []
            for cond in conditions:
                lhs = row[cond.left_indicator]
                rhs = row[cond.right_indicator] if cond.right_indicator else cond.constant
                exprs.append(f"({lhs} {cond.operator} {rhs})")
                if cond.logic_with_next:
                    exprs.append(cond.logic_with_next)

            if eval(" ".join(exprs)):
                matches.append(symbol)

        except Exception as e:
            print(f"Error: {symbol} - {e}")

    return matches
