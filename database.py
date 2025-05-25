import os
import re
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
from fyers_apiv3 import fyersModel

# PostgreSQL config
DB_NAME = "algo_trading"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

# Fyers config
ACCESS_TOKEN_FILE = r"credentials/access_token.txt"
CLIENT_ID_FILE = r"credentials/client_id.txt"
CSV_FILE = "midcap150.csv"  # Should contain 'symbol' column

def load_access_token():
    with open(ACCESS_TOKEN_FILE, "r") as f:
        return f.read().strip()

def load_client_id():
    with open(CLIENT_ID_FILE, "r") as f:
        return f.read().strip()

def clean_table_name(symbol: str) -> str:
    """
    Replace & with '_and_', then convert all non-alphanumeric to '_'.
    Ensures valid PostgreSQL table name from stock symbol.
    """
    symbol = symbol.replace("&", "_and_")
    return re.sub(r'\W+', '_', symbol).lower()

def fetch_ohlcv(symbol, resolution="D", start_date=(datetime.now() - timedelta(days=365))):
    fyers = fyersModel.FyersModel(client_id=load_client_id(), token=load_access_token(), is_async=False)
    end_date = datetime.now()
    all_data = []

    while start_date < end_date:
        to_date = min(start_date + timedelta(days=366), end_date)
        payload = {
            "symbol": symbol,
            "resolution": resolution,
            "date_format": 0,
            "range_from": int(start_date.timestamp()),
            "range_to": int(to_date.timestamp()),
            "cont_flag": "0",
        }
        try:
            res = fyers.history(data=payload)
            if res.get("s") == "ok":
                df = pd.DataFrame(res["candles"], columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s").dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
                all_data.append(df)
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
        start_date = to_date + timedelta(days=1)

    return pd.concat(all_data, ignore_index=True) if all_data else None

def store_to_postgres(symbol, df):
    table = clean_table_name(symbol)

    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            timestamp TIMESTAMP PRIMARY KEY,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume BIGINT
        )
    """)
    conn.commit()

    for _, row in df.iterrows():
        cur.execute(f"""
            INSERT INTO {table} (timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (timestamp) DO NOTHING
        """, tuple(row))

    conn.commit()
    cur.close()
    conn.close()

def main():
    symbols = pd.read_csv(CSV_FILE)['symbol'].dropna().tolist()
    print(f"⏳ Total symbols: {len(symbols)}")
    for symbol in symbols:
        print(f"📈 Fetching {symbol}...")
        df = fetch_ohlcv(symbol)
        if df is not None and not df.empty:
            store_to_postgres(symbol, df)
            print(f"✅ Stored {len(df)} rows for {symbol}")
        else:
            print(f"⚠️ No data for {symbol}")

if __name__ == "__main__":
    main()
