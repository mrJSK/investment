# Market Data Django App

## Overview

The `market_data` app is a core component of the investment analysis platform, responsible for fetching, storing, and managing all time-series market data from the Fyers API. It is designed to work in tandem with the `fundamentals` app, which provides the master list of symbols to track.

This app contains two primary functionalities, implemented as Django management commands:
1.  **Bulk Historical Data Fetching**: To backfill the database with historical OHLCV (Open, High, Low, Close, Volume) data.
2.  **Live Tick Data Streaming**: To capture real-time market data and prepare it for accumulation into various timeframes.

---

## Models

This app defines one central model for storing all candle data.

### `HistoricalData`

This model is designed to store OHLCV candles for every tracked symbol across all timeframes in a single, efficient table.

**Fields:**

| Field      | Type               | Description                                                                 |
| :--------- | :----------------- | :-------------------------------------------------------------------------- |
| `id`         | `CharField` (PK)   | A unique ID for each candle record, e.g., `NSE:SBIN-EQ_D_1690934400`.        |
| `symbol`     | `CharField`        | The full Fyers symbol format, e.g., `NSE:SBIN-EQ`. Indexed for fast lookups. |
| `timeframe`  | `CharField`        | The timeframe of the candle, e.g., `1`, `5`, `15`, `60`, `D`.                |
| `datetime`   | `DateTimeField`    | The timezone-aware timestamp for the start of the candle (in Asia/Kolkata). |
| `open`       | `FloatField`       | The opening price of the candle.                                            |
| `high`       | `FloatField`       | The highest price of the candle.                                            |
| `low`        | `FloatField`       | The lowest price of the candle.                                             |
| `close`      | `FloatField`       | The closing price of the candle.                                            |
| `volume`     | `BigIntegerField`  | The volume traded during the candle's duration.                             |

---