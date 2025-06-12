Django Financial Screener & Backtester
This is a powerful, web-based financial screening and backtesting application built with Django. It features a custom query language that allows users to build complex screening criteria using a wide array of technical indicators across multiple timeframes. Users can run live scans or execute historical backtests on their strategies, with results visualized through an interactive interface.

Key Features
Dynamic Query Builder: A flexible frontend allows users to build complex queries using a custom Domain-Specific Language (DSL).
Custom DSL: Supports a wide range of technical indicators, logical operators (AND, OR), comparisons (>, crosses above), and nested indicator calculations.
Multi-Timeframe Analysis: A single query can seamlessly mix indicators from different timeframes (e.g., Daily SMA(CLOSE(), 20) > 15min SMA(CLOSE(), 50)).
Live Screener*: Scans the latest available market data to find symbols that match the user's defined criteria.
Integrated Backtesting Engine: Leverages the powerful backtrader library to test screener queries as trading strategies over historical data.
Detailed Backtest Reports: Provides key performance metrics like Total Return, Win Rate, and Max Drawdown, along with a trade-by-trade list and an interactive equity curve chart powered by Lightweight Charts.
Save & Load Queries: Users can name, save, and reload their custom-built scans for future use.
Extensible Indicator Library: Easily add new custom indicators in Python, which automatically become available in the frontend UI.
How It Works
The application follows a modern single-page application (SPA) architecture:

Frontend (UI): The user builds a query (e.g., Daily RSI(CLOSE(), 14) < 30) in a textarea on the dashboard.html page. The JavaScript in builder.js provides autocompletion and handles UI interactions.
DSL Parsing: When a scan or backtest is run, the query string is parsed on the frontend into an Abstract Syntax Tree (AST) using a custom Pratt parser.
API Request: The AST is sent as a JSON payload to the Django backend.
Backend Evaluation:
The Django view (screener/views.py) receives the AST.
The eval_ast_node function recursively walks the AST. For each stock symbol, it loads the necessary OHLCV data using screener/indicator_utils.py.
It calculates the required TA-Lib and custom indicators on the fly.
The final result for each symbol is a boolean (True if it matches, False otherwise).
Backtesting: If a backtest is triggered, the AST is passed to the backtrader engine (screener/backtest_engine.py). The ScreenerStrategy uses eval_ast_node on each bar of historical data to generate buy signals.
Core Technologies
Backend: Django 4+, Pandas, NumPy
Data & Analysis: TA-Lib, backtrader
DSL: Lark-parser for backend AST generation (if needed, though frontend parsing is primary).
Frontend: Vanilla JavaScript (ES6+), Tailwind CSS, Lightweight Charts™
Testing: Pytest