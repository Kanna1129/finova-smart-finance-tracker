import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import db
from utils.ml import clean_transactions_df
from utils.styles import render_header, render_kpi_card

def render_dashboard_page(user_id: str):
    """Renders the main interactive analytics dashboard."""
    render_header("Financial Dashboard", "Real-time summary of your income, expenses, balance, and spending analytics.")

    raw_df = db.get_transactions(user_id)
    df = clean_transactions_df(raw_df)

    if df.empty:
        st.info("💡 **No transactions found yet!** Add your first entry in **Transactions**, or load sample data below to see the dashboard in action.")
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            if st.button("✨ Load Demo Data (~40 Sample Transactions)", type="primary", use_container_width=True, key="dash_load_demo"):
                with st.spinner("Generating sample transactions..."):
                    count = db.load_demo_data(user_id)
                    st.toast(f"Successfully loaded {count} sample transactions!", icon="🎉")
                    st.rerun()
        return

    # Calculate Summary KPIs
    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expense = df[df["type"] == "Expense"]["amount"].sum()
    net_balance = total_income - total_expense
    savings_rate = ((net_balance / total_income) * 100.0) if total_income > 0 else 0.0

    # KPI Metric Cards Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Total Income", total_income, "income", "📈")
    with c2:
        render_kpi_card("Total Expense", total_expense, "expense", "📉")
    with c3:
        render_kpi_card("Net Balance", net_balance, "balance" if net_balance >= 0 else "expense", "🏦")
    with c4:
        render_kpi_card("Savings Rate", savings_rate, "savings", "💡", is_percent=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Category Map lookup
    category_map = db.get_category_map()["id_to_name"]
    df["category_name"] = df["category_id"].map(category_map).fillna("Other")

    # Interactive Plotly Charts Row 1
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        with st.container(border=True):
            st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem;'>Category-wise Expense Breakdown</h3>", unsafe_allow_html=True)
            df_exp = df[df["type"] == "Expense"].copy()
            if not df_exp.empty:
                cat_summary = df_exp.groupby("category_name")["amount"].sum().reset_index()
                fig_pie = px.pie(
                    cat_summary,
                    values="amount",
                    names="category_name",
                    hole=0.45,
                    color_discrete_sequence=["#6D5CE8", "#22C7B8", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4", "#64748B"]
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
                fig_pie.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=320,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.write("No expense data recorded yet.")

    with col_chart2:
        with st.container(border=True):
            st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem;'>Monthly Income vs Expense</h3>", unsafe_allow_html=True)
            df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
            monthly_summary = df.groupby(["month", "type"])["amount"].sum().reset_index()

            if not monthly_summary.empty:
                fig_bar = px.bar(
                    monthly_summary,
                    x="month",
                    y="amount",
                    color="type",
                    barmode="group",
                    color_discrete_map={"Income": "#22C7B8", "Expense": "#EF4444"}
                )
                fig_bar.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=320,
                    xaxis_title="Month",
                    yaxis_title="Amount (₹)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="#E2E8F0")
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.write("No monthly data recorded yet.")

    # Spending Trend Line Chart
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem;'>Daily Spending Trend Over Time</h3>", unsafe_allow_html=True)
        df_exp_trend = df[df["type"] == "Expense"].copy()
        if not df_exp_trend.empty:
            daily_trend = df_exp_trend.groupby("date")["amount"].sum().reset_index()
            fig_line = px.line(
                daily_trend,
                x="date",
                y="amount",
                markers=True,
                color_discrete_sequence=["#6D5CE8", "#22C7B8", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4", "#64748B"]
            )
            fig_line.update_traces(line=dict(width=3), marker=dict(size=6, color="#6D5CE8"))
            fig_line.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=280,
                xaxis_title="Date",
                yaxis_title="Daily Expense (₹)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#E2E8F0")
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.write("No daily spending trend available.")

    # Last 5 Recent Transactions Table
    with st.container(border=True):
        st.markdown("<h3 style='font-size: 1.15rem; font-weight: 700; color: #1E293B; margin-bottom: 1rem;'>Recent 5 Transactions</h3>", unsafe_allow_html=True)
        recent_5 = df.sort_values(by="date", ascending=False).head(5).copy()

        display_df = recent_5[["date", "type", "category_name", "amount", "description"]].rename(
            columns={
                "date": "Date",
                "type": "Type",
                "category_name": "Category",
                "amount": "Amount (₹)",
                "description": "Description"
            }
        )
        display_df["Amount (₹)"] = display_df["Amount (₹)"].apply(lambda x: f"₹{x:,.2f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
