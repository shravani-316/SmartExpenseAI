import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
from pathlib import Path
from auth import init_auth, register_user, login_user, logout_user, current_user
from finance import (
    load_transactions, save_transaction, delete_transaction, load_bills, save_bill,
    delete_bill, load_goals, save_goal, delete_goal, load_profile, save_profile,
    money, financial_health_score, spending_insights, monthly_summary, budget_status
)
from ai_insights import answer_finance_question, suggest_budget, categorize_transaction

st.set_page_config(page_title="Finwise AI | Smart Expense Tracker", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background: #0b1020; color: #eef0fa; }
[data-testid="stSidebar"] { background: #0d1427; border-right: 1px solid #202a43; }
[data-testid="stSidebar"] * { color: #d4d9e8; }
h1,h2,h3 { color: #f6f6ff; letter-spacing: -0.03em; }
div[data-testid="stMetric"] { background: linear-gradient(135deg,#151d32,#11182b); border: 1px solid #26304a; padding: 17px; border-radius: 18px; }
div[data-testid="stMetricLabel"] { color: #9ca8c2; }
div[data-testid="stMetricValue"] { color: #f7f7ff; }
.stButton>button { border-radius: 12px; border: 1px solid #394361; background: #1a2340; color: #f4f2ff; font-weight: 600; min-height: 2.5rem; }
.stButton>button:hover { border-color: #b99aff; color: white; background: #28244c; }
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] { background: #151d32; color: #f4f5ff; border-radius: 10px; }
div[data-testid="stForm"] { background: #11192d; border: 1px solid #26304a; padding: 18px; border-radius: 18px; }
.fin-card { background: linear-gradient(135deg,#151d32,#11182b); border:1px solid #26304a; border-radius:20px; padding:20px; min-height:120px; }
.muted { color:#98a4bf; font-size:0.9rem; }
.purple { color:#bb9cff; }
div[data-testid="stProgressBar"] > div > div { background: linear-gradient(90deg,#8a5cf6,#d18cff); }
</style>
""", unsafe_allow_html=True)

init_auth()

def title_block(eyebrow, title, subtitle=""):
    st.caption(eyebrow.upper())
    st.title(title)
    if subtitle: st.markdown(f"<div class='muted'>{subtitle}</div>", unsafe_allow_html=True)

def show_login():
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown("<div style='padding:30px 10px 10px 5px'>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size:3.2rem;line-height:1.05'>✦ Finwise<span style='color:#b99aff'> AI</span></h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='font-size:2rem'>Your money.<br>Made clearer.</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#aab4cc;font-size:1.05rem'>Track spending, plan budgets, manage bills and turn everyday transactions into useful financial insights.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("### What you can do")
        st.markdown("✦  Track income and expenses  \n✦  Set budgets and savings goals  \n✦  See spending charts and a financial health score  \n✦  Ask the built-in finance assistant")
        st.info("Demo-friendly: create your own account. Data is stored locally in this project folder.")
    with right:
        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign in", "Create account"])
        with tab1:
            with st.form("login_form"):
                st.subheader("Welcome back")
                email = st.text_input("Email", key="login_email").strip().lower()
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Sign in", use_container_width=True)
            if submitted:
                ok, msg = login_user(email, password)
                if ok:
                    st.session_state["user_email"] = email
                    st.rerun()
                else: st.error(msg)
        with tab2:
            with st.form("register_form"):
                st.subheader("Create your Finwise account")
                name = st.text_input("Full name")
                email2 = st.text_input("Email address").strip().lower()
                password2 = st.text_input("Password (at least 8 characters)", type="password")
                password3 = st.text_input("Confirm password", type="password")
                submitted2 = st.form_submit_button("Create account", use_container_width=True)
            if submitted2:
                if password2 != password3: st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(name, email2, password2)
                    if ok:
                        st.success("Account created. Please sign in.")
                    else: st.error(msg)

if not st.session_state.get("user_email"):
    show_login()
    st.stop()

user_email = st.session_state["user_email"]
user = current_user(user_email)
if not user:
    st.session_state.pop("user_email", None)
    st.rerun()

transactions = load_transactions(user_email)
bills = load_bills(user_email)
goals = load_goals(user_email)
profile = load_profile(user_email)
currency = profile.get("currency", "USD")
symbol = {"USD":"$", "INR":"₹", "GBP":"£", "EUR":"€", "CAD":"CA$", "AUD":"A$"}.get(currency, "$")

def fmt(value):
    return money(value, symbol)

with st.sidebar:
    st.markdown(f"<h2 style='margin-bottom:0'>✦ <span style='color:#b99aff'>Finwise</span>.</h2>", unsafe_allow_html=True)
    st.caption("SMART MONEY WORKSPACE")
    st.markdown(f"**{user.get('name','User')}**")
    st.caption(user_email)
    st.divider()
    page = st.radio("NAVIGATION", ["Dashboard", "Budgeting & Expenses", "Savings & Goals", "Bills & Payments", "Transactions", "AI Assistant", "Financial Health", "Reports & Analytics", "Settings", "Help & Support"], label_visibility="visible")
    st.divider()
    st.caption("Your data stays in local project files.")
    if st.button("↪ Log out", use_container_width=True):
        logout_user()
        st.rerun()

today = date.today()
tx = transactions.copy()
if not tx.empty:
    tx["date"] = pd.to_datetime(tx["date"], errors="coerce")
    tx["amount"] = pd.to_numeric(tx["amount"], errors="coerce").fillna(0)
    tx["month"] = tx["date"].dt.to_period("M").astype(str)
else:
    tx = pd.DataFrame(columns=["id","date","type","category","merchant","amount","note","month"])

if page == "Dashboard":
    title_block("FINWISE / OVERVIEW", f"Hey {user.get('name','there').split()[0]}!", "Your personal finance overview at a glance.")
    month = today.strftime("%Y-%m")
    this_month = tx[tx["month"] == month] if not tx.empty else tx
    income = this_month.loc[this_month["type"]=="Income","amount"].sum() if not this_month.empty else 0
    expenses = this_month.loc[this_month["type"]=="Expense","amount"].sum() if not this_month.empty else 0
    total_balance = (tx.loc[tx["type"]=="Income","amount"].sum() - tx.loc[tx["type"]=="Expense","amount"].sum()) if not tx.empty else 0
    savings = income-expenses
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Available balance", fmt(total_balance))
    c2.metric("Income this month", fmt(income))
    c3.metric("Spending this month", fmt(expenses))
    c4.metric("Monthly savings", fmt(savings), delta=f"{(savings/income*100):.0f}% saved" if income > 0 else None)
    st.write("")
    col1,col2 = st.columns([1.35,1], gap="large")
    with col1:
        st.markdown("### Spending breakdown")
        exp = this_month[this_month["type"]=="Expense"] if not this_month.empty else this_month
        if not exp.empty:
            cat = exp.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
            fig = px.pie(cat, names="category", values="amount", hole=.62, template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=10), legend_title_text="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses this month yet. Add a transaction to see your spending chart.")
        st.markdown("### Recent transactions")
        if not tx.empty:
            recent = tx.sort_values("date", ascending=False).head(6).copy()
            recent["date"] = recent["date"].dt.strftime("%b %d, %Y")
            recent["amount"] = recent.apply(lambda r: ("+" if r["type"]=="Income" else "−")+fmt(r["amount"]), axis=1)
            st.dataframe(recent[["date","merchant","category","type","amount"]], use_container_width=True, hide_index=True)
        else: st.caption("Your recent activity will appear here.")
    with col2:
        score = financial_health_score(tx, profile, goals)
        st.markdown("### Financial health score")
        st.markdown(f"<div class='fin-card'><div style='font-size:3rem;color:#c1a2ff;font-weight:800'>{score}<span style='font-size:1rem;color:#8e9ab5'> / 100</span></div><div style='color:#b5bfd4'>Your score is an educational estimate based on savings, budget tracking and goal progress.</div></div>", unsafe_allow_html=True)
        st.progress(score/100)
        st.markdown("### Savings goals")
        if goals:
            for g in goals[:3]:
                current=float(g.get("current",0)); target=float(g.get("target",1) or 1)
                st.write(f"**{g['name']}** — {fmt(current)} / {fmt(target)}")
                st.progress(min(1,current/target))
        else: st.caption("Create a goal in Savings & Goals to track progress.")
        st.markdown("### Quick insights")
        insights = spending_insights(tx, symbol)
        for insight in insights[:3]: st.markdown(f"• {insight}")
    st.caption("Finwise AI provides educational estimates, not professional financial advice.")

elif page == "Budgeting & Expenses":
    title_block("PLAN YOUR MONEY", "Budgeting & Expenses", "Set monthly category limits and add income or expenses.")
    budgets = profile.get("budgets", {})
    with st.expander("Add transaction", expanded=True):
        with st.form("add_tx"):
            a,b,c = st.columns(3)
            ttype = a.selectbox("Type", ["Expense","Income"])
            amount = b.number_input(f"Amount ({currency})", min_value=0.01, value=25.0, step=5.0)
            txdate = c.date_input("Date", value=today)
            d,e = st.columns(2)
            category_options = ["Food & Dining","Transport","Shopping","Bills & Utilities","Entertainment","Health","Education","Housing","Travel","Salary","Freelance","Other"]
            category = d.selectbox("Category", category_options)
            merchant = e.text_input("Merchant / source", placeholder="e.g. Grocery store")
            note = st.text_input("Note (optional)")
            submit = st.form_submit_button("Save transaction", use_container_width=True)
        if submit:
            if not merchant.strip(): merchant = category
            if ttype=="Income" and category not in ["Salary","Freelance","Other"]: category = "Other"
            save_transaction(user_email, {"date":txdate.isoformat(),"type":ttype,"category":category,"merchant":merchant.strip(),"amount":float(amount),"note":note.strip()})
            st.success("Transaction saved.")
            st.rerun()
    st.markdown("### Monthly budgets")
    cats = ["Food & Dining","Transport","Shopping","Bills & Utilities","Entertainment","Health","Education","Housing","Travel","Other"]
    with st.form("budget_form"):
        budget_cols = st.columns(3)
        new_budgets = {}
        for i, cat in enumerate(cats):
            new_budgets[cat] = budget_cols[i%3].number_input(cat, min_value=0.0, value=float(budgets.get(cat,0)), step=25.0, key="budget_"+cat)
        save_b = st.form_submit_button("Save monthly budgets")
    if save_b:
        profile["budgets"] = new_budgets
        save_profile(user_email, profile)
        st.success("Budgets updated.")
        st.rerun()
    st.markdown("### Budget status")
    month_tx = tx[(tx["month"]==today.strftime("%Y-%m")) & (tx["type"]=="Expense")] if not tx.empty else tx
    status = budget_status(month_tx, profile.get("budgets",{}))
    if status:
        for item in status:
            st.write(f"**{item['category']}** — {fmt(item['spent'])} / {fmt(item['budget'])} ({item['percent']:.0f}%)")
            st.progress(min(item["percent"]/100,1.0))
            if item["percent"] > 100: st.error("Over budget")
            elif item["percent"] >= 80: st.warning("Close to budget limit")
    else: st.info("Set a budget above to start tracking category limits.")

elif page == "Savings & Goals":
    title_block("BUILD YOUR FUTURE", "Savings & Goals", "Create targets and track your progress.")
    with st.form("goal_form"):
        a,b,c = st.columns(3)
        gname = a.text_input("Goal name", placeholder="Emergency fund")
        target = b.number_input("Target amount", min_value=1.0, value=1000.0, step=100.0)
        current = c.number_input("Already saved", min_value=0.0, value=0.0, step=50.0)
        deadline = st.date_input("Target date", value=today+timedelta(days=180))
        add_goal = st.form_submit_button("Create savings goal")
    if add_goal:
        if not gname.strip(): st.error("Enter a goal name.")
        else:
            save_goal(user_email, {"name":gname.strip(),"target":float(target),"current":float(current),"deadline":deadline.isoformat()})
            st.success("Goal created.")
            st.rerun()
    if goals:
        for g in goals:
            with st.container(border=True):
                a,b = st.columns([4,1])
                target=float(g.get("target",0)); current=float(g.get("current",0)); pct=min(1,current/target) if target>0 else 0
                a.markdown(f"### {g['name']}")
                a.caption(f"Target date: {g.get('deadline','Not set')} · {pct*100:.0f}% complete")
                a.progress(pct)
                a.write(f"{fmt(current)} saved out of {fmt(target)}")
                with b:
                    with st.popover("Update"):
                        new_current=st.number_input("Current saved", min_value=0.0, value=current, key="goalcur_"+g["id"])
                        if st.button("Save progress", key="savegoal_"+g["id"]):
                            g["current"]=new_current; save_goal(user_email,g); st.rerun()
                    if st.button("Delete", key="delgoal_"+g["id"]):
                        delete_goal(user_email,g["id"]); st.rerun()
    else: st.info("Your goals will appear here.")

elif page == "Bills & Payments":
    title_block("STAY ON TOP", "Bills & Payments", "Keep track of due dates and mark bills as paid.")
    with st.form("bill_form"):
        a,b,c = st.columns(3)
        bname = a.text_input("Bill name", placeholder="Internet bill")
        bamount = b.number_input("Amount", min_value=0.01, value=50.0, step=5.0)
        due = c.date_input("Due date", value=today+timedelta(days=7))
        bill_category = st.selectbox("Category", ["Utilities","Rent / Housing","Phone / Internet","Insurance","Subscription","Loan / Credit","Other"])
        add_bill = st.form_submit_button("Add bill")
    if add_bill:
        if not bname.strip(): st.error("Enter a bill name.")
        else:
            save_bill(user_email, {"name":bname.strip(),"amount":float(bamount),"due_date":due.isoformat(),"category":bill_category,"paid":False})
            st.success("Bill added."); st.rerun()
    if bills:
        for bill in sorted(bills,key=lambda x:x.get("due_date","")):
            due_date = date.fromisoformat(bill["due_date"])
            label = "PAID" if bill.get("paid") else ("OVERDUE" if due_date < today else "UPCOMING")
            with st.container(border=True):
                a,b,c = st.columns([3,2,2])
                a.markdown(f"**{bill['name']}**")
                a.caption(f"{bill['category']} · Due {due_date.strftime('%d %b %Y')}")
                b.write(fmt(bill["amount"]))
                c.write(label)
                x,y = c.columns(2)
                if not bill.get("paid") and x.button("Mark paid",key="paid_"+bill["id"]):
                    bill["paid"]=True; save_bill(user_email,bill); st.rerun()
                if y.button("Delete",key="billdel_"+bill["id"]):
                    delete_bill(user_email,bill["id"]); st.rerun()
    else: st.info("No bills added yet.")

elif page == "Transactions":
    title_block("ACTIVITY", "Transactions", "Search, filter, export or delete your transaction history.")
    if not tx.empty:
        a,b,c = st.columns(3)
        search = a.text_input("Search merchant or note")
        types = b.multiselect("Type",["Income","Expense"],default=["Income","Expense"])
        cats_filter = c.multiselect("Category", sorted(tx["category"].dropna().unique().tolist()))
        view=tx[tx["type"].isin(types)].copy()
        if search: view=view[view.apply(lambda r: search.lower() in (str(r["merchant"])+str(r["note"])).lower(),axis=1)]
        if cats_filter: view=view[view["category"].isin(cats_filter)]
        show=view.sort_values("date",ascending=False).copy()
        show["date"]=show["date"].dt.strftime("%Y-%m-%d")
        st.dataframe(show[["date","type","category","merchant","amount","note"]],use_container_width=True,hide_index=True)
        st.download_button("Download filtered CSV",view.drop(columns=["month"],errors="ignore").to_csv(index=False).encode("utf-8"),"finwise_transactions.csv","text/csv")
        with st.expander("Delete a transaction"):
            choices={f"{r['date'].strftime('%Y-%m-%d')} · {r['merchant']} · {fmt(r['amount'])}":r["id"] for _,r in tx.iterrows()}
            chosen=st.selectbox("Choose transaction",list(choices.keys()))
            if st.button("Delete selected transaction"):
                delete_transaction(user_email,choices[chosen]); st.rerun()
    else: st.info("No transactions yet. Add your first one in Budgeting & Expenses.")

elif page == "AI Assistant":
    title_block("AI & INSIGHTS", "Finwise AI Assistant", "Ask questions about your own recorded spending. This local assistant does not send your data to an external AI service.")
    month_tx=tx[tx["month"]==today.strftime("%Y-%m")] if not tx.empty else tx
    suggestions=["Show my spending breakdown for this month","Where can I save money?","Suggest a budget for me","How is my financial health?"]
    cols=st.columns(2)
    for i,s in enumerate(suggestions):
        if cols[i%2].button(s,use_container_width=True,key="suggest_"+str(i)):
            st.session_state["finance_question"]=s
    question=st.text_input("Ask me anything about your finances",value=st.session_state.get("finance_question",""),placeholder="e.g. How much did I spend on food this month?")
    if st.button("Ask Finwise",type="primary"):
        answer=answer_finance_question(question,tx,profile,goals,bills,symbol)
        st.session_state["finance_answer"]=answer
        st.session_state["finance_question"]=question
    if st.session_state.get("finance_answer"):
        st.markdown(f"<div class='fin-card'><b>✦ Finwise says</b><br><br>{st.session_state['finance_answer']}</div>",unsafe_allow_html=True)
    st.markdown("### Suggested monthly budget")
    if st.button("Generate budget suggestion"):
        st.session_state["budget_suggestion"]=suggest_budget(tx,symbol)
    if st.session_state.get("budget_suggestion"): st.info(st.session_state["budget_suggestion"])
    st.caption("This is a rule-based local assistant for a student project, not a paid generative AI service.")

elif page == "Financial Health":
    title_block("YOUR FINANCIAL WELLBEING", "Financial Health", "An educational score based on the data you enter.")
    score=financial_health_score(tx,profile,goals)
    c1,c2=st.columns([1,2])
    c1.metric("Financial health score",f"{score}/100")
    c2.progress(score/100)
    st.markdown("### What affects your score?")
    for item in spending_insights(tx,symbol): st.markdown("• "+item)
    st.markdown("### Simple habits to improve it")
    st.markdown("- Record income and expenses regularly.\n- Set realistic category budgets and review overspending.\n- Build an emergency savings goal.\n- Pay bills before their due dates.")
    st.warning("This score is an educational estimate, not a credit score or professional financial assessment.")

elif page == "Reports & Analytics":
    title_block("SEE THE BIG PICTURE", "Reports & Analytics", "Explore monthly trends, category spending and export your data.")
    if not tx.empty:
        exp=tx[tx["type"]=="Expense"].copy()
        if not exp.empty:
            monthly=tx.pivot_table(index="month",columns="type",values="amount",aggfunc="sum",fill_value=0).reset_index()
            melted=monthly.melt(id_vars="month",var_name="Type",value_name="Amount")
            fig=px.bar(melted,x="month",y="Amount",color="Type",barmode="group",template="plotly_dark",title="Income vs expenses by month")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig,use_container_width=True)
            cat=exp.groupby("category",as_index=False)["amount"].sum().sort_values("amount",ascending=False)
            fig2=px.bar(cat,x="category",y="amount",template="plotly_dark",title="Total expenses by category")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis_title="",yaxis_title=f"Amount ({currency})")
            st.plotly_chart(fig2,use_container_width=True)
        else: st.info("Add expense transactions to unlock category reports.")
        st.download_button("Export all transactions (CSV)",transactions.to_csv(index=False).encode("utf-8"),"finwise_all_transactions.csv","text/csv")
    else: st.info("Add transactions to see analytics.")

elif page == "Settings":
    title_block("PREFERENCES", "Settings", "Manage your profile and display preferences.")
    with st.form("profile_form"):
        name=st.text_input("Display name",value=profile.get("name",user.get("name","")))
        currency2=st.selectbox("Currency",["USD","INR","GBP","EUR","CAD","AUD"],index=["USD","INR","GBP","EUR","CAD","AUD"].index(profile.get("currency","USD")))
        monthly_income=st.number_input("Expected monthly income",min_value=0.0,value=float(profile.get("monthly_income",0)),step=100.0)
        save_p=st.form_submit_button("Save settings")
    if save_p:
        profile.update({"name":name.strip() or user.get("name",""),"currency":currency2,"monthly_income":monthly_income})
        save_profile(user_email,profile); st.success("Settings saved."); st.rerun()
    st.markdown("### Data and privacy")
    st.write("Your account and finance records are stored locally in the `data/` folder of this project. This demo does not connect to a bank or payment network.")
    if st.button("Download my data as JSON"):
        st.download_button("Click to download",json.dumps({"profile":profile,"transactions":transactions.to_dict("records"),"bills":bills,"goals":goals},indent=2,default=str),"my_finwise_data.json","application/json")

elif page == "Help & Support":
    title_block("NEED A HAND?", "Help & Support", "Quick guide for using Finwise.")
    with st.expander("How do I start?"):
        st.write("Open Budgeting & Expenses and add income or expense records. The dashboard and reports update automatically.")
    with st.expander("How do budgets work?"):
        st.write("Set a monthly limit for each category. Finwise compares it with expense transactions dated in the current month.")
    with st.expander("How do savings goals work?"):
        st.write("Create a target, then use Update to change the amount you have saved.")
    with st.expander("Is my bank connected?"):
        st.write("No. This student project uses transactions entered manually. It does not access real bank accounts or transfer money.")
    with st.expander("Does the AI use a paid API?"):
        st.write("No. The assistant uses local rules and your entered data, so no API key or paid service is needed.")
    st.markdown("### Project details")
    st.write("Finwise AI · Smart Expense Tracker with AI Insights · Python + Streamlit + pandas + Plotly")
