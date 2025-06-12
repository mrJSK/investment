ML ScreenerX: Machine Learning Model Trainer
ML ScreenerX is a Django web application that provides an interactive dashboard for training, evaluating, and visualizing machine learning models on financial time-series data. It is designed to help users quickly experiment with different models, features, and datasets without writing any code.

🌟 Features
Interactive Web UI: A clean, modern dashboard for controlling the training process.
Model Selection: Train and compare various classification models, including Logistic Regression, Random Forest, and XGBoost.
Dynamic Feature Engineering: Add technical analysis indicators (e.g., SMA, EMA, RSI, ATR) as features and configure their parameters on the fly.
Dataset Management: Easily switch between different datasets of OHLCV (Open, High, Low, Close, Volume) data.
Rich Results Visualization:
Detailed performance reports including accuracy, classification report, and confusion matrix.
Interactive charts for Feature Importance and SHAP Values to understand model predictions.
Live training logs to monitor the process.
User-Friendly Interface: Includes a progress bar during training, dark mode, and a responsive layout.
⚙️ How It Works
The application is built with a Django backend and a vanilla JavaScript frontend that uses jQuery, Bootstrap, and Chart.js.

Backend (Django):

views.py: Handles HTTP requests, serves the HTML dashboard, and manages the AJAX calls for model training.
train_utils.py: Contains the core logic for data processing, feature engineering, model training, and evaluation. It uses pandas for data manipulation, scikit-learn and xgboost for modeling, and matplotlib for generating plots.
urls.py: Defines the URL routes for the dashboard, training endpoint, and other AJAX helpers.
Frontend (HTML/CSS/JS):

dashboard.html: The main template for the user interface.
dashboard.js: Manages all client-side interactivity, including adding/configuring features, submitting the training form via AJAX, and rendering the results and charts.
dashboard.css: Custom styling for the application.