# screener/backtest_engine.py

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

    def _eval_ast_node_with_logging(self, symbol, ast_node, context, depth=0):
        """
        A wrapper around eval_ast_node_func to capture and log intermediate values
        and decisions within the AST evaluation process.
        """
        current_date = context.get('current_date', None)
        indent = "  " * depth
        node_type = ast_node.get("type", "").upper()
        # log_key_prefix = f"{symbol}_{current_date.isoformat() if current_date else 'NoDate'}_depth{depth}_"

        try:
            # Recursively evaluate children first to get their string representation and values
            if node_type == "COMPARISON" or node_type == "BINARYEXPRESSION":
                left_val = self._eval_ast_node_with_logging(symbol, ast_node["left"], context, depth + 1)
                right_val = self._eval_ast_node_with_logging(symbol, ast_node["right"], context, depth + 1)
                
                # After children are evaluated, perform current node's evaluation
                op = ast_node["operator"].upper()
                result = self.p.eval_ast_node_func(symbol, ast_node, context) # Call actual evaluator
                
                left_str = str(ast_node["left"].get("name", str(left_val))) if ast_node["left"].get("type") == "IndicatorCall" else str(left_val)
                right_str = str(ast_node["right"].get("name", str(right_val))) if ast_node["right"].get("type") == "IndicatorCall" else str(right_val)
                
                # --- CRITICAL FIX: Extract scalar values for logging comparison ---
                left_val_for_log = left_val.iloc[-1] if isinstance(left_val, pd.Series) and not left_val.empty else left_val
                right_val_for_log = right_val.iloc[-1] if isinstance(right_val, pd.Series) and not right_val.empty else right_val

                # Ensure numerical values are formatted correctly, handle non-numbers gracefully
                left_formatted = f"{left_val_for_log:.2f}" if isinstance(left_val_for_log, (float, int, np.number)) and pd.notna(left_val_for_log) else str(left_val_for_log)
                right_formatted = f"{right_val_for_log:.2f}" if isinstance(right_val_for_log, (float, int, np.number)) and pd.notna(right_val_for_log) else str(right_val_for_log)
                # --- END CRITICAL FIX ---


                if node_type == "COMPARISON":
                    self.log(f"{indent}COMPARE: ({left_str} {op} {right_str}) => {left_formatted} {op} {right_formatted} = {bool(result)}")
                elif node_type == "BINARYEXPRESSION":
                    self.log(f"{indent}LOGIC: ({left_str} {op} {right_str}) => {left_val_for_log} {op} {right_val_for_log} = {bool(result)}")
                return result

            elif node_type == "INDICATORCALL":
                result = self.p.eval_ast_node_func(symbol, ast_node, context) # Call actual evaluator
                ind_name = ast_node.get('name', 'UNKNOWN')
                tf = ast_node.get('timeframe', 'daily')
                part = f".{ast_node['part']}" if ast_node.get('part') else ""
                
                # Log final numerical value for indicator calls if they are numbers
                if isinstance(result, (float, int, np.number)) and pd.notna(result):
                    self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = {result:.2f}")
                elif isinstance(result, pd.Series) and not result.empty: # It's a series, log its last value
                    self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = Series (Last value: {result.iloc[-1]:.2f})")
                elif isinstance(result, bool): # For candlestick patterns wrapped as indicator calls
                    self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = {result}")
                else: # For empty series or other non-numeric results
                    self.log(f"{indent}IND_CALL: {tf.upper()} {ind_name}{part} = {type(result).__name__} (Empty/Invalid)")
                return result

            elif node_type == "NUMBERLITERAL" or node_type == "FIELDLITERAL":
                result = self.p.eval_ast_node_func(symbol, ast_node, context) # Call actual evaluator
                # If it's a field literal, it will be a string like 'close'
                # If it's a number literal, it will be a float/int
                if isinstance(result, (float, int, np.number)) and pd.notna(result):
                    self.log(f"{indent}LITERAL: {ast_node.get('value', ast_node.get('name', 'UNKNOWN'))} = {result:.2f}")
                else:
                    self.log(f"{indent}LITERAL: {ast_node.get('value', ast_node.get('name', 'UNKNOWN'))} = {result}")
                return result

            elif node_type == "NOT":
                expr_result = self._eval_ast_node_with_logging(symbol, ast_node["expr"], context, depth + 1)
                result = self.p.eval_ast_node_func(symbol, ast_node, context) # Call actual evaluator
                self.log(f"{indent}NOT: (NOT {expr_result}) = {bool(result)}")
                return result
            
            else:
                result = self.p.eval_ast_node_func(symbol, ast_node, context) # Call actual evaluator
                self.log(f"{indent}NODE: {node_type} = {result}")
                return result

        except Exception as e:
            self.log(f"{indent}ERROR evaluating node type {node_type}: {e}")
            return False # Or np.nan depending on what `eval_ast_node_func` returns on error

    def next(self):
        # ... (unchanged position management) ...
        if self.position:
            sl_price = self.buy_price * (1 - self.p.stop_loss_pct / 100.0)
            tp_price = self.buy_price * (1 + self.p.take_profit_pct / 100.0)

            if self.data.close[0] <= sl_price:
                self.log(f'CLOSE_POSITION: {self.data._name} STOP LOSS HIT. Current: {self.data.close[0]:.2f}, SL: {sl_price:.2f}')
                self.close()
            elif self.data.close[0] >= tp_price:
                self.log(f'CLOSE_POSITION: {self.data._name} TAKE PROFIT HIT. Current: {self.data.close[0]:.2f}, TP: {tp_price:.2f}')
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
            # traceback.print_exc() # Uncomment for more detailed tracebacks during debugging
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

# ... (rest of the run_backtest function, no changes needed below ScreenerStrategy)
def run_backtest(ast_filter, symbols_to_scan, start_date, end_date, initial_capital, stop_loss_pct, take_profit_pct, position_size_pct):
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
        df = df.sort_index()
        data_feed = bt.feeds.PandasData(dataname=df, name=symbol)
        cerebro.adddata(data_feed)
    cerebro.broker.set_cash(initial_capital)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=position_size_pct)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    if not cerebro.datas:
        return {'summary': {}, 'trades': [], 'equity_curve': [], 'error': 'No valid data feeds added for backtesting.'}
    results = cerebro.run()
    if not results:
        return {'summary': {}, 'trades': [], 'equity_curve': [], 'message': 'Backtest ran, but no strategy results were generated (e.g., no trades).'}
    strat = results[0]
    pyfolio_analyzer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfolio_analyzer.get_pf_items()
    trade_analyzer = strat.analyzers.getbyname('trades').get_analysis()
    drawdown_analyzer = strat.analyzers.getbyname('drawdown').get_analysis()
    sharpe_analyzer = strat.analyzers.getbyname('sharpe').get_analysis()
    final_value = cerebro.broker.getvalue()
    summary = {
        'total_return_pct': (final_value / initial_capital - 1) * 100 if initial_capital != 0 else 0,
        'total_trades': trade_analyzer.total.closed if 'total' in trade_analyzer and 'closed' in trade_analyzer.total else 0,
        'win_rate': (trade_analyzer.won.total / trade_analyzer.total.closed * 100) if 'won' in trade_analyzer and 'total' in trade_analyzer.won and trade_analyzer.total.closed > 0 else 0,
        'profit_factor': (trade_analyzer.won.pnl.total / abs(trade_analyzer.lost.pnl.total)) if 'won' in trade_analyzer and 'pnl' in trade_analyzer.won and 'lost' in trade_analyzer and 'pnl' in trade_analyzer.lost and trade_analyzer.lost.pnl.total !=0 else 0,
        'max_drawdown_pct': drawdown_analyzer.max.drawdown if 'max' in drawdown_analyzer and 'drawdown' in drawdown_analyzer.max else 0,
        'sharpe_ratio': sharpe_analyzer['sharperatio'] if 'sharperatio' in sharpe_analyzer else np.nan
    }
    trades = []
    if 'total' in trade_analyzer and 'closed' in trade_analyzer.total and trade_analyzer.total.closed > 0 and 'trades' in trade_analyzer:
        for trade_id, trade_info in trade_analyzer.trades.items():
            entry_dt = trade_info.ref.datetime.date().isoformat() if hasattr(trade_info.ref, 'datetime') else 'N/A'
            exit_dt = trade_info.date.date().isoformat() if hasattr(trade_info, 'date') else 'N/A'
            pnl_pct = 0
            if trade_info.pnlcomm.total > 0 and trade_info.value > 0:
                 pnl_pct = (trade_info.pnlcomm.total / trade_info.value) * 100
            elif trade_info.pnlcomm.total < 0 and trade_info.value > 0:
                 pnl_pct = (trade_info.pnlcomm.total / trade_info.value) * 100
            trades.append({
                'symbol': trade_info.data._name if hasattr(trade_info, 'data') else 'N/A',
                'entry_date': entry_dt,
                'exit_date': exit_dt,
                'pnl_pct': pnl_pct,
                'reason': 'Strategy Exit',
            })
    else:
        trades.append({
            'symbol': 'N/A',
            'entry_date': 'N/A',
            'exit_date': 'N/A',
            'pnl_pct': 0.0,
            'reason': 'No trades executed',
        })
    equity_curve = []
    if not returns.empty:
        equity = (1 + returns).cumprod() * initial_capital
        for date, value in equity.items():
            equity_curve.append({'datetime': date.strftime('%Y-%m-%d'), 'equity': value})
    return {'summary': summary, 'trades': trades, 'equity_curve': equity_curve}