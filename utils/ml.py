import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import IsolationForest

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

def clean_transactions_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pandas data cleaning function.
    Validates types, converts dates, fills missing values, and sorts chronologically.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["txn_id", "user_id", "category_id", "date", "amount", "type", "description"])

    df = df.copy()

    # Required columns check
    for col in ["txn_id", "user_id", "category_id", "date", "amount", "type", "description"]:
        if col not in df.columns:
            df[col] = ""

    # Clean description
    df["description"] = df["description"].astype(str).str.strip()

    # Clean amount
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df = df[df["amount"] >= 0].copy()

    # Clean type
    df["type"] = df["type"].astype(str).str.strip().str.capitalize()
    df.loc[~df["type"].isin(["Income", "Expense"]), "type"] = "Expense"

    # Clean date
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["date"]).copy()

    # Sort by date ascending
    df = df.sort_values(by="date", ascending=True).reset_index(drop=True)
    return df

class CategoryClassifier:
    """
    Scikit-learn model for automatic expense categorization based on text descriptions.
    Uses TF-IDF Vectorizer + Logistic Regression.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', min_df=1)
        self.model = LogisticRegression(max_iter=200, C=1.0)
        self.is_trained = False
        self._train_initial_model()

    def _train_initial_model(self):
        sample_path = os.path.join(DATA_DIR, "sample_descriptions.csv")
        if os.path.exists(sample_path):
            try:
                df_sample = pd.read_csv(sample_path)
                if not df_sample.empty and "description" in df_sample.columns and "category" in df_sample.columns:
                    X = self.vectorizer.fit_transform(df_sample["description"].astype(str))
                    y = df_sample["category"].astype(str)
                    self.model.fit(X, y)
                    self.is_trained = True
            except Exception:
                self.is_trained = False

    def train_on_user_data(self, user_df: pd.DataFrame, category_map: dict):
        """Re-trains/fine-tunes the model including user historical transactions."""
        sample_path = os.path.join(DATA_DIR, "sample_descriptions.csv")
        data_list = []

        if os.path.exists(sample_path):
            try:
                df_sample = pd.read_csv(sample_path)
                data_list.append(df_sample[["description", "category"]])
            except Exception:
                pass

        if user_df is not None and not user_df.empty:
            df_user = user_df.copy()
            id_to_name = category_map.get("id_to_name", {})
            df_user["category"] = df_user["category_id"].map(id_to_name)
            df_user = df_user.dropna(subset=["description", "category"])
            if not df_user.empty:
                data_list.append(df_user[["description", "category"]])

        if data_list:
            combined = pd.concat(data_list, ignore_index=True)
            combined["description"] = combined["description"].astype(str).str.strip()
            combined = combined[combined["description"] != ""]
            if len(combined) >= 5:
                X = self.vectorizer.fit_transform(combined["description"])
                y = combined["category"]
                self.model.fit(X, y)
                self.is_trained = True

    def predict_category(self, description: str) -> str:
        """Predicts category name for a given expense description text."""
        if not description or not str(description).strip():
            return "Other"

        if not self.is_trained:
            return "Other"

        try:
            X_vec = self.vectorizer.transform([str(description).strip()])
            pred = self.model.predict(X_vec)[0]
            return str(pred)
        except Exception:
            return "Other"

class SpendingPredictor:
    """
    Predicts next month spending total using Linear Regression fit on monthly expense totals.
    """
    @staticmethod
    def predict_next_month_spending(df_txns: pd.DataFrame) -> dict:
        if df_txns is None or df_txns.empty:
            return {"predicted_amount": 0.0, "historical_avg": 0.0, "status": "Insufficient Data", "trend": "flat"}

        df_expenses = df_txns[df_txns["type"] == "Expense"].copy()
        if df_expenses.empty:
            return {"predicted_amount": 0.0, "historical_avg": 0.0, "status": "No Expense History", "trend": "flat"}

        df_expenses["month"] = pd.to_datetime(df_expenses["date"]).dt.to_period("M").astype(str)
        monthly_summary = df_expenses.groupby("month")["amount"].sum().reset_index()

        if len(monthly_summary) == 0:
            return {"predicted_amount": 0.0, "historical_avg": 0.0, "status": "No Data", "trend": "flat"}

        avg_spending = float(monthly_summary["amount"].mean())

        if len(monthly_summary) < 2:
            return {
                "predicted_amount": avg_spending,
                "historical_avg": avg_spending,
                "status": "Single Month Baseline",
                "trend": "neutral"
            }

        # Fit Linear Regression on month indices [0, 1, 2...]
        monthly_summary = monthly_summary.sort_values(by="month").reset_index(drop=True)
        X = np.arange(len(monthly_summary)).reshape(-1, 1)
        y = monthly_summary["amount"].values

        model = LinearRegression()
        model.fit(X, y)

        next_month_idx = len(monthly_summary)
        pred_val = float(model.predict([[next_month_idx]])[0])
        pred_val = max(0.0, round(pred_val, 2))

        slope = model.coef_[0]
        if slope > 500:
            trend = "upward"
        elif slope < -500:
            trend = "downward"
        else:
            trend = "stable"

        return {
            "predicted_amount": pred_val,
            "historical_avg": round(avg_spending, 2),
            "status": "ML Regression Model",
            "trend": trend,
            "monthly_history": monthly_summary
        }

class AnomalyDetector:
    """
    Detects unusual/outlier expenses using Scikit-learn IsolationForest.
    """
    @staticmethod
    def detect_anomalies(df_txns: pd.DataFrame, contamination: float = 0.08) -> pd.DataFrame:
        if df_txns is None or df_txns.empty:
            return pd.DataFrame()

        df_expenses = df_txns[df_txns["type"] == "Expense"].copy()
        if len(df_expenses) < 4:
            df_expenses["is_anomaly"] = False
            return df_expenses

        # Features: amount
        amounts = df_expenses[["amount"]].values

        try:
            iso = IsolationForest(contamination=contamination, random_state=42)
            preds = iso.fit_predict(amounts)
            # -1 represents anomaly, 1 represents normal
            df_expenses["is_anomaly"] = preds == -1
        except Exception:
            df_expenses["is_anomaly"] = False

        return df_expenses

# Global singleton classifier instance
ml_classifier = CategoryClassifier()
