# Personal Expense Tracker (Streamlit + SQLite)
# Run with: streamlit run app.py

import sqlite3
from contextlib import closing
from datetime import date, datetime
import pandas as pd
import streamlit as st

DB_PATH = "expenses.db"

# ---------- DB Utilities ----------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL,
                payment_method TEXT
            );
        """)
        conn.commit()

def add_expense(tx_date:str, category:str, description:str, amount:float, payment_method:str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO expenses (tx_date, category, description, amount, payment_method) VALUES (?, ?, ?, ?, ?);",
            (tx_date, category, description, amount, payment_method),
        )
        conn.commit()

def fetch_expenses(start_date=None, end_date=None, category=None):
    query = "SELECT id, tx_date, category, description, amount, payment_method FROM expenses WHERE 1=1"
    params = []
    if start_date:
        query += " AND date(tx_date) >= date(?)"
        params.append(start_date)
    if end_date:
        query += " AND date(tx_date) <= date(?)"
        params.append(end_date)
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY date(tx_date) DESC, id DESC"
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn, params=params)
    return df

def delete_expense(expense_id:int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?;", (expense_id,))
        conn.commit()

def update_expense(expense_id:int, tx_date:str, category:str, description:str, amount:float, payment_method:str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """UPDATE expenses 
               SET tx_date=?, category=?, description=?, amount=?, payment_method=?
               WHERE id=?;""",
            (tx_date, category, description, amount, payment_method, expense_id),
        )
        conn.commit()

# ---------- App UI ----------
st.set_page_config(page_title="Personal Expense Tracker", page_icon="💸", layout="wide")

st.title("💸 Personal Expense Tracker")

# Ensure DB exists
init_db()

# Sidebar - Add new expense
st.sidebar.header("➕ Add Expense")
with st.sidebar.form("add_expense_form", clear_on_submit=True):
    today = date.today()
    tx_date = st.date_input("Date", value=today, format="YYYY-MM-DD")
    category = st.selectbox(
        "Category",
        ["Food", "Transport", "Rent", "Utilities", "Shopping", "Health", "Education", "Entertainment", "Other"],
        index=0,
    )
    description = st.text_input("Description (optional)")
    amount = st.number_input("Amount", min_value=0.0, step=10.0, format="%.2f")
    payment_method = st.selectbox("Payment Method", ["Cash", "UPI", "Card", "NetBanking", "Other"], index=1)
    submitted = st.form_submit_button("Add")
    if submitted:
        if amount <= 0:
            st.warning("Amount must be greater than 0.")
        else:
            add_expense(tx_date.isoformat(), category, description.strip(), float(amount), payment_method)
            st.success("Expense added!")

# Filters
st.subheader("🔎 Filter")
col1, col2, col3 = st.columns(3)
with col1:
    start_date = st.date_input("Start date", value=None, format="YYYY-MM-DD")
with col2:
    end_date = st.date_input("End date", value=None, format="YYYY-MM-DD")
with col3:
    filter_category = st.selectbox("Category filter", ["All", "Food", "Transport", "Rent", "Utilities", "Shopping", "Health", "Education", "Entertainment", "Other"], index=0)

start_str = start_date.isoformat() if isinstance(start_date, date) else None
end_str = end_date.isoformat() if isinstance(end_date, date) else None

df = fetch_expenses(start_str, end_str, filter_category)

# Summary KPIs
st.subheader("📊 Summary")
if df.empty:
    st.info("No expenses found. Add some using the sidebar.")
else:
    df['tx_date'] = pd.to_datetime(df['tx_date'])
    total_spend = df['amount'].sum()
    by_category = df.groupby('category', as_index=False)['amount'].sum().sort_values('amount', ascending=False)
    by_month = df.set_index('tx_date').resample('MS')['amount'].sum().reset_index()

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Spend", f"₹{total_spend:,.2f}")
    k2.metric("Transactions", f"{len(df):,}")
    k3.metric("Top Category", by_category.iloc[0]['category'] if not by_category.empty else "—")

    st.write("**Spend by Category**")
    st.bar_chart(by_category.set_index('category'))

    st.write("**Monthly Trend**")
    if not by_month.empty:
        by_month = by_month.rename(columns={"tx_date":"Month", "amount":"Spend"})
        by_month = by_month.set_index('Month')
        st.line_chart(by_month)
    else:
        st.caption("No monthly data yet.")

# Detailed table with edit/delete
st.subheader("📋 All Expenses")
if df.empty:
    st.caption("Nothing to show yet.")
else:
    # Display table
    st.dataframe(df, use_container_width=True)

    # Edit/Delete controls
    st.write("### ✏️ Edit / 🗑️ Delete")
    with st.expander("Edit an expense"):
        ids = df['id'].tolist()
        if ids:
            selected_id = st.selectbox("Select ID to edit", ids)
            row = df[df['id'] == selected_id].iloc[0]

            e_col1, e_col2 = st.columns(2)
            with e_col1:
                new_date = st.date_input("Date", value=row['tx_date'].date())
                new_category = st.selectbox("Category", ["Food", "Transport", "Rent", "Utilities", "Shopping", "Health", "Education", "Entertainment", "Other"], index= ["Food","Transport","Rent","Utilities","Shopping","Health","Education","Entertainment","Other"].index(row['category']) if row['category'] in ["Food","Transport","Rent","Utilities","Shopping","Health","Education","Entertainment","Other"] else 0 )
                new_amount = st.number_input("Amount", min_value=0.0, value=float(row['amount']), step=10.0, format="%.2f")
            with e_col2:
                new_desc = st.text_input("Description", value=row['description'] or "")
                new_method = st.selectbox("Payment Method", ["Cash", "UPI", "Card", "NetBanking", "Other"], index= ["Cash","UPI","Card","NetBanking","Other"].index(row['payment_method']) if row['payment_method'] in ["Cash","UPI","Card","NetBanking","Other"] else 0 )

            if st.button("Update"):
                update_expense(int(selected_id), new_date.isoformat(), new_category, new_desc, float(new_amount), new_method)
                st.success("Expense updated. Refresh data from filters above to see changes.")

    with st.expander("Delete an expense"):
        ids = df['id'].tolist()
        if ids:
            del_id = st.selectbox("Select ID to delete", ids, key="delete_id")
            if st.button("Delete", type="primary"):
                delete_expense(int(del_id))
                st.success("Expense deleted. Refresh data from filters above to see changes.")
