import os
import pandas as pd
import numpy as np
import talib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

TA_INDICATORS = {
    "SMA": {"display": "SMA", "args": {"period": 20, "price": "close"}},
    "ATR": {"display": "ATR", "args": {"period": 14}},
    "RSI": {"display": "RSI", "args": {"period": 14, "price": "close"}},
    "ADX": {"display": "ADX", "args": {"period": 14}},
    "WILLR": {"display": "Williams %R", "args": {"period": 14}},
    "EMA": {"display": "EMA", "args": {"period": 20, "price": "close"}},
    # Add more indicators as needed
}

# === Dynamic fetchers for dropdowns ===
def get_available_models():
    return ["Logistic Regression", "XGBoost", "Random Forest"]

def get_available_datasets():
    DATA_DIR = "ohlcv_data"
    return [name for name in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, name))]

def get_all_talib_features():
    return [
        {"name": k, "display": v["display"], "args": v["args"]}
        for k, v in TA_INDICATORS.items()
    ]

def get_sample_features(dataset_folder):
    dataset_dir = os.path.join("ohlcv_data", dataset_folder)
    files = [f for f in os.listdir(dataset_dir) if f.endswith(".csv")]
    if not files:
        return []
    df = pd.read_csv(os.path.join(dataset_dir, files[0]))
    return list(df.columns)

def get_talib_series(df, ftype, args):
    """Dynamically compute a TA-Lib indicator with robust arg parsing."""
    price = args.get("price", "close")
    period = int(args.get("period", 14))
    if ftype == "SMA":
        return talib.SMA(df[price], timeperiod=period)
    if ftype == "EMA":
        return talib.EMA(df[price], timeperiod=period)
    if ftype == "ATR":
        return talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
    if ftype == "RSI":
        return talib.RSI(df[price], timeperiod=period)
    if ftype == "ADX":
        return talib.ADX(df['high'], df['low'], df['close'], timeperiod=period)
    if ftype == "WILLR":
        return talib.WILLR(df['high'], df['low'], df['close'], timeperiod=period)
    raise NotImplementedError(f"{ftype} not implemented.")

def run_training_with_capture(model_type, dataset, feature_configs):
    """
    Loads ALL CSVs from selected dataset directory.
    Calculates all user-selected features for every stock.
    Stacks all rows (with symbol info) for ML training.
    """
    logs = []
    dataset_dir = os.path.join("ohlcv_data", dataset)
    all_files = [f for f in os.listdir(dataset_dir) if f.endswith(".csv")]
    if not all_files:
        return {"status": "error", "error": "No CSV files found in selected dataset!", "logs": ""}

    dfs = []
    for file in all_files:
        try:
            df = pd.read_csv(os.path.join(dataset_dir, file))
            symbol = os.path.splitext(file)[0]
            df['symbol'] = symbol
            orig_len = len(df)
            df = df.dropna(subset=["open", "high", "low", "close", "volume"]).reset_index(drop=True)
            if len(df) < 50:
                logs.append(f"Skipped {symbol} (not enough data: {len(df)})")
                continue

            feature_cols = []
            for feat in feature_configs:
                ftype = feat['type']
                fid = f"{symbol}_{feat['id']}"  # unique per-stock, e.g. NSE_ADANIPORTS-EQ_SMA_1
                args = feat['args']
                try:
                    df[fid] = get_talib_series(df, ftype, args)
                    feature_cols.append(fid)
                    logs.append(f"{symbol}: Added {fid}: {ftype}({args})")
                except Exception as ex:
                    logs.append(f"{symbol}: Failed to compute {ftype}: {ex}")

            # Label: 1 if next close > current close, else 0 (change as needed)
            df["label"] = (df['close'].shift(-1) > df['close']).astype(int)
            df = df.dropna(subset=feature_cols + ["label"])
            if len(df) >= 50:
                dfs.append(df[feature_cols + ["label", "symbol"]])
            else:
                logs.append(f"{symbol}: Not enough valid rows after features ({len(df)})")
        except Exception as ex:
            logs.append(f"Failed to process {file}: {ex}")

    if not dfs:
        return {"status": "error", "error": "No valid data after feature engineering!", "logs": "\n".join(logs)}
    df_all = pd.concat(dfs, axis=0, ignore_index=True)
    logs.append(f"Final training set size: {len(df_all)} rows, {len(df_all.columns)-2} features")

    # ML: Use only feature columns
    feature_cols = [c for c in df_all.columns if c not in ("label", "symbol")]
    X = df_all[feature_cols]
    y = df_all["label"]

    # Robust check
    if X.shape[0] < 100 or len(feature_cols) == 0:
        return {"status": "error", "error": "Not enough data/features after filtering!", "logs": "\n".join(logs)}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    logs.append(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    if model_type == "Random Forest":
        clf = RandomForestClassifier(random_state=42)
    elif model_type == "Logistic Regression":
        clf = LogisticRegression(max_iter=1000, random_state=42)
    elif model_type == "XGBoost":
        clf = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric="logloss")
    else:
        clf = RandomForestClassifier(random_state=42)

    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    logs.append(f"Test Accuracy: {score:.4f}")

    # Feature importance plot
    fi_img, shap_img, feature_importances = None, None, None
    if hasattr(clf, "feature_importances_"):
        plt.figure(figsize=(6, 3))
        idx = np.argsort(clf.feature_importances_)[::-1][:12]
        plt.barh(np.array(feature_cols)[idx], np.array(clf.feature_importances_)[idx], color="#1976d2")
        plt.title("Feature Importance (Top 12)")
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        fi_img = base64.b64encode(buf.getvalue()).decode()
        feature_importances = list(np.array(clf.feature_importances_)[idx])
        logs.append("Feature importance plot generated.")

    # SHAP plot (optional)
    try:
        import shap
        explainer = shap.Explainer(clf, X_train)
        shap_values = explainer(X_test)
        plt.figure(figsize=(6, 3))
        shap.summary_plot(shap_values, X_test, show=False, plot_type="bar")
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        shap_img = base64.b64encode(buf.getvalue()).decode()
        logs.append("SHAP plot generated.")
    except Exception as ex:
        logs.append(f"SHAP plot error: {ex}")

    return {
        "status": "success",
        "message": "Training completed successfully.",
        "features": feature_cols,
        "feature_importances": feature_importances,
        "logs": "\n".join(logs),
        "fi_img": fi_img,
        "shap_img": shap_img
    }
