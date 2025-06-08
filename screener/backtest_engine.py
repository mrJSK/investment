# screener/backtest_engine.py

import traceback
import backtrader as bt
import numpy as np
import pandas as pd
from .indicator_utils import load_ohlcv


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
        
        self.exit_reason = None
        self.closed_trades = []
        # NEW: To store entry details for currently open positions, like execution size
        self.open_positions_info = {}

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        # If a position is already open for the current data feed, check for exit conditions
        if self.getposition().size != 0:
            entry_price = self.getposition().price
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

            condition_met = self.p.eval_ast_node_func(symbol, self.p.ast_filter, backtest_context)
            
            if condition_met:
                self.log(f'BUY CREATE: {self.data._name}, Price: {self.data.close[0]:.2f}')
                self.buy()

        except Exception as e:
            self.log(f'CRITICAL ERROR in next() for {self.data._name} on {self.data.datetime.date(0).isoformat()}: {e}')
            traceback.print_exc()

    def notify_order(self, order):
        """NEW: Catches the execution of an order to store its size."""
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED: {order.data._name}, Size: {order.executed.size}, Price: {order.executed.price:.2f}')
                # Store the executed size for the symbol
                self.open_positions_info[order.data._name] = {'size': order.executed.size}
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order Canceled/Margin/Rejected for {order.data._name}: {order.getstatusname()}')

    def notify_trade(self, trade):
        """MODIFIED: Correctly uses stored info to fix trade size for PnL calculation."""
        if trade.isclosed:
            trade.reason = self.exit_reason or 'Exit Signal'
            symbol = trade.data._name

            # If trade.size from backtrader is 0, use our stored size from notify_order
            if trade.size == 0 and symbol in self.open_positions_info:
                trade.size = self.open_positions_info[symbol]['size']
                self.log(f'DEBUG: Corrected trade.size for {symbol} to {trade.size} based on stored info.')

            # Clean up the stored info for this now-closed trade
            if symbol in self.open_positions_info:
                del self.open_positions_info[symbol]

            self.closed_trades.append(trade)
            # Reset the reason for the next trade
            self.exit_reason = None
            self.log(f'TRADE CLOSED: {trade.data._name}, PNL: {trade.pnlcomm:.2f}, Reason: {trade.reason}')
# --- MODIFICATION END ---


def run_backtest(ast_filter, symbols_to_scan, start_date, end_date, initial_capital, stop_loss_pct, take_profit_pct, position_size_pct):
    """
    Executes a backtest for a given AST filter, a list of symbols, and trading parameters.

    Returns a dictionary containing summary statistics, a list of all executed trades,
    and data for the equity curve.
    """
    cerebro = bt.Cerebro()
    from .views import eval_ast_node as imported_eval_ast_node

    # Add the Strategy with its parameters
    cerebro.addstrategy(
        ScreenerStrategy,
        ast_filter=ast_filter,
        stop_loss_pct=float(stop_loss_pct),
        take_profit_pct=float(take_profit_pct),
        eval_ast_node_func=imported_eval_ast_node,
    )

    # Add data feeds for all symbols
    print(f"DEBUG: Backtest preparing data for range: {start_date} to {end_date}")
    for symbol in symbols_to_scan:
        df = load_ohlcv(symbol, 'daily')
        if df is None or df.empty:
            continue
        # Filter data for the backtest period
        df = df.loc[start_date:end_date]
        if df.empty:
            continue
        df = df.sort_index()
        data_feed = bt.feeds.PandasData(dataname=df, name=symbol)
        cerebro.adddata(data_feed)

    # Configure Cerebro (Broker, Sizer, Analyzers)
    if not cerebro.datas:
        return {'summary': {}, 'trades': [], 'equity_curve': [], 'error': 'No valid data found for the symbols in the selected date range.'}

    try:
        initial_capital = float(initial_capital)
    except ValueError:
        return {'summary': {}, 'trades': [], 'equity_curve': [], 'error': 'Initial capital must be a valid number.'}

    cerebro.broker.set_cash(initial_capital)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=float(position_size_pct))

    # Add all necessary analyzers
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

    final_value = cerebro.broker.getvalue()
    total_stats = trade_analyzer.get('total', {})
    won_stats = trade_analyzer.get('won', {})
    lost_stats = trade_analyzer.get('lost', {})
    streak_stats = trade_analyzer.get('streak', {}) # For optional request

    pnl_won_total = won_stats.get('pnl', {}).get('total', 0)
    pnl_lost_total = lost_stats.get('pnl', {}).get('total', 0)

    profit_factor = 0
    if abs(pnl_lost_total) > 0:
        profit_factor = pnl_won_total / abs(pnl_lost_total)

    summary = {
        'total_return_pct': (final_value / initial_capital - 1) * 100 if initial_capital > 0 else 0,
        'sharpe_ratio': sharpe_analyzer.get('sharperatio'),
        'max_drawdown_pct': drawdown_analyzer.get('max', {}).get('drawdown', 0),
        'total_trades': total_stats.get('closed', 0),
        'win_rate': (won_stats.get('total', 0) / total_stats.get('closed', 1)) * 100 if total_stats.get('closed', 0) > 0 else 0,
        'profit_factor': profit_factor,
        # --- NEW STATS FOR OPTIONAL REQUEST ---
        'avg_win_pnl': won_stats.get('pnl', {}).get('average', 0),
        'avg_loss_pnl': lost_stats.get('pnl', {}).get('average', 0),
        'longest_win_streak': streak_stats.get('won', {}).get('longest', 0),
        'longest_loss_streak': streak_stats.get('lost', {}).get('longest', 0),
    }

    # Build the trade list using the reliable `closed_trades` list
    trades = []
    if hasattr(strat, 'closed_trades') and strat.closed_trades:
        for trade in strat.closed_trades:
            try:
                # This calculation now uses the corrected trade.size
                initial_investment = abs(trade.price * trade.size)
                pnl_pct = (trade.pnlcomm / initial_investment) * 100 if initial_investment != 0 else 0

                trades.append({
                    'symbol': trade.data._name,
                    'entry_date': bt.num2date(trade.dtopen).date().isoformat(),
                    'exit_date': bt.num2date(trade.dtclose).date().isoformat(),
                    'pnl_pct': pnl_pct,
                    'reason': getattr(trade, 'reason', 'Strategy Exit')
                })
            except Exception as e:
                print(f"Error processing a closed trade object: {e}")
                traceback.print_exc()
                continue

    # Prepare the equity curve data for charting
    equity_curve = []
    returns, _, _, _ = pyfolio_analyzer
    if isinstance(returns, pd.Series) and not returns.empty:
        cumulative_returns = (1 + returns).cumprod()
        equity_values = cumulative_returns * initial_capital
        for date, value in equity_values.items():
            equity_curve.append({
                'datetime': date.strftime('%Y-%m-%d'),
                'equity': float(value)
            })

    return {
        'summary': summary,
        'trades': trades,
        'equity_curve': equity_curve
    }