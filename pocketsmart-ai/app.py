"""PocketSmart AI - Smart Budget & Recommendation Assistant (Streamlit + Gemini)."""
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import budget as b
from utils import gemini_client as ai

st.set_page_config(page_title="PocketSmart AI", page_icon="💰", layout="wide")

# ---------- State ----------
if "df" not in st.session_state:
    st.session_state.df = b.clean(pd.read_csv("data/sample_expenses.csv"))
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------- Sidebar ----------
with st.sidebar:
    st.title("💰 PocketSmart AI")
    api_key = st.text_input("Gemini API Key", type="password",
                            help="Or set GEMINI_API_KEY in .env") or None
    up = st.file_uploader("Upload your expenses CSV", type="csv")
    if up:
        st.session_state.df = b.clean(pd.read_csv(up))
        st.success("Data loaded")
    if st.button("Clear all data"):
        st.session_state.df = b.empty_df()
    st.caption("Columns: date, description, category, amount, type")

df = st.session_state.df
summary = b.summarize(df)

st.title("PocketSmart AI: Your Smart Budget & Recommendation Assistant")
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Add Transaction", "🤖 AI Advisor", "🎯 Goal Planner"])

# ---------- Dashboard ----------
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Income", f"₹{summary['income']:,.0f}")
    c2.metric("Expenses", f"₹{summary['expense']:,.0f}")
    c3.metric("Savings", f"₹{summary['savings']:,.0f}")
    c4.metric("Savings Rate", f"{summary['savings_rate']}%")

    if summary["by_category"]:
        left, right = st.columns(2)
        cat_df = pd.DataFrame(summary["by_category"].items(), columns=["Category", "Amount"])
        left.plotly_chart(px.pie(cat_df, names="Category", values="Amount", title="Spending by Category"),
                          width="stretch")
        right.plotly_chart(px.bar(cat_df, x="Category", y="Amount", title="Category Totals"),
                           width="stretch")

        r = b.rule_50_30_20(summary)
        st.subheader("50/30/20 Check")
        st.progress(min(max(r["needs_pct"] / 100, 0.0), 1.0), text=f"Needs {r['needs_pct']}% (target 50%)")
        st.progress(min(max(r["wants_pct"] / 100, 0.0), 1.0), text=f"Wants {r['wants_pct']}% (target 30%)")
        st.progress(min(max(r["savings_pct"] / 100, 0.0), 1.0), text=f"Savings {r['savings_pct']}% (target 20%)")
    else:
        st.info("No expenses yet. Add some in the next tab.")

    st.subheader("Transactions")
    st.dataframe(df.sort_values("date", ascending=False), width="stretch")

# ---------- Add Transaction ----------
with tab2:
    with st.form("add_form", clear_on_submit=True):
        d = st.date_input("Date", date.today())
        desc = st.text_input("Description (e.g. Zomato order)")
        amt = st.number_input("Amount", min_value=0.0, step=100.0)
        typ = st.radio("Type", ["expense", "income"], horizontal=True)
        cat = st.selectbox("Category", ["Auto (AI)"] + b.CATEGORIES + ["Income"])
        ok = st.form_submit_button("Add")
    if ok and desc and amt > 0:
        if cat == "Auto (AI)":
            with st.spinner("Categorizing with Gemini..."):
                cat = ai.auto_categorize(desc, b.CATEGORIES, api_key)
        st.session_state.df = b.add_entry(df, d, desc, cat, amt, typ)
        st.success(f"Added under **{cat}**")
        st.rerun()

# ---------- AI Advisor ----------
with tab3:
    st.caption("Ask anything about your budget.")
    for role, msg in st.session_state.chat:
        st.chat_message(role).write(msg)
    if q := st.chat_input("e.g. Where am I overspending?"):
        st.session_state.chat.append(("user", q))
        st.chat_message("user").write(q)
        try:
            with st.spinner("Thinking..."):
                ans = ai.get_advice(summary, q, api_key)
        except Exception as e:
            ans = f"⚠️ {e}"
        st.session_state.chat.append(("assistant", ans))
        st.chat_message("assistant").write(ans)

# ---------- Goal Planner ----------
with tab4:
    goal = st.text_input("Goal", "Buy a laptop")
    g1, g2 = st.columns(2)
    target = g1.number_input("Target amount (₹)", min_value=1000.0, value=60000.0, step=1000.0)
    months = g2.slider("Months", 1, 36, 6)
    if st.button("Get recommendations"):
        try:
            with st.spinner("Planning..."):
                st.markdown(ai.get_recommendations(summary, goal, target, months, api_key))
        except Exception as e:
            st.error(str(e))