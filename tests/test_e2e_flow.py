import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import db
from modules.auth import hash_password, verify_password
from utils.ml import clean_transactions_df, ml_classifier, SpendingPredictor, AnomalyDetector
from utils.gemini import ask_gemini_financial_question, parse_plain_language_transaction, generate_saving_tips

def test_e2e():
    print("=== Testing 1. Registration & Auth ===")
    email = "test_e2e_user@example.com"
    pwd = "password123"
    pwd_hash = hash_password(pwd)
    
    user = db.add_user("Test User", email, pwd_hash)
    assert user["email"] == email
    assert verify_password(pwd, user["password_hash"])
    print(f"User created: {user['user_id']}")

    print("\n=== Testing 2. Load Demo Data (~40 Sample Transactions) ===")
    count = db.load_demo_data(user["user_id"])
    print(f"Demo data inserted: {count} transactions")

    print("\n=== Testing 3. Data Cleaning & Transaction Retrieval ===")
    raw_txns = db.get_transactions(user["user_id"])
    df = clean_transactions_df(raw_txns)
    print(f"Cleaned transactions count: {len(df)}")
    assert len(df) == count

    print("\n=== Testing 4. ML Auto-Categorization ===")
    pred_food = ml_classifier.predict_category("Swiggy pizza delivery")
    pred_travel = ml_classifier.predict_category("Uber cab fare")
    print(f"Predicted Category for 'Swiggy pizza delivery': {pred_food}")
    print(f"Predicted Category for 'Uber cab fare': {pred_travel}")

    print("\n=== Testing 5. Budget Progress & Limits ===")
    budgets = db.get_budgets(user["user_id"])
    print(f"User budgets defined: {len(budgets)} categories")

    print("\n=== Testing 6. ML Spending Prediction & Anomaly Detection ===")
    pred = SpendingPredictor.predict_next_month_spending(df)
    print(f"Predicted Next Month Expense: Rs. {pred['predicted_amount']:,.2f} ({pred['status']})")
    
    anomalies = AnomalyDetector.detect_anomalies(df, contamination=0.08)
    if "is_anomaly" in anomalies.columns:
        flagged = anomalies[anomalies["is_anomaly"] == True]
        print(f"Anomalies detected: {len(flagged)}")

    print("\n=== Testing 7. Gemini AI Q&A & Plain Language Parser ===")
    summary_text = f"Total Income: 130000, Total Expenses: 65000"
    answer = ask_gemini_financial_question(summary_text, "How much can I save next month?")
    print(f"Gemini Answer Preview: {answer[:120]}...")

    parsed_prompt = parse_plain_language_transaction("spent 250 on lunch yesterday")
    print(f"Parsed Plain Language Prompt: {parsed_prompt}")

    tips = generate_saving_tips(summary_text)
    print(f"Saving Tips Count: {len(tips)}")

    print("\n[OK] ALL END-TO-END WORKFLOW STEPS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_e2e()
