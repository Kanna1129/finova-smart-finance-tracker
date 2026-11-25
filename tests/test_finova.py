import os
import sys
import pytest
import pandas as pd

# Add parent directory to sys.path so modules can be imported directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ml import clean_transactions_df, ml_classifier, SpendingPredictor
from utils.db import db

def test_data_cleaning():
    """Test Pandas data cleaning function."""
    raw_data = pd.DataFrame([
        {"txn_id": "1", "user_id": "U1", "category_id": "CAT-001", "date": "2026-10-01", "amount": "250.50", "type": "expense", "description": " Swiggy Dinner "},
        {"txn_id": "2", "user_id": "U1", "category_id": "CAT-008", "date": "2026-10-02", "amount": "-100", "type": "income", "description": "Salary"},
        {"txn_id": "3", "user_id": "U1", "category_id": "CAT-002", "date": "invalid-date", "amount": "50", "type": "expense", "description": "Cab"}
    ])

    cleaned = clean_transactions_df(raw_data)

    assert isinstance(cleaned, pd.DataFrame)
    assert len(cleaned) == 1  # Invalid date and negative amount dropped
    assert cleaned.iloc[0]["amount"] == 250.50
    assert cleaned.iloc[0]["type"] == "Expense"
    assert cleaned.iloc[0]["description"] == "Swiggy Dinner"

def test_category_prediction():
    """Test ML TF-IDF + Logistic Regression category prediction."""
    pred_food = ml_classifier.predict_category("Starbucks coffee and bagel")
    assert isinstance(pred_food, str)
    assert pred_food in ["Food", "Other"]

    pred_travel = ml_classifier.predict_category("Uber cab ride to office")
    assert isinstance(pred_travel, str)

def test_database_transaction():
    """Test saving and reading transactions from database."""
    test_user_id = "TEST-USER-999"
    
    txn = db.add_transaction(
        user_id=test_user_id,
        category_id="CAT-001",
        date="2026-10-10",
        amount=450.0,
        txn_type="Expense",
        description="Test Pytest Transaction"
    )

    assert txn["user_id"] == test_user_id
    assert txn["amount"] == 450.0

    txns_df = db.get_transactions(test_user_id)
    assert not txns_df.empty
    assert test_user_id in txns_df["user_id"].values
    
    # Cleanup test transaction
    db.delete_transaction(txn["txn_id"])

def test_spending_prediction():
    """Test spending prediction ML logic."""
    df_txns = pd.DataFrame([
        {"txn_id": "1", "user_id": "U1", "category_id": "C1", "date": "2026-08-15", "amount": 10000, "type": "Expense", "description": "M1"},
        {"txn_id": "2", "user_id": "U1", "category_id": "C1", "date": "2026-09-15", "amount": 12000, "type": "Expense", "description": "M2"},
        {"txn_id": "3", "user_id": "U1", "category_id": "C1", "date": "2026-10-15", "amount": 14000, "type": "Expense", "description": "M3"}
    ])

    pred = SpendingPredictor.predict_next_month_spending(df_txns)
    assert "predicted_amount" in pred
    assert pred["predicted_amount"] > 0
