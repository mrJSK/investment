# from django.core.management.base import BaseCommand
# from ...models import OHLCData, OpenTrade, ClosedTrade, Scrip
# from datetime import datetime
# import pandas as pd
# import numpy as np
# import time


# class Command(BaseCommand):
#     help = "Simulate trading using stored OHLCV data with Dow Theory and EMA strategy."

#     def add_arguments(self, parser):
#         parser.add_argument(
#             "--delay",
#             type=int,
#             default=5,
#             help="Time delay (in seconds) between processing each OHLCV record.",
#         )

#     def handle(self, *args, **options):
#         delay = options["delay"]
#         self.stdout.write(f"Starting Dow Theory + EMA trading simulation with {delay}s delay...")

#         try:
#             # Fetch all symbols
#             symbols = list(Scrip.objects.values_list("symbol", flat=True))
#             for symbol in symbols:
#                 self.stdout.write(f"Simulating for {symbol}...")
#                 self.simulate_trading_for_symbol(symbol, delay)
#         except KeyboardInterrupt:
#             self.stdout.write("Simulation stopped.")
#         except Exception as e:
#             self.stderr.write(f"Error: {str(e)}")

#     def simulate_trading_for_symbol(self, symbol, delay):
#         """
#         Simulate trading for a single symbol using stored OHLCV data.
#         """
#         # Fetch historical OHLCV data for the symbol
#         historical_data = list(
#             OHLCData.objects.filter(scrip__symbol=symbol).order_by("timestamp")
#         )

#         if not historical_data:
#             self.stdout.write(f"No historical data available for {symbol}.")
#             return

#         df = pd.DataFrame([{
#             "timestamp": ohlc.timestamp,
#             "open": ohlc.open,
#             "high": ohlc.high,
#             "low": ohlc.low,
#             "close": ohlc.close,
#             "volume": ohlc.volume
#         } for ohlc in historical_data])

#         # Execute Dow Theory + EMA strategy
#         trades = self.execute_dow_ema_strategy(df)

#         # Process each trade with a delay
#         for trade in trades:
#             self.stdout.write(
#                 f"Processing {symbol} | {trade['Type']} trade: Entry {trade['Entry Price']} at {trade['Entry Time']} | "
#                 f"Exit {trade['Exit Price']} at {trade['Exit Time']} | Profit: {trade['Profit % After Brokerage']:.2f}%"
#             )
#             time.sleep(delay)

#     def execute_dow_ema_strategy(self, data):
#         """
#         Execute Dow Theory + EMA-based trading strategy with swing high/low and stop loss.
#         """
#         # Parameters
#         ema_short_length = 9
#         ema_long_length = 26
#         swing_length = 5
#         stop_loss_pct = 1.0  # 1% stop loss

#         # Calculate EMAs
#         data['ema_short'] = data['close'].ewm(span=ema_short_length, adjust=False).mean()
#         data['ema_long'] = data['close'].ewm(span=ema_long_length, adjust=False).mean()

#         # Identify swing highs and lows
#         data['swing_high'] = data['close'][data['close'] == data['close'].rolling(swing_length, center=True).max()]
#         data['swing_low'] = data['close'][data['close'] == data['close'].rolling(swing_length, center=True).min()]

#         # Generate signals
#         data['signal'] = 0
#         data['signal'] = np.where(
#             (data['ema_short'] > data['ema_long']) & (data['swing_low'].notnull()), 1, data['signal']
#         )
#         data['signal'] = np.where(
#             (data['ema_short'] < data['ema_long']) & (data['swing_high'].notnull()), -1, data['signal']
#         )

#         # Process trades
#         trades = []
#         position = None
#         entry_price = None
#         entry_time = None
#         stop_loss_price = None

#         for i in range(len(data)):
#             if position is None:  # No open trade
#                 if data['signal'].iloc[i] == 1:  # Long entry
#                     position = "LONG"
#                     entry_price = data['close'].iloc[i]
#                     entry_time = data['timestamp'].iloc[i]
#                     stop_loss_price = entry_price * (1 - stop_loss_pct / 100)
#                 elif data['signal'].iloc[i] == -1:  # Short entry
#                     position = "SHORT"
#                     entry_price = data['close'].iloc[i]
#                     entry_time = data['timestamp'].iloc[i]
#                     stop_loss_price = entry_price * (1 + stop_loss_pct / 100)
#             else:  # Open trade exists
#                 if position == "LONG":
#                     if data['low'].iloc[i] <= stop_loss_price or data['signal'].iloc[i] == -1:  # Stop-loss or short signal
#                         exit_price = stop_loss_price if data['low'].iloc[i] <= stop_loss_price else data['close'].iloc[i]
#                         exit_time = data['timestamp'].iloc[i]
#                         profit_pct = (exit_price / entry_price - 1) * 100
#                         trades.append({
#                             "Type": "LONG",
#                             "Entry Price": entry_price,
#                             "Entry Time": entry_time,
#                             "Exit Price": exit_price,
#                             "Exit Time": exit_time,
#                             "Profit % After Brokerage": profit_pct,
#                         })
#                         position = None
#                 elif position == "SHORT":
#                     if data['high'].iloc[i] >= stop_loss_price or data['signal'].iloc[i] == 1:  # Stop-loss or long signal
#                         exit_price = stop_loss_price if data['high'].iloc[i] >= stop_loss_price else data['close'].iloc[i]
#                         exit_time = data['timestamp'].iloc[i]
#                         profit_pct = (entry_price / exit_price - 1) * 100
#                         trades.append({
#                             "Type": "SHORT",
#                             "Entry Price": entry_price,
#                             "Entry Time": entry_time,
#                             "Exit Price": exit_price,
#                             "Exit Time": exit_time,
#                             "Profit % After Brokerage": profit_pct,
#                         })
#                         position = None

#         return trades
# from django.core.management.base import BaseCommand
# from ...models import OHLCData, OpenTrade, ClosedTrade, Scrip
# from datetime import datetime
# import pandas as pd
# import numpy as np
# import time


# class Command(BaseCommand):
#     help = "Simulate trading using stored OHLCV data with Dow Theory and EMA strategy."

#     def add_arguments(self, parser):
#         parser.add_argument(
#             "--delay",
#             type=int,
#             default=5,
#             help="Time delay (in seconds) between processing each OHLCV record.",
#         )

#     def handle(self, *args, **options):
#         delay = options["delay"]
#         self.stdout.write(f"Starting Dow Theory + EMA trading simulation with {delay}s delay...")

#         try:
#             # Fetch all symbols
#             symbols = list(Scrip.objects.values_list("symbol", flat=True))
#             for symbol in symbols:
#                 self.stdout.write(f"Simulating for {symbol}...")
#                 self.simulate_trading_for_symbol(symbol, delay)
#         except KeyboardInterrupt:
#             self.stdout.write("Simulation stopped.")
#         except Exception as e:
#             self.stderr.write(f"Error: {str(e)}")

#     def simulate_trading_for_symbol(self, symbol, delay):
#         """
#         Simulate trading for a single symbol using stored OHLCV data.
#         """
#         # Fetch historical OHLCV data for the symbol
#         historical_data = list(
#             OHLCData.objects.filter(scrip__symbol=symbol).order_by("timestamp")
#         )

#         if not historical_data:
#             self.stdout.write(f"No historical data available for {symbol}.")
#             return

#         df = pd.DataFrame([{
#             "timestamp": ohlc.timestamp,
#             "open": ohlc.open,
#             "high": ohlc.high,
#             "low": ohlc.low,
#             "close": ohlc.close,
#             "volume": ohlc.volume
#         } for ohlc in historical_data])

#         # Execute Dow Theory + EMA strategy
#         trades = self.execute_dow_ema_strategy(df, symbol)

#         # Process each trade with a delay
#         for trade in trades:
#             self.stdout.write(
#                 f"Processing {symbol} | {trade['Type']} trade: Entry {trade['Entry Price']} at {trade['Entry Time']} | "
#                 f"Exit {trade['Exit Price']} at {trade['Exit Time']} | Profit: {trade['Profit % After Brokerage']:.2f}%"
#             )
#             time.sleep(delay)

#     def execute_dow_ema_strategy(self, data, symbol):
#         """
#         Execute Dow Theory + EMA-based trading strategy with swing high/low and stop loss.
#         """
#         # Parameters
#         ema_short_length = 9
#         ema_long_length = 26
#         swing_length = 5
#         stop_loss_pct = 1.0  # 1% stop loss

#         # Calculate EMAs
#         data['ema_short'] = data['close'].ewm(span=ema_short_length, adjust=False).mean()
#         data['ema_long'] = data['close'].ewm(span=ema_long_length, adjust=False).mean()

#         # Identify swing highs and lows
#         data['swing_high'] = data['close'][data['close'] == data['close'].rolling(swing_length, center=True).max()]
#         data['swing_low'] = data['close'][data['close'] == data['close'].rolling(swing_length, center=True).min()]

#         # Generate signals
#         data['signal'] = 0
#         data['signal'] = np.where(
#             (data['ema_short'] > data['ema_long']) & (data['swing_low'].notnull()), 1, data['signal']
#         )
#         data['signal'] = np.where(
#             (data['ema_short'] < data['ema_long']) & (data['swing_high'].notnull()), -1, data['signal']
#         )

#         # Process trades
#         trades = []
#         position = None
#         entry_price = None
#         entry_time = None
#         stop_loss_price = None
#         scrip = Scrip.objects.get(symbol=symbol)

#         for i in range(len(data)):
#             if position is None:  # No open trade
#                 if data['signal'].iloc[i] == 1:  # Long entry
#                     position = "LONG"
#                     entry_price = data['close'].iloc[i]
#                     entry_time = data['timestamp'].iloc[i]
#                     stop_loss_price = entry_price * (1 - stop_loss_pct / 100)

#                     # Save the LONG trade as an open trade
#                     OpenTrade.objects.create(
#                         scrip=scrip,
#                         entry_price=entry_price,
#                         entry_time=entry_time,
#                         quantity=10,  # Fixed quantity
#                         stop_loss_price=stop_loss_price,
#                         position_type="LONG",
#                     )

#                 elif data['signal'].iloc[i] == -1:  # Short entry
#                     position = "SHORT"
#                     entry_price = data['close'].iloc[i]
#                     entry_time = data['timestamp'].iloc[i]
#                     stop_loss_price = entry_price * (1 + stop_loss_pct / 100)

#                     # Save the SHORT trade as an open trade
#                     OpenTrade.objects.create(
#                         scrip=scrip,
#                         entry_price=entry_price,
#                         entry_time=entry_time,
#                         quantity=10,  # Fixed quantity
#                         stop_loss_price=stop_loss_price,
#                         position_type="SHORT",
#                     )

#             else:  # Open trade exists
#                 if position == "LONG":
#                     if data['low'].iloc[i] <= stop_loss_price or data['signal'].iloc[i] == -1:  # Stop-loss or short signal
#                         exit_price = stop_loss_price if data['low'].iloc[i] <= stop_loss_price else data['close'].iloc[i]
#                         exit_time = data['timestamp'].iloc[i]
#                         profit_pct = (exit_price / entry_price - 1) * 100
#                         trades.append({
#                             "Type": "LONG",
#                             "Entry Price": entry_price,
#                             "Entry Time": entry_time,
#                             "Exit Price": exit_price,
#                             "Exit Time": exit_time,
#                             "Profit % After Brokerage": profit_pct,
#                         })

#                         # Save the closed trade
#                         ClosedTrade.objects.create(
#                             scrip=scrip,
#                             entry_price=entry_price,
#                             exit_price=exit_price,
#                             entry_time=entry_time,
#                             exit_time=exit_time,
#                             quantity=10,  # Fixed quantity
#                             position_type="LONG",
#                             profit=(exit_price - entry_price) * 10,
#                             strategy="Dow + EMA Crossover",
#                         )

#                         position = None

#                 elif position == "SHORT":
#                     if data['high'].iloc[i] >= stop_loss_price or data['signal'].iloc[i] == 1:  # Stop-loss or long signal
#                         exit_price = stop_loss_price if data['high'].iloc[i] >= stop_loss_price else data['close'].iloc[i]
#                         exit_time = data['timestamp'].iloc[i]
#                         profit_pct = (entry_price / exit_price - 1) * 100
#                         trades.append({
#                             "Type": "SHORT",
#                             "Entry Price": entry_price,
#                             "Entry Time": entry_time,
#                             "Exit Price": exit_price,
#                             "Exit Time": exit_time,
#                             "Profit % After Brokerage": profit_pct,
#                         })

#                         # Save the closed trade
#                         ClosedTrade.objects.create(
#                             scrip=scrip,
#                             entry_price=entry_price,
#                             exit_price=exit_price,
#                             entry_time=entry_time,
#                             exit_time=exit_time,
#                             quantity=10,  # Fixed quantity
#                             position_type="SHORT",
#                             profit=(entry_price - exit_price) * 10,
#                             strategy="Dow + EMA Crossover",
#                         )

#                         position = None

#         return trades

# Latest Working Version Below

# from django.core.management.base import BaseCommand
# from ...models import OHLCData, OpenTrade, ClosedTrade, Scrip
# from datetime import datetime
# import pandas as pd
# import numpy as np
# import time


# class Command(BaseCommand):
#     help = "Simulate trading using stored OHLCV data with Dow Theory and EMA strategy."

#     def add_arguments(self, parser):
#         parser.add_argument(
#             "--delay",
#             type=int,
#             default=5,
#             help="Time delay (in seconds) between processing each OHLCV record.",
#         )

#     def handle(self, *args, **options):
#         delay = options["delay"]
#         self.stdout.write(f"Starting Dow Theory + EMA trading simulation with {delay}s delay...")

#         try:
#             # Fetch all symbols from the Scrip table
#             symbols = list(Scrip.objects.values_list("symbol", flat=True))
#             for symbol in symbols:
#                 self.stdout.write(f"Simulating for {symbol}...")
#                 self.simulate_trading_for_symbol(symbol, delay)
#         except KeyboardInterrupt:
#             self.stdout.write("Simulation stopped.")
#         except Exception as e:
#             self.stderr.write(f"Error: {str(e)}")

#     def simulate_trading_for_symbol(self, symbol, delay):
#         """
#         Simulate trading for a single symbol using stored OHLCV data.
#         """
#         # Fetch historical OHLCV data for the symbol
#         historical_data = list(
#             OHLCData.objects.filter(scrip__symbol=symbol).order_by("timestamp")
#         )

#         if not historical_data:
#             self.stdout.write(f"No historical data available for {symbol}.")
#             return

#         df = pd.DataFrame([{
#             "timestamp": ohlc.timestamp,
#             "open": ohlc.open,
#             "high": ohlc.high,
#             "low": ohlc.low,
#             "close": ohlc.close,
#             "volume": ohlc.volume
#         } for ohlc in historical_data])

#         # Execute Dow Theory + EMA strategy
#         trades = self.execute_dow_ema_strategy(df, symbol)

#         # Process each trade with a delay
#         for trade in trades:
#             self.stdout.write(
#                 f"Processing {symbol} | {trade['Type']} trade: Entry {trade['Entry Price']} at {trade['Entry Time']} | "
#                 f"Exit {trade['Exit Price']} at {trade['Exit Time']} | Profit: {trade['Profit % After Brokerage']:.2f}%"
#             )
#             time.sleep(delay)

#     def execute_dow_ema_strategy(self, data, symbol):
#         """
#         Execute Dow Theory + EMA-based trading strategy with swing high/low and stop loss.
#         """
#         # Parameters
#         ema_short_length = 9
#         ema_long_length = 26
#         swing_length = 5
#         stop_loss_pct = 1.0  # 1% stop loss

#         # Calculate EMAs
#         data['ema_short'] = data['close'].ewm(span=ema_short_length, adjust=False).mean()
#         data['ema_long'] = data['close'].ewm(span=ema_long_length, adjust=False).mean()

#         # Identify swing highs and lows
#         data['swing_high'] = data['close'][data['close'] == data['close'].rolling(swing_length, center=True).max()]
#         data['swing_low'] = data['close'][data['close'] == data['close'].rolling(swing_length, center=True).min()]

#         # Generate signals
#         data['signal'] = 0
#         data['signal'] = np.where(
#             (data['ema_short'] > data['ema_long']) & (data['swing_low'].notnull()), 1, data['signal']
#         )
#         data['signal'] = np.where(
#             (data['ema_short'] < data['ema_long']) & (data['swing_high'].notnull()), -1, data['signal']
#         )

#         # Process trades
#         trades = []
#         position = None
#         entry_price = None
#         entry_time = None
#         stop_loss_price = None
#         scrip = Scrip.objects.get(symbol=symbol)

#         for i in range(len(data)):
#             if position is None:  # No open trade
#                 if data['signal'].iloc[i] == 1:  # Long entry
#                     position = "LONG"
#                     entry_price = data['close'].iloc[i]
#                     entry_time = data['timestamp'].iloc[i]
#                     stop_loss_price = entry_price * (1 - stop_loss_pct / 100)

#                     # Save the LONG trade as an open trade
#                     OpenTrade.objects.create(
#                         scrip=scrip,
#                         entry_price=entry_price,
#                         entry_time=entry_time,
#                         quantity=10,  # Fixed quantity
#                         stop_loss_price=stop_loss_price,
#                         position_type="LONG",
#                     )
#                     self.stdout.write(f"Buy signal generated for {symbol}. Placing LONG order at {entry_price}.")

#                 elif data['signal'].iloc[i] == -1:  # Short entry
#                     position = "SHORT"
#                     entry_price = data['close'].iloc[i]
#                     entry_time = data['timestamp'].iloc[i]
#                     stop_loss_price = entry_price * (1 + stop_loss_pct / 100)

#                     # Save the SHORT trade as an open trade
#                     OpenTrade.objects.create(
#                         scrip=scrip,
#                         entry_price=entry_price,
#                         entry_time=entry_time,
#                         quantity=10,  # Fixed quantity
#                         stop_loss_price=stop_loss_price,
#                         position_type="SHORT",
#                     )
#                     self.stdout.write(f"Sell signal generated for {symbol}. Placing SHORT order at {entry_price}.")

#             else:  # Open trade exists
#                 if position == "LONG":
#                     if data['low'].iloc[i] <= stop_loss_price or data['signal'].iloc[i] == -1:  # Stop-loss or short signal
#                         exit_price = stop_loss_price if data['low'].iloc[i] <= stop_loss_price else data['close'].iloc[i]
#                         exit_time = data['timestamp'].iloc[i]
#                         profit_pct = (exit_price / entry_price - 1) * 100
#                         trades.append({
#                             "Type": "LONG",
#                             "Entry Price": entry_price,
#                             "Entry Time": entry_time,
#                             "Exit Price": exit_price,
#                             "Exit Time": exit_time,
#                             "Profit % After Brokerage": profit_pct,
#                         })

#                         # Save the closed trade
#                         ClosedTrade.objects.create(
#                             scrip=scrip,
#                             entry_price=entry_price,
#                             exit_price=exit_price,
#                             entry_time=entry_time,
#                             exit_time=exit_time,
#                             quantity=10,  # Fixed quantity
#                             position_type="LONG",
#                             profit=(exit_price - entry_price) * 10,
#                             strategy="Dow + EMA Crossover",
#                         )
#                         self.stdout.write(f"LONG trade closed for {symbol} at {exit_price}. Profit: {profit_pct:.2f}%")
#                         position = None

#                 elif position == "SHORT":
#                     if data['high'].iloc[i] >= stop_loss_price or data['signal'].iloc[i] == 1:  # Stop-loss or long signal
#                         exit_price = stop_loss_price if data['high'].iloc[i] >= stop_loss_price else data['close'].iloc[i]
#                         exit_time = data['timestamp'].iloc[i]
#                         profit_pct = (entry_price / exit_price - 1) * 100
#                         trades.append({
#                             "Type": "SHORT",
#                             "Entry Price": entry_price,
#                             "Entry Time": entry_time,
#                             "Exit Price": exit_price,
#                             "Exit Time": exit_time,
#                             "Profit % After Brokerage": profit_pct,
#                         })

#                         # Save the closed trade
#                         ClosedTrade.objects.create(
#                             scrip=scrip,
#                             entry_price=entry_price,
#                             exit_price=exit_price,
#                             entry_time=entry_time,
#                             exit_time=exit_time,
#                             quantity=10,  # Fixed quantity
#                             position_type="SHORT",
#                             profit=(entry_price - exit_price) * 10,
#                             strategy="Dow + EMA Crossover",
#                         )
#                         self.stdout.write(f"SHORT trade closed for {symbol} at {exit_price}. Profit: {profit_pct:.2f}%")
#                         position = None

#         return trades


# from django.core.management.base import BaseCommand
# from django.db import connection, IntegrityError
# from login.models import Scrip, OpenTrade, ClosedTrade
# from datetime import datetime
# import pandas as pd
# import numpy as np
# import time
# from concurrent.futures import ThreadPoolExecutor
# from zoneinfo import ZoneInfo as timezone

# class Command(BaseCommand):
#     help = "Simulate trading using stored OHLCV data with Dow Theory and EMA strategy."

#     def add_arguments(self, parser):
#         parser.add_argument("--delay", type=int, default=1, help="Time delay (in seconds).")
#         parser.add_argument("--threads", type=int, default=4, help="Number of threads.")

#     def handle(self, *args, **options):
#         delay = options["delay"]
#         threads = options["threads"]
#         self.stdout.write(f"Starting simulation with {delay}s delay using {threads} threads...")

#         ohlc_tables = self.get_ohlc_tables()
#         if not ohlc_tables:
#             self.stdout.write(self.style.ERROR("No OHLC tables found."))
#             return

#         with ThreadPoolExecutor(max_workers=threads) as executor:
#             for table in ohlc_tables:
#                 executor.submit(self.simulate_trading_for_table, table, delay)

#     def get_ohlc_tables(self):
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'ohlc_nse_%';")
#             return [row[0] for row in cursor.fetchall()]

#     def table_to_symbol(self, table_name):
#         return table_name.replace("ohlc_", "").replace("_", ":").replace(":eq", "-EQ").upper()

#     def simulate_trading_for_table(self, table_name, delay):
#         symbol = self.table_to_symbol(table_name)
#         self.stdout.write(f"Simulating trades for {symbol}...")

#         data = self.fetch_table_data(table_name)
#         if data.empty:
#             self.stdout.write(f"No data for {symbol}.")
#             return

#         trades = self.execute_dow_ema_strategy(data, symbol)

#         for trade in trades:
#             self.save_trade(symbol, trade)
#             if trade:  # Check if trade is not None
#                 self.stdout.write(
#                     f"Processed {symbol} | {trade['Type']} trade: Entry {trade['Entry Price']} at {trade['Entry Time']} | "
#                     f"Exit {trade['Exit Price']} at {trade['Exit Time']} | Profit: {trade['Profit % After Brokerage']:.2f}%"
#                 )
#                 time.sleep(delay)

#     def fetch_table_data(self, table_name):
#         query = f"SELECT timestamp, open, high, low, close, volume FROM {table_name} ORDER BY timestamp;"
#         with connection.cursor() as cursor:
#             cursor.execute(query)
#             rows = cursor.fetchall()
#         return pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])

#     def execute_dow_ema_strategy(self, data, symbol):
#         ema_short_length = 9
#         ema_long_length = 26
#         swing_length = 5
#         stop_loss_pct = 1.0

#         data['ema_short'] = data['close'].ewm(span=ema_short_length, adjust=False).mean()
#         data['ema_long'] = data['close'].ewm(span=ema_long_length, adjust=False).mean()

#         data['swing_high'] = data['close'][data['close'] == data['close'].rolling(swing_length, center=True).max()]
#         data['swing_low'] = data['close'][data['close'] == data['close'].rolling(swing_length, center=True).min()]

#         data['signal'] = 0
#         data['signal'] = np.where(
#             (data['ema_short'] > data['ema_long']) & (data['swing_low'].notnull()), 1, data['signal']
#         )
#         data['signal'] = np.where(
#             (data['ema_short'] < data['ema_long']) & (data['swing_high'].notnull()), -1, data['signal']
#         )

#         trades = []
#         position = None
#         entry_price, entry_time, stop_loss_price = None, None, None

#         for i in range(len(data)):
#             if position is None:
#                 if data['signal'].iloc[i] == 1:
#                     position = "LONG"
#                     entry_price, entry_time = data['close'].iloc[i], data['timestamp'].iloc[i]
#                     stop_loss_price = entry_price * (1 - stop_loss_pct / 100)
#                 elif data['signal'].iloc[i] == -1:
#                     position = "SHORT"
#                     entry_price, entry_time = data['close'].iloc[i], data['timestamp'].iloc[i]
#                     stop_loss_price = entry_price * (1 + stop_loss_pct / 100)
#             else:
#                 if position == "LONG" and (data['low'].iloc[i] <= stop_loss_price or data['signal'].iloc[i] == -1):
#                     exit_price = stop_loss_price if data['low'].iloc[i] <= stop_loss_price else data['close'].iloc[i]
#                     trades.append(self.create_trade("LONG", entry_price, entry_time, exit_price, data['timestamp'].iloc[i], symbol))
#                     position = None
#                 elif position == "SHORT" and (data['high'].iloc[i] >= stop_loss_price or data['signal'].iloc[i] == 1):
#                     exit_price = stop_loss_price if data['high'].iloc[i] >= stop_loss_price else data['close'].iloc[i]
#                     trades.append(self.create_trade("SHORT", entry_price, entry_time, exit_price, data['timestamp'].iloc[i], symbol))
#                     position = None

#         return trades

#     def create_trade(self, trade_type, entry_price, entry_time, exit_price, exit_time, symbol):
#         profit_pct = ((exit_price / entry_price - 1) * 100) if trade_type == "LONG" else ((entry_price / exit_price - 1) * 100)
#         try:
#             scrip = Scrip.objects.get(symbol=symbol)
#         except Scrip.DoesNotExist:
#             self.stdout.write(self.style.ERROR(f"Scrip with symbol {symbol} not found!"))
#             return None

#         return {
#             "Type": trade_type,
#             "Entry Price": entry_price,
#             "Entry Time": entry_time,
#             "Exit Price": exit_price,
#             "Exit Time": exit_time,
#             "Profit % After Brokerage": profit_pct,
#             "scrip": scrip,
#         }

#     def save_trade(self, symbol, trade):
#         if trade is None:
#             return

#         try:
#             if trade["Type"] == "LONG":
#                 ClosedTrade.objects.create(
#                     scrip=trade["scrip"],
#                     entry_price=trade["Entry Price"],
#                     exit_price=trade["Exit Price"],
#                     entry_time=trade["Entry Time"],
#                     exit_time=trade["Exit Time"],
#                     quantity=10,
#                     position_type="LONG",
#                     profit=(trade["Exit Price"] - trade["Entry Price"]) * 10,
#                 )
#             elif trade["Type"] == "SHORT":
#                 ClosedTrade.objects.create(
#                     scrip=trade["scrip"],
#                     entry_price=trade["Entry Price"],
#                     exit_price=trade["Exit Price"],
#                     entry_time=trade["Entry Time"],
#                     exit_time=trade["Exit Time"],
#                     quantity=10,
#                     position_type="SHORT",
#                     profit=(trade["Entry Price"] - trade["Exit Price"]) * 10,
#                 )
#             self.stdout.write(self.style.SUCCESS(f"Trade for {symbol} saved."))

#         except IntegrityError as e:
#             self.stdout.write(self.style.ERROR(f"Integrity Error saving trade for {symbol}: {e}"))
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f"General Error saving trade for {symbol}: {e}"))

import asyncio
from django.core.management.base import BaseCommand
from django.db import connection, IntegrityError
from login.models import Scrip, OpenTrade, ClosedTrade
from datetime import datetime
import pandas as pd
import numpy as np
from asgiref.sync import sync_to_async
from zoneinfo import ZoneInfo as timezone

class Command(BaseCommand):
    help = "Simulate trading using stored OHLCV data with Dow Theory and EMA strategy."

    def add_arguments(self, parser):
        parser.add_argument("--delay", type=int, default=1, help="Time delay (in seconds).")

    async def handle(self, *args, **options):
        delay = options["delay"]
        self.stdout.write(f"Starting simulation with {delay}s delay using async...")

        ohlc_tables = await sync_to_async(self.get_ohlc_tables)()
        if not ohlc_tables:
            self.stdout.write(self.style.ERROR("No OHLC tables found."))
            return

        tasks = [self.simulate_trading_for_table(table, delay) for table in ohlc_tables]
        await asyncio.gather(*tasks)

    def get_ohlc_tables(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'ohlc_nse_%';")
            return [row[0] for row in cursor.fetchall()]

    def table_to_symbol(self, table_name):
        return table_name.replace("ohlc_", "").replace("_", ":").replace(":eq", "-EQ").upper()

    async def simulate_trading_for_table(self, table_name, delay):
        symbol = self.table_to_symbol(table_name)
        self.stdout.write(f"Simulating trades for {symbol}...")

        data = await sync_to_async(self.fetch_table_data)(table_name)
        if data.empty:
            self.stdout.write(f"No data for {symbol}.")
            return

        trades = await self.execute_dow_ema_strategy(data, symbol)

        for trade in trades:
            await self.save_trade(symbol, trade)
            if trade:
                self.stdout.write(
                    f"Processed {symbol} | {trade['Type']} trade: Entry {trade['Entry Price']} at {trade['Entry Time']} | "
                    f"Exit {trade['Exit Price']} at {trade['Exit Time']} | Profit: {trade['Profit % After Brokerage']:.2f}%"
                )
                await asyncio.sleep(delay)

    def fetch_table_data(self, table_name):
        query = f"SELECT timestamp, open, high, low, close, volume FROM {table_name} ORDER BY timestamp;"
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])

    async def execute_dow_ema_strategy(self, data, symbol):
        ema_short_length = 9
        ema_long_length = 26
        swing_length = 5
        stop_loss_pct = 1.0

        data['ema_short'] = data['close'].ewm(span=ema_short_length, adjust=False).mean()
        data['ema_long'] = data['close'].ewm(span=ema_long_length, adjust=False).mean()

        data['swing_high'] = data['close'][data['close'] == data['close'].rolling(swing_length, center=True).max()]
        data['swing_low'] = data['close'][data['close'] == data['close'].rolling(swing_length, center=True).min()]

        data['signal'] = 0
        data['signal'] = np.where(
            (data['ema_short'] > data['ema_long']) & (data['swing_low'].notnull()), 1, data['signal']
        )
        data['signal'] = np.where(
            (data['ema_short'] < data['ema_long']) & (data['swing_high'].notnull()), -1, data['signal']
        )

        trades = []
        position = None
        entry_price, entry_time, stop_loss_price = None, None, None

        for i in range(len(data)):
            if position is None:
                if data['signal'].iloc[i] == 1:
                    position = "LONG"
                    entry_price, entry_time = data['close'].iloc[i], data['timestamp'].iloc[i]
                    stop_loss_price = entry_price * (1 - stop_loss_pct / 100)
                elif data['signal'].iloc[i] == -1:
                    position = "SHORT"
                    entry_price, entry_time = data['close'].iloc[i], data['timestamp'].iloc[i]
                    stop_loss_price = entry_price * (1 + stop_loss_pct / 100)
            else:
                if position == "LONG" and (data['low'].iloc[i] <= stop_loss_price or data['signal'].iloc[i] == -1):
                    exit_price = stop_loss_price if data['low'].iloc[i] <= stop_loss_price else data['close'].iloc[i]
                    trades.append(await self.create_trade("LONG", entry_price, entry_time, exit_price, data['timestamp'].iloc[i], symbol))
                    position = None
                elif position == "SHORT" and (data['high'].iloc[i] >= stop_loss_price or data['signal'].iloc[i] == 1):
                    exit_price = stop_loss_price if data['high'].iloc[i] >= stop_loss_price else data['close'].iloc[i]
                    trades.append(await self.create_trade("SHORT", entry_price, entry_time, exit_price, data['timestamp'].iloc[i], symbol))
                    position = None

        return trades

    async def create_trade(self, trade_type, entry_price, entry_time, exit_price, exit_time, symbol):
        profit_pct = ((exit_price / entry_price - 1) * 100) if trade_type == "LONG" else ((entry_price / exit_price - 1) * 100)
        
        scrip = await sync_to_async(Scrip.objects.get)(symbol=symbol)  

        return {
            "Type": trade_type,
            "Entry Price": entry_price,
            "Entry Time": entry_time,
            "Exit Price": exit_price,
            "Exit Time": exit_time,
            "Profit % After Brokerage": profit_pct,
            "scrip": scrip,
        }

    @sync_to_async
    def save_trade(self, symbol, trade):
        if trade is None:
            return

        try:
            if trade["Type"] == "LONG":
                ClosedTrade.objects.create(
                    scrip=trade["scrip"],
                    entry_price=trade["Entry Price"],
                    exit_price=trade["Exit Price"],
                    entry_time=trade["Entry Time"],
                    exit_time=trade["Exit Time"],
                    quantity=10,
                    position_type="LONG",
                    profit=(trade["Exit Price"] - trade["Entry Price"]) * 10,
                )
            elif trade["Type"] == "SHORT":
                ClosedTrade.objects.create(
                    scrip=trade["scrip"],
                    entry_price=trade["Entry Price"],
                    exit_price=trade["Exit Price"],
                    entry_time=trade["Entry Time"],
                    exit_time=trade["Exit Time"],
                    quantity=10,
                    position_type="SHORT",
                    profit=(trade["Entry Price"] - trade["Exit Price"]) * 10,
                )
            self.stdout.write(self.style.SUCCESS(f"Trade for {symbol} saved."))

        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f"Integrity Error saving trade for {symbol}: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"General Error saving trade for {symbol}: {e}"))

