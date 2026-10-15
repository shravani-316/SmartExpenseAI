# Finwise AI — Smart Expense Tracker with AI Insights

A local, beginner-friendly Python + Streamlit college project inspired by the supplied dashboard reference.

## Features
- Sign up, sign in and log out (passwords stored as salted PBKDF2 hashes).
- Personal dashboard with balance, income, expenses, savings, category breakdown and recent transactions.
- Add/delete/filter/search/export income and expense transactions.
- Monthly category budgets with progress and overspending warnings.
- Savings goals with progress updates.
- Bills and payments with due dates, overdue status and mark-as-paid.
- Local rule-based finance assistant that answers questions using entered data.
- Financial health estimate and spending insights.
- Reports and analytics charts; CSV export.
- Settings for display name, currency and expected monthly income.
- Help page; local data storage per account; no paid API keys required.

## Requirements
- Windows 10/11
- Python 3.10 or newer
- Internet is only needed once to install Python packages. App features themselves do not need an AI API.

## Run on Windows
1. Extract the ZIP.
2. Open the extracted `SmartExpenseAI` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Run these commands one at a time:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt terminal and run:
```bat
.venv\Scripts\activate.bat
```
Then continue with `pip install -r requirements.txt` and `streamlit run app.py`.

5. The browser opens to the login page. Choose **Create account**, register, then sign in.
6. Add sample transactions through **Budgeting & Expenses** to populate the dashboard and reports.

## Important notes
- This project is a functional local finance tracker for educational use. It does **not** connect to a real bank, make transfers, or pay bills.
- “AI insights” are transparent local rule-based insights, not a large language model and not professional financial advice.
- Accounts and finance records are stored in local JSON files in `data/`. Do not use real sensitive financial information.
- Use demo data for college presentations. Delete generated JSON files in `data/` if you want to reset all local accounts and records.

## Demo data for a presentation
Create a fresh account and add a few transactions:
- Income / Salary / "Part-time job" / 1800
- Expense / Food & Dining / "Cafe" / 22
- Expense / Transport / "Uber" / 14
- Expense / Bills & Utilities / "Internet bill" / 45
- Expense / Entertainment / "Netflix" / 10
- Income / Freelance / "Design work" / 250
Create an emergency fund goal and add a couple of upcoming bills.

## Viva explanation
**Problem:** People can lose track of everyday expenses, bills and savings goals.
**Solution:** Finwise records manually entered transactions and presents them as dashboards, budgets, reports and local finance insights.
**Tech stack:** Python, Streamlit, pandas, Plotly, JSON file storage, password hashing.
**AI part:** A rule-based assistant reads the user's own records to answer common finance questions and gives simple budget estimates. It is not a paid API or a trained ML model.
**Limitations:** No bank integration, no real payments, local single-machine storage, educational health score.
