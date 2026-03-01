import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# --- පිටුවේ සැකසුම් ---
st.set_page_config(page_title="Smart Finance v1", page_icon="💰", layout="wide")

# --- Custom CSS (ලස්සන කරන්න) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2ecc71; color: white; }
    .login-card { background-color: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- මුරපදය පරීක්ෂාව (ලස්සන කළ Login Screen එක) ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # Login එක මැදට ගන්න Columns පාවිච්චි කරමු
    _, col_mid, _ = st.columns([1, 1, 1])
    
    with col_mid:
        st.write("#") # පොඩි ඉඩක්
        st.image("https://cdn-icons-png.flaticon.com/512/2850/2850358.png", width=100) # පොඩි Icon එකක්
        st.title("Welcome Back!")
        st.subheader("🔐 Login to Pocket Finance")
        
        with st.container():
            pwd = st.text_input("Enter Secret Password", type="password", placeholder="Your password here...")
            if st.button("Login Now 🚀"):
                if pwd == "###1984***":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("වැරදි මුරපදයක්! ආයෙත් උත්සාහ කරන්න.")
    st.stop() # Login වෙනකම් ඉතිරි Code එක වැඩ කරන්නේ නැහැ

# --- මෙතන සිට ඇතුළත Code එක (Dashboard) ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"],
    }
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    sheet_id = "1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8"
    sh = client.open_by_key(sheet_id)
    worksheet = sh.worksheet("Sheet1")
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- UI (Dashboard Content) ---
st.title("💰 Smart Finance Dashboard")

if not df.empty:
    total_income = df[df['Type'] == 'Income']['Amount'].sum()
    total_expense = df[df['Type'] == 'Expense']['Amount'].sum()
    balance = total_income - total_expense

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Income", f"LKR {total_income:,.2f}")
    m2.metric("Total Expense", f"LKR {total_expense:,.2f}", delta=f"-{total_expense:,.2f}", delta_color="inverse")
    m3.metric("Net Balance", f"LKR {balance:,.2f}")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Expense by Category")
        expense_df = df[df['Type'] == 'Expense']
        if not expense_df.empty:
            fig_pie = px.pie(expense_df, values='Amount', names='Category', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        st.subheader("Income vs Expense")
        sum_df = pd.DataFrame({"Type": ["Income", "Expense"], "Amount": [total_income, total_expense]})
        fig_bar = px.bar(sum_df, x='Type', y='Amount', color='Type', color_discrete_map={"Income": "#2ecc71", "Expense": "#e74c3c"})
        st.plotly_chart(fig_bar, use_container_width=True)

st.divider()
tab1, tab2 = st.tabs(["➕ Add Entry", "📊 History Log"])

with tab1:
    with st.form("add_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        t_type = col_a.selectbox("Type", ["Expense", "Income"])
        t_amt = col_b.number_input("Amount (LKR)", min_value=0.0)
        t_cat = st.selectbox("Category", ["Food", "Travel", "Bills", "Rent", "Salary", "Shopping", "Other"])
        t_note = st.text_input("Description")
        if st.form_submit_button("Save Entry"):
            if t_amt > 0:
                new_row = [str(date.today()), t_cat, t_amt, t_note, t_type]
                worksheet.append_row(new_row)
                st.success("Saved Successfully! ✅")
                st.rerun()

with tab2:
    if not df.empty:
        st.dataframe(df.iloc[::-1], use_container_width=True)
