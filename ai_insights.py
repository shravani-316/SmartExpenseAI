import pandas as pd
from finance import money, spending_insights, monthly_summary

def suggest_budget(tx, symbol="$"):
    if tx.empty or tx[tx["type"]=="Expense"].empty:
        return "Add some expense transactions first. Then Finwise can suggest category limits based on your actual recorded spending."
    exp=tx[tx["type"]=="Expense"].copy()
    exp["amount"]=pd.to_numeric(exp["amount"],errors="coerce").fillna(0)
    cats=exp.groupby("category")["amount"].sum().sort_values(ascending=False)
    total=float(cats.sum())
    lines=[f"Based on your entered expense history ({money(total,symbol)} total), here are starter monthly limits:"]
    for cat,val in cats.head(6).items():
        lines.append(f"• {cat}: {money(float(val)/max(1,exp['month'].nunique())*1.10,symbol)} (about 10% above your average recorded monthly spend)")
    lines.append("These are simple estimates from your data, not a guarantee or financial advice.")
    return "\n".join(lines)

def answer_finance_question(question, tx, profile, goals, bills, symbol="$"):
    q=(question or "").lower()
    if not q.strip(): return "Type a question first. Try asking about spending, savings, bills or budgets."
    if tx.empty:
        return "I don't have any transactions yet. Add income and expenses in Budgeting & Expenses, then ask me again."
    x=tx.copy()
    x["amount"]=pd.to_numeric(x["amount"],errors="coerce").fillna(0)
    if "month" not in x.columns:
        x["date"]=pd.to_datetime(x["date"],errors="coerce"); x["month"]=x["date"].dt.to_period("M").astype(str)
    month=pd.Timestamp.today().strftime("%Y-%m")
    current=x[x["month"]==month]
    exp=current[current["type"]=="Expense"]
    inc=current[current["type"]=="Income"]
    if any(k in q for k in ["breakdown","category","categories","where did","spending by"]):
        if exp.empty: return "No expenses recorded for the current month yet."
        cats=exp.groupby("category")["amount"].sum().sort_values(ascending=False)
        return "This month's recorded spending:\n"+"\n".join([f"• {c}: {money(v,symbol)}" for c,v in cats.items()])+f"\nTotal: {money(cats.sum(),symbol)}."
    if any(k in q for k in ["save money","save","saving","budget"]):
        return suggest_budget(x,symbol)
    if any(k in q for k in ["bill","due","payment"]):
        unpaid=[b for b in bills if not b.get("paid")]
        if not unpaid: return "You have no unpaid bills recorded."
        return "Your unpaid bills:\n"+"\n".join([f"• {b['name']}: {money(b['amount'],symbol)} due {b['due_date']}" for b in unpaid])
    if any(k in q for k in ["health","score"]):
        return "Your financial health score is an educational estimate shown on the Financial Health page. Add income, expenses, budgets and savings goals to make it more useful."
    if any(k in q for k in ["income","earned","salary"]):
        return f"Your recorded income this month is {money(inc['amount'].sum(),symbol)}."
    if any(k in q for k in ["spent","expense","spending","much"]):
        return f"Your recorded expenses this month total {money(exp['amount'].sum(),symbol)}. "+("Your recorded income is "+money(inc['amount'].sum(),symbol)+"." if not inc.empty else "No income is recorded this month.")
    return "I can help with spending breakdowns, income, bills, savings suggestions and budgets. Try: 'Show my spending breakdown for this month' or 'Where can I save money?'"

def categorize_transaction(merchant, note=""):
    text=(str(merchant)+" "+str(note)).lower()
    rules={"Food & Dining":["restaurant","cafe","coffee","grocery","food","pizza","swiggy","zomato"],
           "Transport":["uber","ola","fuel","petrol","bus","train","metro","taxi"],
           "Bills & Utilities":["electric","water bill","internet","wifi","phone bill","utility"],
           "Entertainment":["netflix","spotify","movie","cinema","game"],
           "Shopping":["amazon","flipkart","mall","clothing","shopping"]}
    for cat,words in rules.items():
        if any(w in text for w in words): return cat
    return "Other"
