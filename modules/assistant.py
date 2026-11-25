import datetime
import pandas as pd
import streamlit as st
from utils.db import db
from utils.ml import clean_transactions_df
from utils.gemini import ask_gemini_financial_question, parse_plain_language_transaction
from utils.styles import render_header

def build_financial_summary_context(user_id: str) -> str:
    """Constructs text summary of user financial data for Gemini context."""
    txns = clean_transactions_df(db.get_transactions(user_id))
    if txns.empty:
        return "No transactions recorded yet."

    cat_map = db.get_category_map()["id_to_name"]
    txns["category_name"] = txns["category_id"].map(cat_map).fillna("Other")

    total_income = txns[txns["type"] == "Income"]["amount"].sum()
    total_expense = txns[txns["type"] == "Expense"]["amount"].sum()
    net_balance = total_income - total_expense

    cat_breakdown = txns[txns["type"] == "Expense"].groupby("category_name")["amount"].sum().to_dict()
    cat_str = ", ".join([f"{k}: ₹{v:,.2f}" for k, v in cat_breakdown.items()])

    recent = txns.sort_values(by="date", ascending=False).head(5)
    recent_str = "; ".join([f"{r['date']} ({r['type']}): ₹{r['amount']} - {r['description']}" for _, r in recent.iterrows()])

    context = f"""
    - Total Income: ₹{total_income:,.2f}
    - Total Expense: ₹{total_expense:,.2f}
    - Net Balance: ₹{net_balance:,.2f}
    - Expense Breakdown by Category: {cat_str if cat_str else 'None'}
    - Recent 5 Transactions: {recent_str}
    """
    return context.strip()

def render_assistant_page(user_id: str):
    """Renders AI Assistant Page (Gemini Chat & Plain Language Transaction Entry)."""
    render_header("AI Financial Assistant (Google Gemini)", "Ask questions in natural language or quickly log transactions with plain text.")

    tab_chat, tab_natural_entry, tab_history = st.tabs(["💬 Ask Gemini AI", "🎙️ Plain-Language Txn Entry", "📜 Query History"])

    summary_context = build_financial_summary_context(user_id)

    # TAB 1: GEMINI Q&A CHAT
    with tab_chat:
        with st.container(border=True):
            st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B;'>Financial Question & Answer</h3>", unsafe_allow_html=True)
            st.caption("Example: 'How much did I spend on food this month?' or 'How can I save ₹5000 next month?'")

            user_query = st.text_input("Ask a question about your finances:", key="gemini_query_input")
            if st.button("Send to Gemini AI", use_container_width=True, type="primary"):
                if not user_query.strip():
                    st.error("Please enter a question.")
                else:
                    with st.spinner("Analyzing your financial data with Gemini AI..."):
                        answer = ask_gemini_financial_question(summary_context, user_query)
                        db.save_ai_query(user_id, user_query, answer)
                        
                        st.markdown("#### 🤖 Gemini Response:")
                        st.success(answer)

    # TAB 2: PLAIN LANGUAGE TXN ENTRY
    with tab_natural_entry:
        with st.container(border=True):
            st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B;'>Natural Language Transaction Logger</h3>", unsafe_allow_html=True)
            st.caption("Type in natural language, e.g., 'spent 250 on lunch yesterday' or 'earned 5000 from freelance project today'.")

            prompt_input = st.text_input("Enter transaction phrase:", placeholder="spent 250 on lunch yesterday")
            
            if st.button("Parse with Gemini AI", use_container_width=True):
                if not prompt_input.strip():
                    st.error("Please enter a phrase.")
                else:
                    with st.spinner("Parsing transaction details..."):
                        parsed_data = parse_plain_language_transaction(prompt_input)
                        st.session_state["parsed_txn"] = parsed_data

            if "parsed_txn" in st.session_state and st.session_state["parsed_txn"]:
                parsed = st.session_state["parsed_txn"]
                st.markdown("---")
                st.markdown("#### 📋 Extracted Transaction Details (Please Confirm):")
                
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Amount", f"₹{parsed.get('amount', 0.0):,.2f}")
                with c2:
                    st.metric("Type", parsed.get('type', 'Expense'))
                with c3:
                    st.metric("Category", parsed.get('category', 'Other'))
                with c4:
                    st.metric("Date", parsed.get('date', datetime.date.today().strftime('%Y-%m-%d')))
                
                st.caption(f"Description: **{parsed.get('description', '')}**")

                cat_name_map = db.get_category_map()["name_to_id"]

                if st.button("✅ Confirm & Save Transaction to Database", type="primary", use_container_width=True):
                    cat_id = cat_name_map.get(parsed.get('category'), "CAT-009")
                    db.add_transaction(
                        user_id=user_id,
                        category_id=cat_id,
                        date=parsed.get('date'),
                        amount=parsed.get('amount'),
                        txn_type=parsed.get('type'),
                        description=parsed.get('description')
                    )
                    st.toast("Transaction parsed and saved!", icon="🎉")
                    del st.session_state["parsed_txn"]
                    st.rerun()

    # TAB 3: QUERY HISTORY
    with tab_history:
        with st.container(border=True):
            st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B;'>Saved AI Query Log</h3>", unsafe_allow_html=True)
            queries_df = db.get_ai_queries(user_id)
            if queries_df.empty:
                st.info("No AI questions asked yet.")
            else:
                queries_df = queries_df.sort_values(by="timestamp", ascending=False).reset_index(drop=True)
                for _, row in queries_df.iterrows():
                    with st.expander(f"❓ {row['question']} ({row['timestamp']})"):
                        st.write(row['response'])
