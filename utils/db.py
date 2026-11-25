import os
import uuid
import datetime
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Constants
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_CATEGORIES = [
    {"category_id": "CAT-001", "category_name": "Food"},
    {"category_id": "CAT-002", "category_name": "Travel"},
    {"category_id": "CAT-003", "category_name": "Bills"},
    {"category_id": "CAT-004", "category_name": "Shopping"},
    {"category_id": "CAT-005", "category_name": "Health"},
    {"category_id": "CAT-006", "category_name": "Education"},
    {"category_id": "CAT-007", "category_name": "Entertainment"},
    {"category_id": "CAT-008", "category_name": "Salary"},
    {"category_id": "CAT-009", "category_name": "Other"}
]

class Database:
    """
    Database interface for Finova.
    Attempts Google Sheets (gspread) connection if configured.
    Seamlessly falls back to local CSV storage if credentials or Google connection fail.
    """
    def __init__(self):
        self.use_gsheets = False
        self.gc = None
        self.sh = None
        self._init_connection()
        self._init_tables()

    def _init_connection(self):
        """Tries to connect to Google Sheets using service account credentials."""
        sheet_name = os.getenv("GOOGLE_SHEET_NAME")
        if not sheet_name:
            try:
                sheet_name = st.secrets.get("GOOGLE_SHEET_NAME", "Finova_Database")
            except Exception:
                sheet_name = "Finova_Database"

        service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        if not service_account_file:
            try:
                service_account_file = st.secrets.get("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json")
            except Exception:
                service_account_file = "credentials.json"

        has_gcp_secret = False
        try:
            if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
                has_gcp_secret = True
        except Exception:
            has_gcp_secret = False

        if os.path.exists(service_account_file) or has_gcp_secret:
            try:
                import gspread
                from google.oauth2.service_account import Credentials
                
                scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                if os.path.exists(service_account_file):
                    creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)
                else:
                    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
                
                self.gc = gspread.authorize(creds)
                self.sh = self.gc.open(sheet_name)
                self.use_gsheets = True
            except Exception:
                self.use_gsheets = False
        else:
            self.use_gsheets = False

    def _get_csv_path(self, table_name: str) -> str:
        return os.path.join(DATA_DIR, f"{table_name.lower()}.csv")

    def _init_tables(self):
        """Ensures all 5 tables (Users, Transactions, Categories, Budgets, AI_Queries) exist."""
        schemas = {
            "users": ["user_id", "name", "email", "password_hash", "created_at"],
            "transactions": ["txn_id", "user_id", "category_id", "date", "amount", "type", "description"],
            "categories": ["category_id", "category_name"],
            "budgets": ["budget_id", "user_id", "category_id", "monthly_limit"],
            "ai_queries": ["query_id", "user_id", "question", "response", "timestamp"]
        }

        if self.use_gsheets:
            try:
                existing_worksheets = [ws.title for ws in self.sh.worksheets()]
                for table, cols in schemas.items():
                    if table.capitalize() not in existing_worksheets:
                        ws = self.sh.add_worksheet(title=table.capitalize(), rows=100, cols=len(cols))
                        ws.append_row(cols)
                self._seed_categories_gsheets()
                return
            except Exception:
                self.use_gsheets = False

        # CSV Fallback
        for table, cols in schemas.items():
            path = self._get_csv_path(table)
            if not os.path.exists(path):
                df = pd.DataFrame(columns=cols)
                df.to_csv(path, index=False)
        self._seed_categories_csv()

    def _seed_categories_csv(self):
        path = self._get_csv_path("categories")
        df = pd.read_csv(path)
        if df.empty:
            df_cat = pd.DataFrame(DEFAULT_CATEGORIES)
            df_cat.to_csv(path, index=False)

    def _seed_categories_gsheets(self):
        ws = self.sh.worksheet("Categories")
        records = ws.get_all_records()
        if not records:
            for cat in DEFAULT_CATEGORIES:
                ws.append_row([cat["category_id"], cat["category_name"]])

    def _read_table(self, table_name: str) -> pd.DataFrame:
        if self.use_gsheets:
            try:
                ws = self.sh.worksheet(table_name.capitalize())
                records = ws.get_all_records()
                return pd.DataFrame(records)
            except Exception:
                self.use_gsheets = False

        path = self._get_csv_path(table_name)
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                return df
            except Exception:
                return pd.DataFrame()
        return pd.DataFrame()

    def _write_table(self, table_name: str, df: pd.DataFrame):
        if self.use_gsheets:
            try:
                ws = self.sh.worksheet(table_name.capitalize())
                ws.clear()
                ws.append_row(df.columns.tolist())
                ws.append_rows(df.astype(str).values.tolist())
                return
            except Exception:
                self.use_gsheets = False

        path = self._get_csv_path(table_name)
        df.to_csv(path, index=False)

    # --- USERS ---
    def get_users(self) -> pd.DataFrame:
        return self._read_table("users")

    def get_user_by_email(self, email: str):
        df = self._read_table("users")
        if df.empty:
            return None
        matched = df[df["email"].astype(str).str.lower() == email.lower().strip()]
        if not matched.empty:
            return matched.iloc[0].to_dict()
        return None

    def add_user(self, name: str, email: str, password_hash: str) -> dict:
        df = self._read_table("users")
        user_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_user = {
            "user_id": user_id,
            "name": name.strip(),
            "email": email.strip().lower(),
            "password_hash": password_hash,
            "created_at": created_at
        }
        df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
        self._write_table("users", df)
        return new_user

    def update_user_password(self, user_id: str, new_password_hash: str) -> bool:
        df = self._read_table("users")
        if df.empty:
            return False
        mask = df["user_id"].astype(str) == str(user_id)
        if not mask.any():
            return False
        df.loc[mask, "password_hash"] = new_password_hash
        self._write_table("users", df)
        return True

    # --- CATEGORIES ---
    def get_categories(self) -> pd.DataFrame:
        df = self._read_table("categories")
        if df.empty:
            df = pd.DataFrame(DEFAULT_CATEGORIES)
            self._write_table("categories", df)
        return df

    def get_category_map(self) -> dict:
        df = self.get_categories()
        id_to_name = dict(zip(df["category_id"].astype(str), df["category_name"].astype(str)))
        name_to_id = dict(zip(df["category_name"].astype(str), df["category_id"].astype(str)))
        return {"id_to_name": id_to_name, "name_to_id": name_to_id}

    # --- TRANSACTIONS ---
    def get_transactions(self, user_id: str = None) -> pd.DataFrame:
        df = self._read_table("transactions")
        if df.empty:
            df = pd.DataFrame(columns=["txn_id", "user_id", "category_id", "date", "amount", "type", "description"])
            return df
        if user_id:
            df = df[df["user_id"].astype(str) == str(user_id)].copy()
        if not df.empty and "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        return df

    def add_transaction(self, user_id: str, category_id: str, date: str, amount: float, txn_type: str, description: str) -> dict:
        df = self._read_table("transactions")
        txn_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        new_txn = {
            "txn_id": txn_id,
            "user_id": str(user_id),
            "category_id": str(category_id),
            "date": str(date),
            "amount": float(amount),
            "type": str(txn_type),
            "description": str(description).strip()
        }
        df = pd.concat([df, pd.DataFrame([new_txn])], ignore_index=True)
        self._write_table("transactions", df)
        return new_txn

    def update_transaction(self, txn_id: str, category_id: str, date: str, amount: float, txn_type: str, description: str) -> bool:
        df = self._read_table("transactions")
        if df.empty:
            return False
        mask = df["txn_id"].astype(str) == str(txn_id)
        if not mask.any():
            return False
        df.loc[mask, "category_id"] = str(category_id)
        df.loc[mask, "date"] = str(date)
        df.loc[mask, "amount"] = float(amount)
        df.loc[mask, "type"] = str(txn_type)
        df.loc[mask, "description"] = str(description).strip()
        self._write_table("transactions", df)
        return True

    def delete_transaction(self, txn_id: str) -> bool:
        df = self._read_table("transactions")
        if df.empty:
            return False
        df_filtered = df[df["txn_id"].astype(str) != str(txn_id)].copy()
        if len(df_filtered) == len(df):
            return False
        self._write_table("transactions", df_filtered)
        return True

    # --- BUDGETS ---
    def get_budgets(self, user_id: str = None) -> pd.DataFrame:
        df = self._read_table("budgets")
        if df.empty:
            return pd.DataFrame(columns=["budget_id", "user_id", "category_id", "monthly_limit"])
        if user_id:
            df = df[df["user_id"].astype(str) == str(user_id)].copy()
        if not df.empty and "monthly_limit" in df.columns:
            df["monthly_limit"] = pd.to_numeric(df["monthly_limit"], errors="coerce").fillna(0.0)
        return df

    def set_budget(self, user_id: str, category_id: str, monthly_limit: float) -> bool:
        df = self._read_table("budgets")
        user_id_str = str(user_id)
        category_id_str = str(category_id)
        
        if not df.empty:
            mask = (df["user_id"].astype(str) == user_id_str) & (df["category_id"].astype(str) == category_id_str)
            if mask.any():
                df.loc[mask, "monthly_limit"] = float(monthly_limit)
                self._write_table("budgets", df)
                return True
        
        budget_id = f"BDG-{uuid.uuid4().hex[:8].upper()}"
        new_budget = {
            "budget_id": budget_id,
            "user_id": user_id_str,
            "category_id": category_id_str,
            "monthly_limit": float(monthly_limit)
        }
        df = pd.concat([df, pd.DataFrame([new_budget])], ignore_index=True)
        self._write_table("budgets", df)
        return True

    # --- AI QUERIES ---
    def get_ai_queries(self, user_id: str = None) -> pd.DataFrame:
        df = self._read_table("ai_queries")
        if df.empty:
            return pd.DataFrame(columns=["query_id", "user_id", "question", "response", "timestamp"])
        if user_id:
            df = df[df["user_id"].astype(str) == str(user_id)].copy()
        return df

    def save_ai_query(self, user_id: str, question: str, response: str) -> dict:
        df = self._read_table("ai_queries")
        query_id = f"AIQ-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_query = {
            "query_id": query_id,
            "user_id": str(user_id),
            "question": str(question),
            "response": str(response),
            "timestamp": timestamp
        }
        df = pd.concat([df, pd.DataFrame([new_query])], ignore_index=True)
        self._write_table("ai_queries", df)
        return new_query

    # --- DEMO DATA LOADER ---
    def load_demo_data(self, user_id: str) -> int:
        """Inserts ~40 sample realistic transactions for presentation demo."""
        category_map = self.get_category_map()["name_to_id"]
        
        sample_txns = [
            # Income entries
            {"type": "Income", "amount": 65000.0, "category": "Salary", "description": "Monthly Salary Transfer", "days_ago": 60},
            {"type": "Income", "amount": 65000.0, "category": "Salary", "description": "Monthly Salary Transfer", "days_ago": 30},
            {"type": "Income", "amount": 65000.0, "category": "Salary", "description": "Monthly Salary Transfer", "days_ago": 2},
            {"type": "Income", "amount": 5000.0, "category": "Salary", "description": "Freelance Web Design Project", "days_ago": 15},
            {"type": "Income", "amount": 3000.0, "category": "Other", "description": "Cash Cashback Rewards", "days_ago": 8},

            # Expense - Food
            {"type": "Expense", "amount": 450.0, "category": "Food", "description": "Swiggy Dinner Order", "days_ago": 55},
            {"type": "Expense", "amount": 220.0, "category": "Food", "description": "Starbucks Coffee & Snacks", "days_ago": 48},
            {"type": "Expense", "amount": 1200.0, "category": "Food", "description": "Weekend Restaurant Dinner", "days_ago": 40},
            {"type": "Expense", "amount": 350.0, "category": "Food", "description": "Zomato Lunch Order", "days_ago": 28},
            {"type": "Expense", "amount": 1800.0, "category": "Food", "description": "Supermarket Monthly Groceries", "days_ago": 25},
            {"type": "Expense", "amount": 540.0, "category": "Food", "description": "Dominos Pizza Party", "days_ago": 18},
            {"type": "Expense", "amount": 290.0, "category": "Food", "description": "Swiggy Evening Snacks", "days_ago": 12},
            {"type": "Expense", "amount": 1500.0, "category": "Food", "description": "Weekly Family Grocery", "days_ago": 5},
            {"type": "Expense", "amount": 180.0, "category": "Food", "description": "Tea & Coffee Cafe", "days_ago": 1},

            # Expense - Travel
            {"type": "Expense", "amount": 2500.0, "category": "Travel", "description": "Monthly Petrol Refill", "days_ago": 58},
            {"type": "Expense", "amount": 340.0, "category": "Travel", "description": "Uber Cab to Office", "days_ago": 42},
            {"type": "Expense", "amount": 500.0, "category": "Travel", "description": "Metro Card Recharge", "days_ago": 35},
            {"type": "Expense", "amount": 2600.0, "category": "Travel", "description": "Petrol Refill Bike", "days_ago": 27},
            {"type": "Expense", "amount": 420.0, "category": "Travel", "description": "Ola Auto Ride", "days_ago": 14},
            {"type": "Expense", "amount": 4500.0, "category": "Travel", "description": "Flight Ticket to Delhi", "days_ago": 7},

            # Expense - Bills
            {"type": "Expense", "amount": 12000.0, "category": "Bills", "description": "House Rent Payment", "days_ago": 59},
            {"type": "Expense", "amount": 1450.0, "category": "Bills", "description": "Electricity Bill Payment", "days_ago": 50},
            {"type": "Expense", "amount": 999.0, "category": "Bills", "description": "Jio Fiber Broadband Internet", "days_ago": 45},
            {"type": "Expense", "amount": 12000.0, "category": "Bills", "description": "House Rent Payment", "days_ago": 29},
            {"type": "Expense", "amount": 1600.0, "category": "Bills", "description": "Electricity Bill", "days_ago": 20},
            {"type": "Expense", "amount": 999.0, "category": "Bills", "description": "Jio Fiber Wifi Bill", "days_ago": 10},

            # Expense - Shopping
            {"type": "Expense", "amount": 3499.0, "category": "Shopping", "description": "Amazon Headphones", "days_ago": 52},
            {"type": "Expense", "amount": 2100.0, "category": "Shopping", "description": "Myntra Clothes Shopping", "days_ago": 38},
            {"type": "Expense", "amount": 1290.0, "category": "Shopping", "description": "Nike Sports T-Shirt", "days_ago": 22},
            {"type": "Expense", "amount": 4999.0, "category": "Shopping", "description": "Flipkart Smartwatch", "days_ago": 9},

            # Expense - Health
            {"type": "Expense", "amount": 650.0, "category": "Health", "description": "Pharmacy Medicines Apollo", "days_ago": 46},
            {"type": "Expense", "amount": 1500.0, "category": "Health", "description": "Doctor Consultation & Checkup", "days_ago": 24},
            {"type": "Expense", "amount": 850.0, "category": "Health", "description": "Vitamin Supplements", "days_ago": 6},

            # Expense - Education
            {"type": "Expense", "amount": 3600.0, "category": "Education", "description": "Udemy Python & Data Science Course", "days_ago": 51},
            {"type": "Expense", "amount": 1200.0, "category": "Education", "description": "Reference Books & Notebooks", "days_ago": 19},

            # Expense - Entertainment
            {"type": "Expense", "amount": 799.0, "category": "Entertainment", "description": "Netflix 4K Subscription", "days_ago": 54},
            {"type": "Expense", "amount": 900.0, "category": "Entertainment", "description": "PVR Movie Tickets with Popcorn", "days_ago": 33},
            {"type": "Expense", "amount": 799.0, "category": "Entertainment", "description": "Netflix Monthly Plan", "days_ago": 23},
            {"type": "Expense", "amount": 149.0, "category": "Entertainment", "description": "Spotify Premium Monthly", "days_ago": 11},

            # Expense - Anomaly item (Unusual High Purchase)
            {"type": "Expense", "amount": 35000.0, "category": "Shopping", "description": "Apple iPad Air Tech Purchase (Unusual High Expense)", "days_ago": 16}
        ]

        today = datetime.date.today()
        inserted_count = 0
        for item in sample_txns:
            txn_date = (today - datetime.timedelta(days=item["days_ago"])).strftime("%Y-%m-%d")
            cat_id = category_map.get(item["category"], category_map.get("Other", "CAT-009"))
            self.add_transaction(
                user_id=user_id,
                category_id=cat_id,
                date=txn_date,
                amount=item["amount"],
                txn_type=item["type"],
                description=item["description"]
            )
            inserted_count += 1
            
        # Seed default budgets for user
        self.set_budget(user_id, category_map.get("Food", "CAT-001"), 8000.0)
        self.set_budget(user_id, category_map.get("Travel", "CAT-002"), 5000.0)
        self.set_budget(user_id, category_map.get("Bills", "CAT-003"), 15000.0)
        self.set_budget(user_id, category_map.get("Shopping", "CAT-004"), 10000.0)
        self.set_budget(user_id, category_map.get("Entertainment", "CAT-007"), 3000.0)

        return inserted_count

# Singleton instance
db = Database()
