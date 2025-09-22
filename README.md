# Personal Expense Tracker (Streamlit + SQLite)

A simple, beginner-friendly personal expense tracker built with **Python**, **Streamlit**, and **SQLite**.

## Features
- Add expenses with date, category, description, amount, and payment method
- Filter by date range and category
- Summary KPIs, spend-by-category bar chart, and monthly trend line chart
- View, edit, and delete transactions
- Local SQLite database (no external setup)

## How to Run
1. Create a virtual environment (optional but recommended)
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   streamlit run app.py
   ```

Your data will be stored in `expenses.db` in the same folder.

## Notes
- This is a single-file app (`app.py`) to keep things simple for a fresher project.
- You can customize categories, payment methods, and UI text in the code.
