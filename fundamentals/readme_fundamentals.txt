Of course! Based on the files you've provided, here is a detailed README.md for your fundamentals Django app.

Django App: fundamentals
Overview
The fundamentals app is a comprehensive Django application designed for financial analysis of publicly traded companies. It scrapes detailed financial data from an external source (screener.in), stores it in a structured relational database, and presents it to the user through a rich, dynamic, and interactive web interface.

The application allows users to browse companies, view them categorized by market capitalization, and perform a deep-dive analysis into a company's financial health, performance metrics, and peer comparison. It also includes an optional AI-driven analysis feature to generate qualitative pros and cons.

Features
Data Models: Robust database schema to store company information, including hierarchical industry classifications.
Web Scraper: A powerful management command to download and process company data.
REST APIs: A set of APIs to serve the financial data to the frontend.
Dynamic Frontend: A responsive, single-page-like interface built with vanilla JavaScript and Tailwind CSS for data visualization.
AI-Powered Analysis: Integrates with a local AI model to automatically generate financial pros and cons for each company.
Components
1. Data Models (models.py)
The app consists of two core models:

IndustryClassification: A self-referencing model that creates a hierarchical tree structure for industry categories (e.g., Commodities > Metals & Mining > Industrial Minerals). This allows for precise classification and effective peer grouping.
Company: The central model that stores all data for a single company. Key fields include:
Core Info: name, symbol, website, about, bse_code, nse_code.
Key Ratios: market_cap, current_price, stock_pe, roce, roe, dividend_yield, etc.
Financial Statements: quarterly_results, profit_loss_statement, balance_sheet, and cash_flow_statement are stored as JSON, preserving the original table structure.
Growth & Shareholding: compounded_sales_growth, stock_price_cagr, and shareholding_pattern are also stored as JSON.
Analysis: pros and cons fields to store lists of strengths and weaknesses.
2. Management Command (management/commands/latest_scrape.py)
This is the data engine of the application. It's a powerful script designed to populate the database.

Usage: python manage.py latest_scrape [--mode <all|download|process>]

--mode download: Fetches company pages from screener.in and saves the raw HTML files to the data/scraped_html/ directory.
--mode process: Parses the local HTML files in the storage directory, extracts all relevant data, and populates the Company and IndustryClassification models in the database.
--mode all (default): Runs both the download and process phases sequentially.
3. API Endpoints (views.py & urls.py)
The app exposes several API endpoints to make data available to the frontend.

GET /fundamentals/api/companies/
Description: Returns a flat list of all companies with their name and symbol. Used to populate the sidebar navigation.
GET /fundamentals/api/market-cap-data/
Description: Returns all companies categorized into large_caps, mid_caps, and small_caps based on their market capitalization. Used for the default landing page view.
GET /fundamentals/api/company/<str:symbol>/
Description: The main data endpoint. Returns a complete JSON object with all financial details for the specified company symbol. It also dynamically finds peer companies and attempts to generate pros and cons by calling a local AI model at http://localhost:11434/api/generate.
4. Frontend (fundamentals.html & main.js)
The user interface is a single, dynamic page that provides a seamless Browse experience.

Structure: The page is divided into a searchable company list in the sidebar and a main content area.
Views:
Market Cap View: The default view, showing companies grouped into Large, Mid, and Small Cap columns.
Deep Dive View: Shown when a company is selected. This view renders all the detailed financial tables, key metrics, pros/cons, peer comparisons, and growth charts for the selected company.
Functionality:
Dynamic Loading: All data is fetched asynchronously from the APIs without requiring page reloads.
Client-Side Search: Users can instantly filter the company list in the sidebar and within the market cap categories.
Interactive Tables: Financial data is rendered in clearly formatted tables. Peer company names are clickable, allowing for quick navigation between related companies.