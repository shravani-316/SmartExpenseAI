import json, uuid
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
def _path(kind, email):
    import hashlib
    key=hashlib.sha256(email.lower().encode()).hexdigest()[:24]
    DATA_DIR.mkdir(exist_ok=True)
    return DATA_DIR / f"{kind}_{key}.json"
def _read(kind,email,default):
    p=_path(kind,email)
    if not p.exists(): return default
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return default
def _write(kind,email,data):
    _path(kind,email).write_text(json.dumps(data,indent=2,ensure_ascii=False,default=str),encoding="utf-8")
def money(value,symbol="$"):
    return f"{symbol}{float(value):,.2f}"
def load_transactions(email):
    rows=_read("transactions",email,[])
    return pd.DataFrame(rows,columns=["id","date","type","category","merchant","amount","note"])
def save_transaction(email,row):
    rows=_read("transactions",email,[])
    row=dict(row); row["id"]=row.get("id") or uuid.uuid4().hex[:10]
    rows.append(row); _write("transactions",email,rows)
def delete_transaction(email,ident):
    rows=[r for r in _read("transactions",email,[]) if r.get("id")!=ident]; _write("transactions",email,rows)
def load_bills(email): return _read("bills",email,[])
def save_bill(email,row):
    rows=_read("bills",email,[])
    if not row.get("id"): row["id"]=uuid.uuid4().hex[:10]
    rows=[r for r in rows if r.get("id")!=row["id"]]; rows.append(row); _write("bills",email,rows)
def delete_bill(email,ident): _write("bills",email,[r for r in load_bills(email) if r.get("id")!=ident])
def load_goals(email): return _read("goals",email,[])
def save_goal(email,row):
    rows=load_goals(email)
    if not row.get("id"): row["id"]=uuid.uuid4().hex[:10]
    rows=[r for r in rows if r.get("id")!=row["id"]]; rows.append(row); _write("goals",email,rows)
def delete_goal(email,ident): _write("goals",email,[r for r in load_goals(email) if r.get("id")!=ident])
def load_profile(email):
    return _read("profile",email,{"currency":"USD","budgets":{},"monthly_income":0})
def save_profile(email,profile): _write("profile",email,profile)
def financial_health_score(tx,profile,goals):
    score=50
    if not tx.empty:
        income=tx.loc[tx["type"]=="Income","amount"].sum()
        expense=tx.loc[tx["type"]=="Expense","amount"].sum()
        if income>0:
            rate=(income-expense)/income
            score += max(-20,min(25,int(rate*50)))
        score += min(10, len(tx)//3)
        budgets=profile.get("budgets",{})
        if budgets:
            score += 5
            if all(float(budgets.get(c,0))==0 or float(budgets.get(c,0))>0 for c in budgets): score+=2
    if goals:
        progress=sum(min(1,float(g.get("current",0))/max(float(g.get("target",1)),1)) for g in goals)/len(goals)
        score += int(progress*10)
    return max(0,min(100,score))
def spending_insights(tx,symbol="$"):
    if tx.empty: return ["Add a few transactions to unlock personalized spending insights."]
    expenses=tx[tx["type"]=="Expense"]
    if expenses.empty: return ["No expenses recorded yet. Add expense records to understand spending."]
    out=[]
    cats=expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
    out.append(f"Your highest recorded spending category is {cats.index[0]} ({money(cats.iloc[0],symbol)}).")
    income=tx[tx["type"]=="Income"]["amount"].sum()
    spend=expenses["amount"].sum()
    if income>0:
        rate=(income-spend)/income*100
        out.append(f"Your recorded savings rate is {rate:.1f}% across all entered transactions.")
        if rate<10: out.append("Try reviewing recurring subscriptions and flexible purchases to find room to save.")
        else: out.append("Keep reviewing your budget regularly to protect your savings progress.")
    else: out.append("Add income records to estimate a savings rate.")
    if len(expenses)>1:
        out.append(f"You have {len(expenses)} expense records. Consistent tracking improves the usefulness of reports.")
    return out
def monthly_summary(tx, month):
    if tx.empty: return {"income":0,"expenses":0}
    x=tx.copy(); x["date"]=pd.to_datetime(x["date"],errors="coerce")
    x=x[x["date"].dt.strftime("%Y-%m")==month]
    return {"income":float(x.loc[x["type"]=="Income","amount"].sum()),"expenses":float(x.loc[x["type"]=="Expense","amount"].sum())}
def budget_status(month_tx,budgets):
    if month_tx.empty: spent={}
    else: spent=month_tx.groupby("category")["amount"].sum().to_dict()
    result=[]
    for cat, budget in budgets.items():
        budget=float(budget or 0)
        if budget<=0: continue
        amount=float(spent.get(cat,0))
        result.append({"category":cat,"spent":amount,"budget":budget,"percent":amount/budget*100})
    return result
