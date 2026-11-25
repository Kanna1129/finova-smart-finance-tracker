import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import db
from utils.ml import clean_transactions_df, SpendingPredictor, AnomalyDetector
from utils.gemini import generate_saving_tips
from utils.styles import render_header

def render_insights_page(user_id: str):
    """Renders Smart Insights Page (ML Spending Prediction, Anomaly Detection, Gemini Recommendations)."""
    render_header("Smart Insights & ML Analytics", "Machine Learning models forecast future spending, flag anomalies, and offer custom savings tips.")

    raw_txns = db.get_transactions(user_id)
    txns_df = clean_transactions_df(raw_txns)

    if txns_df.empty:
        st.info("💡 Please add transactions or click 'Load Demo Data' in Profile to generate ML insights.")
        return

    cat_map = db.get_category_map()["id_to_name"]
    txns_df["category_name"] = txns_df["category_id"].map(cat_map).fillna("Other")

    # 1. ML SPENDING PREDICTION
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B;'>🔮 Next-Month Spending Forecast (Linear Regression)</h3>", unsafe_allow_html=True)
        st.caption("Scikit-learn Linear Regression model fits on historical monthly expense totals.")

        prediction = SpendingPredictor.predict_next_month_spending(txns_df)

        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            st.metric("Predicted Next Month Expense", f"₹{prediction['predicted_amount']:,.2f}")
        with p_col2:
            st.metric("Historical Monthly Avg", f"₹{prediction['historical_avg']:,.2f}")
        with p_col3:
            st.metric("Trend Direction", f"{prediction['trend'].capitalize()} Trend")

        if "monthly_history" in prediction and not prediction["monthly_history"].empty:
            fig_pred = px.bar(
                prediction["monthly_history"],
                x="month",
                y="amount",
                title="Monthly Expense History Baseline",
                color_discrete_sequence=["#059669"]
            )
            fig_pred.update_layout(height=240, margin=dict(t=30, b=20, l=20, r=20))
            st.plotly_chart(fig_pred, use_container_width=True)

    # 2. ANOMALY DETECTION (ISOLATION FOREST)
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B;'>⚠️ Anomaly Detection (IsolationForest ML)</h3>", unsafe_allow_html=True)
        st.caption("Scikit-Learn IsolationForest algorithm identifies unusually high or outlier transactions.")

        anomalies_df = AnomalyDetector.detect_anomalies(txns_df, contamination=0.08)

        if not anomalies_df.empty and "is_anomaly" in anomalies_df.columns:
            flagged = anomalies_df[anomalies_df["is_anomaly"] == True].copy()
            if not flagged.empty:
                st.warning(f"Detected **{len(flagged)}** unusual transaction(s) that deviate significantly from typical spending patterns:")
                flagged_disp = flagged[["date", "category_name", "amount", "description"]].rename(
                    columns={
                        "date": "Date",
                        "category_name": "Category",
                        "amount": "Amount (₹)",
                        "description": "Description"
                    }
                )
                flagged_disp["Amount (₹)"] = flagged_disp["Amount (₹)"].apply(lambda x: f"₹{x:,.2f}")
                st.dataframe(flagged_disp, use_container_width=True, hide_index=True)
            else:
                st.success("✅ No spending anomalies detected. All transactions align with normal spending behavior.")
        else:
            st.info("Insufficient transactions to run IsolationForest anomaly detection.")

    # 3. GEMINI AI SAVING TIPS & RECOMMENDATIONS
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B;'>💡 Gemini AI Financial Recommendations & Saving Tips</h3>", unsafe_allow_html=True)

        summary_text = f"Total Income: ₹{txns_df[txns_df['type']=='Income']['amount'].sum():,.2f}, Total Expense: ₹{txns_df[txns_df['type']=='Expense']['amount'].sum():,.2f}"
        
        with st.spinner("Generating custom financial recommendations with Gemini..."):
            tips = generate_saving_tips(summary_text)

        for i, tip in enumerate(tips, 1):
            st.markdown(
                f"""
                <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 1rem 1.2rem; border-radius: 10px; margin-bottom: 0.8rem; border-left: 4px solid #0D9488;">
                    <strong>Tip #{i}:</strong> {tip}
                </div>
                """,
                unsafe_allow_html=True
            )
