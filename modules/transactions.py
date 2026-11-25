import datetime
import pandas as pd
import streamlit as st
from utils.db import db
from utils.ml import ml_classifier, clean_transactions_df
from utils.styles import render_header

def render_transactions_page(user_id: str):
    """Renders Transaction Management (Add, Filter, Search, Edit, Delete, Export CSV)."""
    render_header("Transaction Management", "Log new entries, search, filter, edit, or export your financial records.")

    cat_map = db.get_category_map()
    id_to_name = cat_map["id_to_name"]
    name_to_id = cat_map["name_to_id"]

    tab_add, tab_view = st.tabs(["➕ Add New Transaction", "📋 All Transactions & Filters"])

    # TAB 1: ADD TRANSACTION
    with tab_add:
        with st.container(border=True):
            st.markdown("<h3 style='font-size: 1.2rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem;'>Add Income or Expense Entry</h3>", unsafe_allow_html=True)

            with st.form("add_txn_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    txn_type = st.selectbox("Transaction Type", ["Expense", "Income"])
                    amount = st.number_input("Amount (₹)", min_value=1.0, value=250.0, step=10.0)
                    txn_date = st.date_input("Date", datetime.date.today())

                with c2:
                    cat_options = ["Auto (ML Predict)"] + list(name_to_id.keys())
                    selected_cat_name = st.selectbox("Category", cat_options)
                    description = st.text_input("Description", placeholder="e.g. Swiggy dinner order, Metro recharge...")

                submitted = st.form_submit_button("Save Transaction Entry ➔", use_container_width=True, type="primary")

                if submitted:
                    if not description.strip():
                        st.error("Please enter a description.")
                    else:
                        # ML Auto-Categorization logic
                        final_cat_name = selected_cat_name
                        if selected_cat_name == "Auto (ML Predict)":
                            final_cat_name = ml_classifier.predict_category(description)
                            st.info(f"🤖 **Scikit-Learn Model Auto-Predicted Category:** `{final_cat_name}`")

                        cat_id = name_to_id.get(final_cat_name, name_to_id.get("Other", "CAT-009"))
                        db.add_transaction(
                            user_id=user_id,
                            category_id=cat_id,
                            date=txn_date.strftime("%Y-%m-%d"),
                            amount=amount,
                            txn_type=txn_type,
                            description=description
                        )
                        st.toast("Transaction added successfully!", icon="✅")
                        st.rerun()

    # TAB 2: VIEW & FILTER TRANSACTIONS
    with tab_view:
        raw_df = db.get_transactions(user_id)
        df = clean_transactions_df(raw_df)

        if df.empty:
            st.info("No transactions found.")
            return

        df["category_name"] = df["category_id"].map(id_to_name).fillna("Other")

        with st.container(border=True):
            st.markdown("<h3 style='font-size: 1.2rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem;'>Filter & Search Records</h3>", unsafe_allow_html=True)

            f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1, 1, 1])
            with f_col1:
                search_query = st.text_input("🔍 Search Description", placeholder="e.g. Swiggy, Salary...")
            with f_col2:
                type_filter = st.selectbox("Type Filter", ["All", "Income", "Expense"])
            with f_col3:
                cat_filter = st.selectbox("Category Filter", ["All"] + list(name_to_id.keys()))
            with f_col4:
                date_range = st.date_input("Date Range", [datetime.date.today() - datetime.timedelta(days=90), datetime.date.today()])

            # Apply Filters
            filtered_df = df.copy()

            if search_query.strip():
                filtered_df = filtered_df[filtered_df["description"].str.contains(search_query.strip(), case=False, na=False)]

            if type_filter != "All":
                filtered_df = filtered_df[filtered_df["type"] == type_filter]

            if cat_filter != "All":
                filtered_df = filtered_df[filtered_df["category_name"] == cat_filter]

            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                start_d, end_d = date_range[0].strftime("%Y-%m-%d"), date_range[1].strftime("%Y-%m-%d")
                filtered_df = filtered_df[(filtered_df["date"] >= start_d) & (filtered_df["date"] <= end_d)]

            # Sort descending by date
            filtered_df = filtered_df.sort_values(by="date", ascending=False).reset_index(drop=True)

            st.markdown(f"**Showing `{len(filtered_df)}` of `{len(df)}` transactions**")

            display_cols = ["date", "type", "category_name", "amount", "description"]
            display_df = filtered_df[display_cols].rename(
                columns={
                    "date": "Date",
                    "type": "Type",
                    "category_name": "Category",
                    "amount": "Amount (₹)",
                    "description": "Description"
                }
            )

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Download CSV Button
            csv_data = filtered_df[["txn_id", "date", "type", "category_name", "amount", "description"]].to_csv(index=False)
            st.download_button(
                label="📥 Export Filtered Transactions to CSV",
                data=csv_data,
                file_name=f"finova_transactions_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.markdown("---")

            # Edit & Delete Section
            st.markdown("<h4 style='font-size: 1.1rem; font-weight: 700; color: #1E293B;'>⚙️ Manage Selected Transaction (Edit / Delete)</h4>", unsafe_allow_html=True)
            if not filtered_df.empty:
                txn_choices = {
                    f"{row['date']} | {row['type']} | ₹{row['amount']} | {row['description'][:25]} (ID: {row['txn_id']})": row['txn_id']
                    for _, row in filtered_df.iterrows()
                }
                selected_label = st.selectbox("Select Transaction to Modify", list(txn_choices.keys()))
                selected_id = txn_choices[selected_label]
                target_row = filtered_df[filtered_df["txn_id"] == selected_id].iloc[0]

                col_edit, col_del = st.columns([3, 1])

                with col_edit:
                    with st.expander("✏️ Edit Transaction Details"):
                        with st.form(f"edit_form_{selected_id}"):
                            e_type = st.selectbox("Type", ["Expense", "Income"], index=0 if target_row["type"] == "Expense" else 1)
                            e_amount = st.number_input("Amount (₹)", min_value=0.0, value=float(target_row["amount"]))
                            e_cat_idx = list(name_to_id.keys()).index(target_row["category_name"]) if target_row["category_name"] in name_to_id else 0
                            e_cat_name = st.selectbox("Category", list(name_to_id.keys()), index=e_cat_idx)
                            e_date = st.date_input("Date", datetime.datetime.strptime(target_row["date"], "%Y-%m-%d").date())
                            e_desc = st.text_input("Description", value=str(target_row["description"]))

                            save_edit = st.form_submit_button("Update Transaction")
                            if save_edit:
                                cat_id = name_to_id.get(e_cat_name, "CAT-009")
                                db.update_transaction(selected_id, cat_id, e_date.strftime("%Y-%m-%d"), e_amount, e_type, e_desc)
                                st.toast("Transaction updated!", icon="✏️")
                                st.rerun()

                with col_del:
                    if st.button("🗑️ Delete Entry", type="primary"):
                        db.delete_transaction(selected_id)
                        st.toast("Transaction deleted!", icon="🗑️")
                        st.rerun()
