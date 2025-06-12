Django Financial Dashboard
This project is a comprehensive, real-time financial dashboard built with Django. It scrapes, processes, and displays a wide range of financial data, including market news, corporate announcements, and financial reports from the National Stock Exchange (NSE) of India. The frontend is a dynamic, single-page-style interface that fetches data asynchronously, providing a responsive user experience.

✨ Key Features
Real-time Market News: Scrapes the latest market news from sources like CNBCTV18, analyzes article content, and displays it in a live feed.
AI-Powered Sentiment Analysis: Utilizes a pre-trained FinBERT model (ProsusAI/finbert) to perform sentiment analysis on news articles, classifying them as Positive, Negative, or Neutral and suggesting a corresponding Buy, Sell, or Hold action.
Corporate Announcements: Fetches and categorizes official corporate announcements directly from the NSE RSS feeds, including:
Operational news (new orders, contracts, acquisitions)
Financial actions (dividends, splits, bonuses)
Board meetings and financial results.
Financial Report Parsing: Automatically downloads and parses both Annual and Quarterly financial reports filed in XBRL format. It extracts key financial statements like the P&L and Balance Sheet and displays them in a structured, easy-to-read format.
Stocks in Focus: Identifies and extracts specific stock-related news from "Stocks to Watch" articles for quick insights.
Asynchronous Frontend: The dashboard loads data for each section (News, Reports, Announcements) independently using asynchronous API calls, preventing long-loading scrapers from blocking the UI.
Modern UI: A clean and responsive user interface built with Tailwind CSS, featuring interactive elements like tabs and accordions for a smooth user experience.
Caching System: Implements caching for API responses to minimize redundant scraping, reduce load times, and avoid rate-limiting from data sources.
🏛️ Architecture
The application is designed with a clear separation of concerns:

Backend (Django): Serves as a powerful data processing engine and API provider.

services.py: The core of the application. This file contains all the business logic for scraping websites (requests, BeautifulSoup), parsing RSS feeds (feedparser), performing sentiment analysis (transformers), parsing XBRL financial statements (xml.etree.ElementTree), and saving data to the database.
models.py: Defines the database schema for storing all financial data, including articles, reports, and corporate actions.
views.py: Provides the API endpoints that the frontend consumes. Each view calls a corresponding service function to fetch the required data.
urls.py: Maps the API endpoint URLs to their respective views.
Frontend (Vanilla JavaScript & Tailwind CSS):

dashboard.html: The main template for the dashboard, structured with Tailwind CSS.
dashboard.js: Handles all client-side logic. It makes fetch requests to the Django backend APIs, receives the JSON data, and dynamically renders the HTML for each section of the dashboard. This approach creates a seamless, single-page application experience.
🛠️ Technology Stack
Backend:

Python 3.x
Django 4.x
requests: For making HTTP requests to external sites.
BeautifulSoup4: For parsing HTML content.
feedparser: For parsing RSS/XML feeds from the NSE.
transformers (Hugging Face): For loading the FinBERT model.
torch: The underlying framework for the sentiment analysis model.
Frontend:

HTML5
Tailwind CSS
Vanilla JavaScript (ES6+)
Database:

Django ORM (compatible with PostgreSQL, SQLite, etc.)
🚀 Getting Started
Follow these instructions to get a copy of the project up and running on your local machine.

Prerequisites
Python 3.8+ and pip
A virtual environment tool (e.g., venv)