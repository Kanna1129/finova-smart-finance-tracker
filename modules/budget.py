import datetime
import pandas as pd
import streamlit as st
from utils.db import db
from utils.ml import clean_transactions_df
from utils.styles import render_header

def render_budget_page(user_id: str):
    """Renders Category Budget Management & Spending Alerts."""
    render_header("Budget Management & Alerts", "Set monthly spending caps per category and track progress alerts.")

    cat_map = db.get_category_map()
    id_to_name = cat_map["id_to_name"]
    name_to_id = cat_map["name_to_id"]

    budgets_df = db.get_budgets(user_id)
    raw_txns = db.get_transactions(user_id)
    txns_df = clean_transactions_df(raw_txns)

    # Current month filtering
    current_month_str = datetime.date.today().strftime("%Y-%m")

    if not txns_df.empty:
        txns_df["month"] = pd.to_datetime(txns_df["date"]).dt.to_period("M").astype(str)
        curr_exp = txns_df[(txns_df["month"] == current_month_str) & (txns_df["type"] == "Expense")].copy()
    else:
        curr_exp = pd.DataFrame()

    c1, c2 = st.columns([1, 1.8])

    # Left Column: Set Monthly Budget Form
    with c1:
        with st.container(border=True):
            st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem;'>Set Monthly Category Cap</h3>", unsafe_allow_html=True)

            expense_cats = [c for c in name_to_id.keys() if c != "Salary"]

            with st.form("set_budget_form", clear_on_submit=True):
                selected_cat = st.selectbox("Category", expense_cats)
                
                existing_limit = 5000.0
                if not budgets_df.empty:
                    cat_id = name_to_id.get(selected_cat)
                    match = budgets_df[budgets_df["category_id"].astype(str) == str(cat_id)]
                    if not match.empty:
                        existing_limit = float(match.iloc[0]["monthly_limit"])

                limit_amt = st.number_input("Monthly Limit (₹)", min_value=100.0, value=existing_limit, step=500.0)
                submitted = st.form_submit_button("Save Budget Limit", use_container_width=True)

                if submitted:
                    cat_id = name_to_id.get(selected_cat)
                    db.set_budget(user_id, cat_id, limit_amt)
                    st.toast(f"Budget for {selected_cat} set to ₹{limit_amt:,.2f}!", icon="🎯")
                    st.rerun()

    # Right Column: Budget Progress Bars & Warnings
    with c2:
        with st.container(border=True):
            st.markdown(f"<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem;'>Current Month Progress ({current_month_str})</h3>", unsafe_allow_html=True)

            if budgets_df.empty:
                st.info("No budget caps defined yet. Set category limits using the form on the left.")
            else:
                spent_map = {}
                if not curr_exp.empty:
                    spent_grp = curr_exp.groupby("category_id")["amount"].sum().to_dict()
                    spent_map = {str(k): float(v) for k, v in spent_grp.items()}

                for _, b_row in budgets_df.iterrows():
                    cat_id = str(b_row["category_id"])
                    cat_name = id_to_name.get(cat_id, "Other")
                    limit = float(b_row["monthly_limit"])
                    if limit <= 0:
                        continue

                    spent = spent_map.get(cat_id, 0.0)
                    pct = min(100.0, (spent / limit) * 100.0)

                    col_label, col_val = st.columns([2, 1])
                    with col_label:
                        st.write(f"**{cat_name}**")
                    with col_val:
                        st.write(f"₹{spent:,.0f} / ₹{limit:,.0f}")

                    progress_val = min(1.0, spent / limit)
                    st.progress(progress_val)

                    if spent >= limit:
                        st.markdown(
                            f"""
                            <div class="budget-exceeded">
                                🚨 <strong>Over Budget Warning:</strong> You have exceeded your {cat_name} budget by ₹{spent - limit:,.2f}! ({pct:.1f}%)
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    elif spent >= 0.8 * limit:
                        st.markdown(
                            f"""
                            <div class="budget-warning">
                                ⚠️ <strong>Caution Alert:</strong> You have reached {pct:.1f}% of your monthly {cat_name} limit!
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
