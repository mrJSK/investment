# # screener/backtest_engine.py

# import traceback
# import backtrader as bt
# import numpy as np
# import pandas as pd
# from .indicator_utils import load_ohlcv


# class ScreenerStrategy(bt.Strategy):
#     """
#     A generic backtrader strategy that uses the screener's AST filter
#     to generate buy signals. It implements a fixed percentage for
#     stop-loss and take-profit.
#     """
#     params = (
#         ('ast_filter', None),
#         ('stop_loss_pct', 2.0),
#         ('take_profit_pct', 5.0),
#         ('eval_ast_node_func', None),
#     )

#     def __init__(self):
#         if not self.p.ast_filter:
#             raise ValueError("An AST filter must be provided to the strategy.")
#         if not self.p.eval_ast_node_func:
#             raise ValueError("eval_ast_node_func must be provided to the strategy.")
        
#         self.buy_price = None
#         self.buy_comm = None
#         self.log_details = {}
#         self.closed_trades = [] # MODIFICATION: Add a list to store closed trades

#     # ... (the _eval_ast_node_with_logging function remains unchanged) ...
#     def _eval_ast_node_with_logging(self, symbol, ast_node, context, depth=0):
#         """
#         A wrapper around eval_ast_node_func to capture and log intermediate values
#         and decisions within the AST evaluation process.
#         """
#         current_date = context.get('current_date', None)
#         indent = "  " * depth
#         node_type = ast_node.get("type", "").upper()
#         # log_key_prefix = f"{symbol}_{current_date.isoformat() if current_date else 'NoDate'}_depth{depth}_"

#         try:
#             # Recursively evaluate children first to get their string representation and values
#             if node_type == "COMPARISON" or node_type == "BINARYEXPRESSION":
#                 left_val = self._eval_ast_node_with_logging(symbol, ast_node["left"], context, depth + 1)
#                 right_val = self._eval_ast_node_with_logging(symbol, ast_node["right"], context, depth + 1)
                
#                 # After children are evaluated, perform current node's evaluation
#                 op = ast_node["operator"].upper()
#                 result = self.p.eval_ast_node_func(symbol, ast_node, context) # Call actual evaluator
                
#                 left_str = str(ast_node["left"].get("name", str(left_val))) if ast_node["left"].get("type") == "IndicatorCall" else str(left_val)
#                 right_str = str(ast_node["right"].get("name", str(right_val))) if ast_node["right"].get("type") == "IndicatorCall" else str(right_val)
                
#                 # --- CRITICAL FIX: Extract scalar values for logging comparison ---
#                 left_val_for_log = left_val.iloc[-1] if isinstance(left_val, pd.Series) and not left_val.empty else left_val
#                 right_val_for_log = right_val.iloc[-1] if isinstance(right_val, pd.Series) and not right_val.empty else right_val

#                 # Ensure numerical values are formatted correctly, handle non-numbers gracefully
#                 left_formatted = f"{left_val_for_log:.2f}" if isinstance(left_val_for_log, (float, int, np.number)) and pd.notna(left_val_for_log) else str(left_val_for_log)
#                 right_formatted = f"{right_val_for_log:.2f}" if isinstance(right_val_for_log, (float, int, np.number)) and pd.notna(right_val_for_log) else str(right_val_for_log)
#                 # --- END CRITICAL FIX ---


#                 if node_type == "COMPARISON":
#                     self.log(f"{indent}COMPARE: ({left_str} {op} {right_str}) => {left_formatted} {op} {right_formatted} = {bool(result)}")
#                 elif node_type == "BINARYEXPRESSION":
#                     self.log(f"{indent}LOGIC: ({left_str} {op} {right_str}) => {left_val_for_log} {op} {right_val_for_log} = {bool(result)}")
#                 return result

#             elif node_type == "INDICATORCALL":
#                 result = self.p.eval_ast_node_func(symbol, ast_node, context) # Call actual evaluator
#                 ind_name = ast_node.get('name', 'UNKNOWN')
#                 tf = ast_node.get('timeframe', 'daily')
#                 part = f".{ast_node['part']}" if ast_node.get('part') else ""
                
#                 # Log final numerical value for indicator calls if they are numbers
#                 if isinstance(result, (float, int, np.number)) and pd.notna(result):
#                     self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = {result:.2f}")
#                 elif isinstance(result, pd.Series) and not result.empty: # It's a series, log its last value
#                     self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = Series (Last value: {result.iloc[-1]:.2f})")
#                 elif isinstance(result, bool): # For candlestick patterns wrapped as indicator calls
#                     self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = {result}")
#                 else: # For empty series or other non-numeric results
#                     self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = {type(result).__name__} (Empty/Invalid)")
#                 return result

#             elif node_type == "NUMBERLITERAL" or node_type == "FIELDLITERAL":
#                 result = self.p.eval_ast_node_func(symbol, ast_node, context) # Call actual evaluator
#                 # If it's a field literal, it will be a string like 'close'
#                 # If it's a number literal, it will be a float/int
#                 if isinstance(result, (float, int, np.number)) and pd.notna(result):
#                     self.log(f"{indent}LITERAL: {ast_node.get('value', ast_node.get('name', 'UNKNOWN'))} = {result:.2f}")
#                 else:
#                     self.log(f"{indent}LITERAL: {ast_node.get('value', ast_node.get('name', 'UNKNOWN'))} = {result}")
#                 return result

#             elif node_type == "NOT":
#                 expr_result = self._eval_ast_node_with_logging(symbol, ast_node["expr"], context, depth + 1)
#                 result = self.p.eval_ast_node_func(symbol, ast_node, context) # Call actual evaluator
#                 self.log(f"{indent}NOT: (NOT {expr_result}) = {bool(result)}")
#                 return result
            
#             else:
#                 result = self.p.eval_ast_node_func(symbol, ast_node, context) # Call actual evaluator
#                 self.log(f"{indent}NODE: {node_type} = {result}")
#                 return result

#         except Exception as e:
#             self.log(f"{indent}ERROR evaluating node type {node_type}: {e}")
#             return False # Or np.nan depending on what `eval_ast_node_func` returns on error

#     def next(self):
#         # ... (unchanged position management) ...
#         if self.position:
#             sl_price = self.buy_price * (1 - self.p.stop_loss_pct / 100.0)
#             tp_price = self.buy_price * (1 + self.p.take_profit_pct / 100.0)

#             if self.data.close[0] <= sl_price:
#                 self.log(f'CLOSE_POSITION: {self.data._name} STOP LOSS HIT. Current: {self.data.close[0]:.2f}, SL: {sl_price:.2f}')
#                 self.close()
#             elif self.data.close[0] >= tp_price:
#                 self.log(f'CLOSE_POSITION: {self.data._name} TAKE PROFIT HIT. Current: {self.data.close[0]:.2f}, TP: {tp_price:.2f}')
#                 self.close()
#             return

#         try:
#             symbol = self.data._name
#             current_date = self.data.datetime.date(0)
#             backtest_context = {'current_date': current_date}

#             self.log(f"\n--- Evaluating {symbol} on {current_date.isoformat()} ---")
#             condition_met = self._eval_ast_node_with_logging(symbol, self.p.ast_filter, backtest_context)
#             self.log(f"FINAL CONDITION FOR {symbol} on {current_date.isoformat()}: {condition_met}")
            
#             if condition_met:
#                 self.log(f'BUY CREATE: {self.data._name}, Price: {self.data.close[0]:.2f}')
#                 self.buy_price = self.data.close[0]
#                 self.buy()

#         except Exception as e:
#             self.log(f'CRITICAL ERROR during next() for {self.data._name} on {self.data.datetime.date(0).isoformat()}: {e}')
#             # traceback.print_exc() # Uncomment for more detailed tracebacks during debugging
#             pass

#     def log(self, txt, dt=None):
#         dt = dt or self.datas[0].datetime.date(0)
#         print('%s, %s' % (dt.isoformat(), txt))

#     def notify_order(self, order):
#         if order.status in [order.Submitted, order.Accepted]:
#             return
#         if order.status in [order.Completed]:
#             if order.isbuy():
#                 self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
#                 self.buy_price = order.executed.price
#                 self.buy_comm = order.executed.comm
#             elif order.issell():
#                 self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
#             self.bar_executed = len(self)
#         elif order.status in [order.Canceled, order.Margin, order.Rejected]:
#             self.log(f'Order Canceled/Margin/Rejected: {order.getstatusname()}')
#         self.order = None

#     # NEW FUNCTION: Add notify_trade to capture closed trades
#     def notify_trade(self, trade):
#         """
#         This method is called by backtrader when a trade is opened, updated, or closed.
#         We'll use it to collect closed trades.
#         """
#         if trade.isclosed:
#             self.log(f'TRADE CLOSED: {trade.data._name}, PNL: {trade.pnlcomm:.2f}')
#             self.closed_trades.append(trade)


# def run_backtest(ast_filter, symbols_to_scan, start_date, end_date, initial_capital, stop_loss_pct, take_profit_pct, position_size_pct):
#     cerebro = bt.Cerebro()
#     from .views import eval_ast_node as imported_eval_ast_node
#     cerebro.addstrategy(
#         ScreenerStrategy,
#         ast_filter=ast_filter,
#         stop_loss_pct=stop_loss_pct,
#         take_profit_pct=take_profit_pct,
#         eval_ast_node_func=imported_eval_ast_node,
#     )
    
#     # ... (data loading logic remains unchanged) ...
#     for symbol in symbols_to_scan:
#         df = load_ohlcv(symbol, 'daily')
#         if df is None or df.empty:
#             continue
#         df = df.loc[start_date:end_date]
#         if df.empty:
#             continue
#         df = df.sort_index()
#         data_feed = bt.feeds.PandasData(dataname=df, name=symbol)
#         cerebro.adddata(data_feed)
    
#     # ... (cerebro configuration remains unchanged) ...
#     cerebro.broker.set_cash(initial_capital)
#     cerebro.broker.setcommission(commission=0.001)
#     cerebro.addsizer(bt.sizers.PercentSizer, percents=position_size_pct)
    
#     cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
#     cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days)
#     cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
#     cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

#     if not cerebro.datas:
#         return {'summary': {}, 'trades': [], 'equity_curve': [], 'error': 'No valid data feeds added for backtesting.'}

#     results = cerebro.run()
#     if not results:
#         return {'summary': {}, 'trades': [], 'equity_curve': [], 'message': 'Backtest ran, but no strategy results were generated.'}
    
#     strat = results[0]
    
#     # ... (analyzer retrieval remains unchanged) ...
#     trade_analyzer = strat.analyzers.getbyname('trades').get_analysis()
#     pyfolio_analyzer = strat.analyzers.getbyname('pyfolio').get_pf_items()
#     drawdown_analyzer = strat.analyzers.getbyname('drawdown').get_analysis()
#     sharpe_analyzer = strat.analyzers.getbyname('sharpe').get_analysis()
    
#     # ... (summary stats preparation remains unchanged) ...
#     final_value = cerebro.broker.getvalue()
#     summary = {
#         'total_return_pct': (final_value / initial_capital - 1) * 100 if initial_capital != 0 else 0,
#         'total_trades': trade_analyzer.total.closed if 'total' in trade_analyzer and 'closed' in trade_analyzer.total else 0,
#         'win_rate': (trade_analyzer.won.total / trade_analyzer.total.closed * 100) if 'won' in trade_analyzer and trade_analyzer.total.closed > 0 else 0,
#         'profit_factor': (trade_analyzer.won.pnl.total / abs(trade_analyzer.lost.pnl.total)) if 'won' in trade_analyzer and 'lost' in trade_analyzer and trade_analyzer.lost.pnl.total != 0 else 0,
#         'max_drawdown_pct': drawdown_analyzer.max.drawdown if 'max' in drawdown_analyzer else 0,
#         'sharpe_ratio': sharpe_analyzer['sharperatio'] if 'sharperatio' in sharpe_analyzer else np.nan
#     }

#     # --- MODIFICATION START: Correct way to extract trades ---
#     trades = []
#     # Iterate over the list of closed trades we collected in the strategy
#     if hasattr(strat, 'closed_trades') and strat.closed_trades:
#         for trade in strat.closed_trades:
#             try:
#                 # The entry value of the trade (price * size)
#                 trade_value = trade.value
#                 pnl_pct = 0.0
#                 # Calculate PnL percentage against the initial trade value
#                 if trade_value != 0:
#                     pnl_pct = (trade.pnlcomm / trade_value) * 100

#                 trades.append({
#                     'symbol': trade.data._name,
#                     'entry_date': bt.num2date(trade.dtopen).date().isoformat(),
#                     'exit_date': bt.num2date(trade.dtclose).date().isoformat(),
#                     'pnl_pct': pnl_pct,
#                     'reason': 'Strategy Exit' # Note: Getting the specific reason (SL/TP) is more complex
#                 })
#             except Exception as e:
#                 print(f"Error processing a closed trade: {e}")
#                 continue
#     # --- MODIFICATION END ---
    
#     # Fallback message if no trades were executed
#     if not trades and trade_analyzer.total.closed > 0:
#         trades.append({
#             'symbol': 'Multiple',
#             'entry_date': 'N/A',
#             'exit_date': 'N/A',
#             'pnl_pct': summary['total_return_pct'],
#             'reason': f"{trade_analyzer.total.closed} trades executed (details not available)"
#         })
#     elif not trades:
#         trades.append({
#             'symbol': 'N/A',
#             'entry_date': 'N/A',
#             'exit_date': 'N/A',
#             'pnl_pct': 0.0,
#             'reason': 'No trades executed'
#         })

#     # ... (equity curve logic remains unchanged) ...
#     equity_curve = []
#     returns, positions, transactions, gross_lev = pyfolio_analyzer
#     if isinstance(returns, pd.Series) and not returns.empty:
#         cumulative = (returns + 1).cumprod() * initial_capital
#         for date, value in cumulative.items():
#             equity_curve.append({
#                 'datetime': date.strftime('%Y-%m-%d'), 
#                 'equity': float(value)
#             })

#     return {
#         'summary': summary,
#         'trades': trades,
#         'equity_curve': equity_curve
#     }


# screener/backtest_engine.py

import traceback
import backtrader as bt
import numpy as np
import pandas as pd
from .indicator_utils import load_ohlcv


class ScreenerStrategy(bt.Strategy):
    """
    A generic backtrader strategy that uses the screener's AST filter
    to generate buy signals. It implements a fixed percentage for
    stop-loss and take-profit.
    """
    params = (
        ('ast_filter', None),
        ('stop_loss_pct', 2.0),
        ('take_profit_pct', 5.0),
        ('eval_ast_node_func', None),
    )

    def __init__(self):
        if not self.p.ast_filter:
            raise ValueError("An AST filter must be provided to the strategy.")
        if not self.p.eval_ast_node_func:
            raise ValueError("eval_ast_node_func must be provided to the strategy.")
        
        self.buy_price = None
        self.buy_comm = None
        self.log_details = {}
        self.closed_trades = []
        self.exit_reason = None # NEW: To store the reason for closing a trade

    # ... (the _eval_ast_node_with_logging function remains unchanged) ...
    def _eval_ast_node_with_logging(self, symbol, ast_node, context, depth=0):
        # This function is unchanged
        current_date = context.get('current_date', None)
        indent = "  " * depth
        node_type = ast_node.get("type", "").upper()
        try:
            if node_type == "COMPARISON" or node_type == "BINARYEXPRESSION":
                left_val = self._eval_ast_node_with_logging(symbol, ast_node["left"], context, depth + 1)
                right_val = self._eval_ast_node_with_logging(symbol, ast_node["right"], context, depth + 1)
                op = ast_node["operator"].upper()
                result = self.p.eval_ast_node_func(symbol, ast_node, context)
                left_str = str(ast_node["left"].get("name", str(left_val))) if ast_node["left"].get("type") == "IndicatorCall" else str(left_val)
                right_str = str(ast_node["right"].get("name", str(right_val))) if ast_node["right"].get("type") == "IndicatorCall" else str(right_val)
                left_val_for_log = left_val.iloc[-1] if isinstance(left_val, pd.Series) and not left_val.empty else left_val
                right_val_for_log = right_val.iloc[-1] if isinstance(right_val, pd.Series) and not right_val.empty else right_val
                left_formatted = f"{left_val_for_log:.2f}" if isinstance(left_val_for_log, (float, int, np.number)) and pd.notna(left_val_for_log) else str(left_val_for_log)
                right_formatted = f"{right_val_for_log:.2f}" if isinstance(right_val_for_log, (float, int, np.number)) and pd.notna(right_val_for_log) else str(right_val_for_log)
                if node_type == "COMPARISON":
                    self.log(f"{indent}COMPARE: ({left_str} {op} {right_str}) => {left_formatted} {op} {right_formatted} = {bool(result)}")
                elif node_type == "BINARYEXPRESSION":
                    self.log(f"{indent}LOGIC: ({left_str} {op} {right_str}) => {left_val_for_log} {op} {right_val_for_log} = {bool(result)}")
                return result
            elif node_type == "INDICATORCALL":
                result = self.p.eval_ast_node_func(symbol, ast_node, context)
                ind_name = ast_node.get('name', 'UNKNOWN')
                tf = ast_node.get('timeframe', 'daily')
                part = f".{ast_node['part']}" if ast_node.get('part') else ""
                if isinstance(result, (float, int, np.number)) and pd.notna(result):
                    self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = {result:.2f}")
                elif isinstance(result, pd.Series) and not result.empty:
                    self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = Series (Last value: {result.iloc[-1]:.2f})")
                elif isinstance(result, bool):
                    self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = {result}")
                else:
                    self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = {type(result).__name__} (Empty/Invalid)")
                return result
            elif node_type == "NUMBERLITERAL" or node_type == "FIELDLITERAL":
                result = self.p.eval_ast_node_func(symbol, ast_node, context)
                if isinstance(result, (float, int, np.number)) and pd.notna(result):
                    self.log(f"{indent}LITERAL: {ast_node.get('value', ast_node.get('name', 'UNKNOWN'))} = {result:.2f}")
                else:
                    self.log(f"{indent}LITERAL: {ast_node.get('value', ast_node.get('name', 'UNKNOWN'))} = {result}")
                return result
            elif node_type == "NOT":
                expr_result = self._eval_ast_node_with_logging(symbol, ast_node["expr"], context, depth + 1)
                result = self.p.eval_ast_node_func(symbol, ast_node, context)
                self.log(f"{indent}NOT: (NOT {expr_result}) = {bool(result)}")
                return result
            else:
                result = self.p.eval_ast_node_func(symbol, ast_node, context)
                self.log(f"{indent}NODE: {node_type} = {result}")
                return result
        except Exception as e:
            self.log(f"{indent}ERROR evaluating node type {node_type}: {e}")
            return False

    def next(self):
        # MODIFIED: Set the exit reason before closing the position
        if self.position:
            sl_price = self.buy_price * (1 - self.p.stop_loss_pct / 100.0)
            tp_price = self.buy_price * (1 + self.p.take_profit_pct / 100.0)

            if self.data.close[0] <= sl_price:
                self.log(f'CLOSE_POSITION: {self.data._name} STOP LOSS HIT. Current: {self.data.close[0]:.2f}, SL: {sl_price:.2f}')
                self.exit_reason = 'Stop Loss' # SET REASON
                self.close()
            elif self.data.close[0] >= tp_price:
                self.log(f'CLOSE_POSITION: {self.data._name} TAKE PROFIT HIT. Current: {self.data.close[0]:.2f}, TP: {tp_price:.2f}')
                self.exit_reason = 'Take Profit' # SET REASON
                self.close()
            return

        try:
            symbol = self.data._name
            current_date = self.data.datetime.date(0)
            backtest_context = {'current_date': current_date}

            self.log(f"\n--- Evaluating {symbol} on {current_date.isoformat()} ---")
            condition_met = self._eval_ast_node_with_logging(symbol, self.p.ast_filter, backtest_context)
            self.log(f"FINAL CONDITION FOR {symbol} on {current_date.isoformat()}: {condition_met}")
            
            if condition_met:
                self.log(f'BUY CREATE: {self.data._name}, Price: {self.data.close[0]:.2f}')
                self.buy_price = self.data.close[0]
                self.buy()

        except Exception as e:
            self.log(f'CRITICAL ERROR during next() for {self.data._name} on {self.data.datetime.date(0).isoformat()}: {e}')
            pass

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order Canceled/Margin/Rejected: {order.getstatusname()}')
        self.order = None

    # --- MODIFICATION START: A more robust and correct strategy implementation ---
class ScreenerStrategy(bt.Strategy):
    """
    A generic backtrader strategy that uses the screener's AST filter
    to generate buy signals. It implements a fixed percentage for
    stop-loss and take-profit.
    """
    params = (
        ('ast_filter', None),
        ('stop_loss_pct', 2.0),
        ('take_profit_pct', 5.0),
        ('eval_ast_node_func', None),
    )

    def __init__(self):
        if not self.p.ast_filter:
            raise ValueError("An AST filter must be provided to the strategy.")
        if not self.p.eval_ast_node_func:
            raise ValueError("eval_ast_node_func must be provided to the strategy.")
        
        # We no longer need to manually track buy_price or buy_comm here.
        self.exit_reason = None
        self.closed_trades = []

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        # If a position is already open, check for exit conditions
        if self.position:
            # For robustness, get the entry price directly from the position object
            entry_price = self.position.price

            sl_price = entry_price * (1 - self.p.stop_loss_pct / 100.0)
            tp_price = entry_price * (1 + self.p.take_profit_pct / 100.0)

            current_close = self.data.close[0]

            if current_close <= sl_price:
                self.log(f'CLOSE_POSITION (SL): {self.data._name}, Entry: {entry_price:.2f}, Exit: {current_close:.2f}')
                self.exit_reason = 'Stop Loss'
                self.close() # Close position
            elif current_close >= tp_price:
                self.log(f'CLOSE_POSITION (TP): {self.data._name}, Entry: {entry_price:.2f}, Exit: {current_close:.2f}')
                self.exit_reason = 'Take Profit'
                self.close() # Close position
            return # Do nothing else if we are in a position

        # If no position is open, check for entry conditions
        try:
            symbol = self.data._name
            current_date = self.data.datetime.date(0)
            backtest_context = {'current_date': current_date}

            # Note: The _eval_ast_node_with_logging function is removed from the strategy
            # as it was for debugging and the core eval logic is passed in via params.
            # We call the function passed from the backtest runner directly.
            condition_met = self.p.eval_ast_node_func(symbol, self.p.ast_filter, backtest_context)
            
            if condition_met:
                self.log(f'BUY CREATE: {self.data._name}, Price: {self.data.close[0]:.2f}')
                self.buy() # Let backtrader handle the trade execution

        except Exception as e:
            self.log(f'CRITICAL ERROR in next() for {self.data._name} on {self.data.datetime.date(0).isoformat()}: {e}')
            traceback.print_exc()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return # A buy/sell order has been submitted/accepted - Nothing to do

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED: {order.data._name}, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED: {order.data._name}, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order Canceled/Margin/Rejected: {order.getstatusname()} for {order.data._name}')

    def notify_trade(self, trade):
        if trade.isclosed:
            # Attach the exit reason we stored in next() to the trade object
            trade.reason = self.exit_reason or 'Exit Signal'
            self.closed_trades.append(trade)
            # Reset the reason for the next trade
            self.exit_reason = None
            self.log(f'TRADE CLOSED: {trade.data._name}, PNL: {trade.pnlcomm:.2f}, Reason: {trade.reason}')
        # --- MODIFICATION END ---


# screener/backtest_engine.py

import traceback
import backtrader as bt
import numpy as np
import pandas as pd
from .indicator_utils import load_ohlcv

# --- This is the core strategy logic ---
class ScreenerStrategy(bt.Strategy):
    """
    A robust backtrader strategy that uses the screener's AST filter
    to generate buy signals. It exits based on a fixed percentage for
    stop-loss and take-profit.
    """
    params = (
        ('ast_filter', None),
        ('stop_loss_pct', 2.0),
        ('take_profit_pct', 5.0),
        ('eval_ast_node_func', None),
    )

    def __init__(self):
        if not self.p.ast_filter:
            raise ValueError("An AST filter must be provided to the strategy.")
        if not self.p.eval_ast_node_func:
            raise ValueError("eval_ast_node_func must be provided to the strategy.")
        
        # Stores the reason for a trade exit (e.g., 'Stop Loss')
        self.exit_reason = None
        # A list to hold all completed trade objects for later analysis
        self.closed_trades = []

    def log(self, txt, dt=None):
        """ Logging function for this strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        """Main strategy logic, executed on each bar."""
        # If a position is already open, check only for exit conditions
        if self.position:
            entry_price = self.position.price
            current_close = self.data.close[0]

            sl_price = entry_price * (1 - self.p.stop_loss_pct / 100.0)
            tp_price = entry_price * (1 + self.p.take_profit_pct / 100.0)

            if current_close <= sl_price:
                self.log(f'CLOSE_POSITION (SL): {self.data._name}, Entry: {entry_price:.2f}, Exit: {current_close:.2f}')
                self.exit_reason = 'Stop Loss'
                self.close()
            elif current_close >= tp_price:
                self.log(f'CLOSE_POSITION (TP): {self.data._name}, Entry: {entry_price:.2f}, Exit: {current_close:.2f}')
                self.exit_reason = 'Take Profit'
                self.close()
            return

        # If no position is open, check for a new entry signal
        try:
            symbol = self.data._name
            current_date = self.data.datetime.date(0)
            backtest_context = {'current_date': current_date}

            # Use the evaluation function passed from the view to check screener conditions
            condition_met = self.p.eval_ast_node_func(symbol, self.p.ast_filter, backtest_context)
            
            if condition_met:
                self.log(f'BUY CREATE: {self.data._name}, Price: {self.data.close[0]:.2f}')
                self.buy()

        except Exception as e:
            self.log(f'CRITICAL ERROR in next() for {self.data._name} on {current_date.isoformat()}: {e}')
            traceback.print_exc()

    def notify_order(self, order):
        """Handles order status notifications."""
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED: {order.data._name}, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED: {order.data._name}, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order Canceled/Margin/Rejected: {order.getstatusname()} for {order.data._name}')

    def notify_trade(self, trade):
        """Collects closed trades and attaches the exit reason."""
        if trade.isclosed:
            trade.reason = self.exit_reason or 'Exit Signal'
            self.closed_trades.append(trade)
            self.exit_reason = None # Reset for the next trade
            self.log(f'TRADE CLOSED: {trade.data._name}, PNL: {trade.pnlcomm:.2f}, Reason: {trade.reason}')


# --- This function runs the entire backtest and returns the results ---
def run_backtest(ast_filter, symbols_to_scan, start_date, end_date, initial_capital, stop_loss_pct, take_profit_pct, position_size_pct):
    """
    Executes a backtest for a given AST filter, a list of symbols, and trading parameters.
    Returns a dictionary containing summary statistics, a list of all executed trades,
    and data for the equity curve.
    """
    cerebro = bt.Cerebro()
    from .views import eval_ast_node as imported_eval_ast_node

    cerebro.addstrategy(
        ScreenerStrategy,
        ast_filter=ast_filter,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct,
        eval_ast_node_func=imported_eval_ast_node,
    )

    for symbol in symbols_to_scan:
        df = load_ohlcv(symbol, 'daily')
        if df is None or df.empty:
            continue
        df = df.loc[start_date:end_date]
        if df.empty:
            continue
        data_feed = bt.feeds.PandasData(dataname=df.sort_index(), name=symbol)
        cerebro.adddata(data_feed)

    if not cerebro.datas:
        return {'summary': {}, 'trades': [], 'equity_curve': [], 'error': 'No valid data found for the symbols in the selected date range.'}

    cerebro.broker.set_cash(initial_capital)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=position_size_pct)

    # Add analyzers to get performance metrics
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')

    results = cerebro.run()
    if not results:
        return {'summary': {}, 'trades': [], 'equity_curve': [], 'message': 'Backtest ran, but no strategy results were generated.'}

    strat = results[0]

    # Extract results from analyzers
    trade_analyzer = strat.analyzers.getbyname('trades').get_analysis()
    pyfolio_analyzer = strat.analyzers.getbyname('pyfolio').get_pf_items()
    drawdown_analyzer = strat.analyzers.getbyname('drawdown').get_analysis()
    sharpe_analyzer = strat.analyzers.getbyname('sharpe').get_analysis()

    # Prepare summary statistics
    final_value = cerebro.broker.getvalue()
    total_stats = trade_analyzer.get('total', {})
    won_stats = trade_analyzer.get('won', {})
    lost_stats = trade_analyzer.get('lost', {})
    pnl_won_total = won_stats.get('pnl', {}).get('total', 0)
    pnl_lost_total = lost_stats.get('pnl', {}).get('total', 0)
    profit_factor = pnl_won_total / abs(pnl_lost_total) if pnl_lost_total != 0 else 0

    summary = {
        'total_return_pct': (final_value / initial_capital - 1) * 100 if initial_capital > 0 else 0,
        'sharpe_ratio': sharpe_analyzer.get('sharperatio'),
        'max_drawdown_pct': drawdown_analyzer.get('max', {}).get('drawdown', 0),
        'total_trades': total_stats.get('closed', 0),
        'win_rate': (won_stats.get('total', 0) / total_stats.get('closed', 1)) * 100 if total_stats.get('closed', 0) > 0 else 0,
        'profit_factor': profit_factor,
    }

    # Build the trade list using the reliable `closed_trades` list from the strategy
    trades = []
    if hasattr(strat, 'closed_trades') and strat.closed_trades:
        for trade in strat.closed_trades:
            pnl_pct = (trade.pnlcomm / trade.value) * 100 if trade.value != 0 else 0
            trades.append({
                'symbol': trade.data._name,
                'entry_date': bt.num2date(trade.dtopen).date().isoformat(),
                'exit_date': bt.num2date(trade.dtclose).date().isoformat(),
                'pnl_pct': pnl_pct,
                'reason': getattr(trade, 'reason', 'Strategy Exit')
            })
    else:
        trades.append({'symbol': 'N/A', 'entry_date': 'N/A', 'exit_date': 'N/A', 'pnl_pct': 0.0, 'reason': 'No trades executed'})

    # Prepare the equity curve data
    equity_curve = []
    returns, _, _, _ = pyfolio_analyzer
    if isinstance(returns, pd.Series) and not returns.empty:
        equity_values = (1 + returns).cumprod() * initial_capital
        for date, value in equity_values.items():
            equity_curve.append({'datetime': date.strftime('%Y-%m-%d'), 'equity': float(value)})

    # Return the final results object, ready to be converted to JSON
    return {
        'summary': summary,
        'trades': trades,
        'equity_curve': equity_curve
    }