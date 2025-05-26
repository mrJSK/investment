# import os
# import traceback
# import pandas as pd
# import numpy as np
# import talib
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from xgboost import XGBClassifier
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import classification_report, confusion_matrix
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import base64
# from io import BytesIO

# TA_INDICATORS = {
#     "SMA": {"display": "SMA", "args": {"period": 20, "price": "close"}},
#     "ATR": {"display": "ATR", "args": {"period": 14}},
#     "RSI": {"display": "RSI", "args": {"period": 14, "price": "close"}},
#     "ADX": {"display": "ADX", "args": {"period": 14}},
#     "WILLR": {"display": "Williams %R", "args": {"period": 14}},
#     "EMA": {"display": "EMA", "args": {"period": 20, "price": "close"}},
#     # Add more indicators as needed
# }

# def get_available_models():
#     return ["Logistic Regression", "XGBoost", "Random Forest"]

# def get_available_datasets():
#     DATA_DIR = "ohlcv_data"
#     return [name for name in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, name))]

# def get_all_talib_features():
#     return [
#         {"name": k, "display": v["display"], "args": v["args"]}
#         for k, v in TA_INDICATORS.items()
#     ]

# def get_sample_features(dataset_folder):
#     dataset_dir = os.path.join("ohlcv_data", dataset_folder)
#     files = [f for f in os.listdir(dataset_dir) if f.endswith(".csv")]
#     if not files:
#         return []
#     df = pd.read_csv(os.path.join(dataset_dir, files[0]))
#     return list(df.columns)

# def get_talib_series(df, ftype, args):
#     price = args.get("price", "close")
#     period = int(args.get("period", 14))
#     if ftype == "SMA":
#         return talib.SMA(df[price], timeperiod=period)
#     if ftype == "EMA":
#         return talib.EMA(df[price], timeperiod=period)
#     if ftype == "ATR":
#         return talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
#     if ftype == "RSI":
#         return talib.RSI(df[price], timeperiod=period)
#     if ftype == "ADX":
#         return talib.ADX(df['high'], df['low'], df['close'], timeperiod=period)
#     if ftype == "WILLR":
#         return talib.WILLR(df['high'], df['low'], df['close'], timeperiod=period)
#     raise NotImplementedError(f"{ftype} not implemented.")

# def run_training_with_capture(model_type, dataset, feature_configs):
#     logs = []
#     try:
#         dataset_dir = os.path.join("ohlcv_data", dataset)
#         all_files = [f for f in os.listdir(dataset_dir) if f.endswith(".csv")]
#         if not all_files:
#             return {"status": "error", "error": "No CSV files found in selected dataset!", "logs": ""}

#         dfs = []
#         for file in all_files:
#             try:
#                 df = pd.read_csv(os.path.join(dataset_dir, file))
#                 symbol = os.path.splitext(file)[0]
#                 df['symbol'] = symbol
#                 df = df.dropna(subset=["open", "high", "low", "close", "volume"]).reset_index(drop=True)
#                 if len(df) < 50:
#                     logs.append(f"Skipped {symbol} (not enough data: {len(df)})")
#                     continue

#                 feature_cols = []
#                 for feat in feature_configs:
#                     ftype = feat['type']
#                     fid = f"{symbol}_{feat['id']}"  # unique per-stock
#                     args = feat['args']
#                     try:
#                         df[fid] = get_talib_series(df, ftype, args)
#                         feature_cols.append(fid)
#                         logs.append(f"{symbol}: Added {fid}: {ftype}({args})")
#                     except Exception as ex:
#                         logs.append(f"{symbol}: Failed to compute {ftype}: {ex}")

#                 df["label"] = (df['close'].shift(-1) > df['close']).astype(int)
#                 df = df.dropna(subset=feature_cols + ["label"])
#                 if len(df) >= 50:
#                     dfs.append(df[feature_cols + ["label", "symbol"]])
#                 else:
#                     logs.append(f"{symbol}: Not enough valid rows after features ({len(df)})")
#             except Exception as ex:
#                 logs.append(f"Failed to process {file}: {ex}")

#         if not dfs:
#             return {"status": "error", "error": "No valid data after feature engineering!", "logs": "\n".join(logs)}
#         df_all = pd.concat(dfs, axis=0, ignore_index=True)
#         logs.append(f"Final training set size: {len(df_all)} rows, {len(df_all.columns)-2} features")

#         feature_cols = [c for c in df_all.columns if c not in ("label", "symbol")]
#         X = df_all[feature_cols]
#         y = df_all["label"]

#         if X.shape[0] < 100 or len(feature_cols) == 0:
#             return {"status": "error", "error": "Not enough data/features after filtering!", "logs": "\n".join(logs)}

#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y, test_size=0.2, random_state=42, stratify=y
#         )
#         logs.append(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

#         if model_type == "Random Forest":
#             clf = RandomForestClassifier(random_state=42)
#         elif model_type == "Logistic Regression":
#             clf = LogisticRegression(max_iter=1000, random_state=42)
#         elif model_type == "XGBoost":
#             clf = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric="logloss")
#         else:
#             clf = RandomForestClassifier(random_state=42)

#         clf.fit(X_train, y_train)
#         score = clf.score(X_test, y_test)
#         logs.append(f"Test Accuracy: {score:.4f}")

#         # --- Detailed HTML Report ---
#         y_pred = clf.predict(X_test)
#         try:
#             cr = classification_report(y_test, y_pred, digits=3, output_dict=False)
#         except Exception as ex:
#             cr = f"Could not compute classification report: {ex}"
#         try:
#             cm = confusion_matrix(y_test, y_pred)
#         except Exception as ex:
#             cm = f"Could not compute confusion matrix: {ex}"
#         report_lines = [
#             f"<b>Model:</b> {model_type}",
#             f"<b>Train Rows:</b> {len(X_train)}",
#             f"<b>Test Rows:</b> {len(X_test)}",
#             f"<b>Accuracy:</b> {score:.4f}",
#             "<b>Classification Report:</b><br><pre style='font-size:13px;'>" + str(cr) + "</pre>",
#             f"<b>Confusion Matrix:</b><br><pre style='font-size:13px;'>{cm}</pre>",
#         ]
#         if hasattr(clf, "feature_importances_"):
#             idx = np.argsort(clf.feature_importances_)[::-1][:3]
#             top_feats = ', '.join(np.array(feature_cols)[idx])
#             report_lines.append(f"<b>Top Features:</b> {top_feats}")
#         report_html = "<br>".join(report_lines)

#         # --- Feature Importance Plot ---
#         fi_img, shap_img, feature_importances = None, None, None
#         fi_error, shap_error = "", ""
#         if hasattr(clf, "feature_importances_"):
#             try:
#                 plt.figure(figsize=(6, 3))
#                 idx = np.argsort(clf.feature_importances_)[::-1][:12]
#                 plt.barh(np.array(feature_cols)[idx], np.array(clf.feature_importances_)[idx], color="#1976d2")
#                 plt.title("Feature Importance (Top 12)")
#                 plt.tight_layout()
#                 buf = BytesIO()
#                 plt.savefig(buf, format='png')
#                 plt.close()
#                 fi_img = base64.b64encode(buf.getvalue()).decode()
#                 feature_importances = list(np.array(clf.feature_importances_)[idx])
#                 logs.append("Feature importance plot generated.")
#             except Exception as ex:
#                 fi_error = str(ex)
#                 logs.append(f"Feature importance error: {fi_error}")
#         else:
#             logs.append("Model does not have feature_importances_ attribute.")

#         # --- SHAP Plot ---
#         try:
#             import shap
#             explainer = shap.Explainer(clf, X_train)
#             shap_values = explainer(X_test)
#             plt.figure(figsize=(6, 3))
#             shap.summary_plot(shap_values, X_test, show=False, plot_type="bar")
#             buf = BytesIO()
#             plt.savefig(buf, format='png')
#             plt.close()
#             shap_img = base64.b64encode(buf.getvalue()).decode()
#             logs.append("SHAP plot generated.")
#         except Exception as ex:
#             shap_error = str(ex)
#             logs.append(f"SHAP plot error: {shap_error}")

#         return {
#             "status": "success",
#             "message": "Training completed successfully.",
#             "features": feature_cols,
#             "feature_importances": feature_importances,
#             "logs": "\n".join(logs),
#             "fi_img": fi_img,
#             "shap_img": shap_img,
#             "report": report_html,
#             "fi_error": fi_error,
#             "shap_error": shap_error,
#         }

#     except Exception as ex:
#         tb = traceback.format_exc()
#         logs.append(f"\n\n[ERROR]: {str(ex)}\n{tb}")
#         return {
#             "status": "error",
#             "error": str(ex),
#             "logs": "\n".join(logs)
#         }

# def to_python_type(obj):
#     # Recursively convert numpy types to Python types
#     if isinstance(obj, dict):
#         return {k: to_python_type(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [to_python_type(v) for v in obj]
#     elif isinstance(obj, np.generic):
#         return obj.item()
#     elif isinstance(obj, np.ndarray):
#         return obj.tolist()
#     else:
#         return obj

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_sample_weight
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import json

# --- TA-Lib-like feature map (expand as needed) ---
TA_INDICATORS = {
    "SMA": {"display": "SMA", "args": {"period": 20, "price": "close"}},
    "ATR": {"display": "ATR", "args": {"period": 14}},
    "RSI": {"display": "RSI", "args": {"period": 14, "price": "close"}},
    "EMA": {"display": "EMA", "args": {"period": 20, "price": "close"}},
    # Add more
}

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
    # --- Minimal TA emulation (for demo, replace with real TA-Lib for prod) ---
    price = args.get("price", "close")
    period = int(args.get("period", 14))
    if ftype == "SMA":
        return df[price].rolling(period).mean()
    if ftype == "EMA":
        return df[price].ewm(span=period, adjust=False).mean()
    if ftype == "ATR":
        high, low, close = df["high"], df["low"], df["close"]
        tr = pd.concat([
            (high - low),
            abs(high - close.shift(1)),
            abs(low - close.shift(1))
        ], axis=1).max(axis=1)
        return tr.rolling(period).mean()
    if ftype == "RSI":
        diff = df[price].diff()
        gain = (diff.where(diff > 0, 0)).rolling(period).mean()
        loss = (-diff.where(diff < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    raise NotImplementedError(f"{ftype} not implemented.")

def to_python_type(obj):
    # Recursively convert numpy types to python native
    if isinstance(obj, dict):
        return {k: to_python_type(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_python_type(v) for v in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    return obj

def run_training_with_capture(model_type, dataset, feature_configs):
    import warnings
    warnings.filterwarnings('ignore')
    logs = []
    dataset_dir = os.path.join("ohlcv_data", dataset)
    all_files = [f for f in os.listdir(dataset_dir) if f.endswith(".csv")]
    if not all_files:
        return {"status": "error", "error": "No CSV files found in selected dataset!", "logs": ""}

    dfs = []
    for file in all_files:
        try:
            df = pd.read_csv(os.path.join(dataset_dir, file))
            orig_len = len(df)
            df = df.dropna(subset=["open", "high", "low", "close", "volume"]).reset_index(drop=True)
            if len(df) < 50:
                logs.append(f"Skipped {file} (not enough data: {len(df)})")
                continue

            feature_cols = []
            for feat in feature_configs:
                ftype = feat['type']
                args = feat['args']
                colname = f"{ftype.upper()}_{args.get('period', '')}_{args.get('price', '')}".replace("__", "_")
                # Only use feature name, not stock symbol
                try:
                    df[colname] = get_talib_series(df, ftype, args)
                    feature_cols.append(colname)
                    logs.append(f"{file}: Added {colname}: {ftype}({args})")
                except Exception as ex:
                    logs.append(f"{file}: Failed to compute {ftype}: {ex}")

            # Label (custom logic: can be improved to match your long-term .py)
            df["label"] = (df['close'].shift(-1) > df['close']).astype(int)
            df = df.dropna(subset=feature_cols + ["label"])
            if len(df) >= 50:
                dfs.append(df[feature_cols + ["label"]])
            else:
                logs.append(f"{file}: Not enough valid rows after features ({len(df)})")
        except Exception as ex:
            logs.append(f"Failed to process {file}: {ex}")

    if not dfs:
        return {"status": "error", "error": "No valid data after feature engineering!", "logs": "\n".join(logs)}
    df_all = pd.concat(dfs, axis=0, ignore_index=True)
    logs.append(f"Final training set size: {len(df_all)} rows, {len(df_all.columns)-1} features")

    feature_cols = [c for c in df_all.columns if c != "label"]
    X = df_all[feature_cols]
    y = df_all["label"]

    if X.shape[0] < 100 or len(feature_cols) == 0:
        return {"status": "error", "error": "Not enough data/features after filtering!", "logs": "\n".join(logs)}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    logs.append(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    # --- Model select ---
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

    # --- Report as HTML (match your old pipeline style) ---
    y_pred = clf.predict(X_test)
    from sklearn.metrics import classification_report, confusion_matrix
    cr = classification_report(y_test, y_pred, digits=3, output_dict=False)
    cm = confusion_matrix(y_test, y_pred)
    report_lines = [
        f"<b>Model:</b> {model_type}",
        f"<b>Train Rows:</b> {len(X_train)}",
        f"<b>Test Rows:</b> {len(X_test)}",
        f"<b>Accuracy:</b> {score:.4f}",
        "<b>Classification Report:</b><br><pre style='font-size:13px;'>" + cr + "</pre>",
        f"<b>Confusion Matrix:</b><br><pre style='font-size:13px;'>{cm}</pre>",
    ]
    # Top features (by importance, not by stock)
    if hasattr(clf, "feature_importances_"):
        idx = np.argsort(clf.feature_importances_)[::-1][:3]
        top_feats = ', '.join(np.array(feature_cols)[idx])
        report_lines.append(f"<b>Top Features:</b> {top_feats}")
    report_html = "<br>".join(report_lines)

    # --- Feature Importance Plot (charts.js in frontend) ---
    fi_img, shap_img, feature_importances, fi_labels, shap_labels, fi_values, shap_values = None, None, None, [], [], [], []
    fi_error, shap_error = "", ""
    if hasattr(clf, "feature_importances_"):
        try:
            idx = np.argsort(clf.feature_importances_)[::-1][:12]
            fi_labels = list(np.array(feature_cols)[idx])
            fi_values = list(np.array(clf.feature_importances_)[idx])
            feature_importances = fi_values
            logs.append("Feature importance computed.")
        except Exception as ex:
            fi_error = str(ex)
            logs.append(f"Feature importance error: {fi_error}")
    else:
        logs.append("Model does not have feature_importances_ attribute.")

    # --- SHAP Values (top 12, for bar chart) ---
    try:
        import shap
        explainer = shap.Explainer(clf, X_train)
        shap_values_ = explainer(X_test)
        vals = np.abs(shap_values_.values).mean(axis=0)
        idx = np.argsort(vals)[::-1][:12]
        shap_labels = list(np.array(feature_cols)[idx])
        shap_values = list(vals[idx])
        logs.append("SHAP computed.")
    except Exception as ex:
        shap_error = str(ex)
        logs.append(f"SHAP plot error: {shap_error}")

    # --- Ensure only python built-in types are sent to JSON ---
    return to_python_type({
        "status": "success",
        "message": "Training completed successfully.",
        "features": feature_cols,
        "feature_importances": feature_importances,
        "fi_labels": fi_labels,
        "fi_values": fi_values,
        "shap_labels": shap_labels,
        "shap_values": shap_values,
        "logs": "\n".join(logs),
        "report": report_html,
        "fi_error": fi_error,
        "shap_error": shap_error,
    })
