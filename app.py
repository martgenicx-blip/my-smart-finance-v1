import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", page_icon="💰", layout="wide")

# --- UI එක පින්තූරෙ වගේම කරන්න CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .main { background-color: #f0f2f6; }
    
    /* Top Action Cards */
    div.stButton > button {
        height: 100px !important;
        border-radius: 10px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Hover Effects */
    div.stButton > button:hover {
        border-color: #2196F3 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }

    /* Summary Row Styling */
    .summary-box {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #ddd;
        text-align: center;
    }
    .income-val { color: #2e7d32; font-weight: bold; font-size: 20px; }
    .expense-val { color: #c62828; font-weight: bold; font-size: 20px; }
    .balance-val { color: #333; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- Login Logic ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.title("🔐 Login")
        pwd = st.text_input("Password", type="password")
        if st.button("Login 🚀"):
            if pwd == "###1984***":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- Google Sheets Connection ---
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
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet = sh.worksheet("Sheet1")
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- UI Header ---
st.title("💰 Income Expense Tracker")

# --- පින්තූරෙ තියෙන විදිහටම Top 4 Buttons ---
c1, c2 = st.columns(2)
with c1:
    inc_btn = st.button("➕\nAdd Income")
with c2:
    exp_btn = st.button("➖\nAdd Expense")

c3, c4 = st.columns(2)
with c3:
    st.button("🔄\nTransfer")
with c4:
    st.button("📑\nTransactions")

st.write("---")

# --- Summary Table (Image විදිහටම) ---
if not df.empty:
    total_inc = df[df['Type'] == 'Income']['Amount'].sum()
    total_exp = df[df['Type'] == 'Expense']['Amount'].sum()
    balance = total_inc - total_exp

    st.markdown(f"""
        <table style="width:100%; border:1px solid #ddd; text-align:center; background-color:white;">
            <tr style="background-color:#f8f9fa;">
                <th style="color:green;">Income</th>
                <th style="color:red;">Expense</th>
                <th>Balance</th>
            </tr>
            <tr>
                <td class="income-val">{total_inc:,.2f}</td>
                <td class="expense-val">{total_exp:,.2f}</td>
                <td class="balance-val">{balance:,.2f}</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)

st.write("### Recent Transactions")

# --- Data Entry Modal (බොත්තම් එබුවම විවෘත වෙන Form එක) ---
if inc_btn or exp_btn:
    t_type = "Income" if inc_btn else "Expense"
    with st.expander(f"➕ Add New {t_type}", expanded=True):
        with st.form("new_entry", clear_on_submit=True):
            amt = st.number_input("Amount", min_value=0.0)
            cat = st.selectbox("Category", ["Groceries", "Bank", "Kids", "Personal", "Other"])
            note = st.text_input("Note")
            if st.form_submit_button("Save"):
                worksheet.append_row([str(date.today()), cat, amt, note, t_type])
                st.success("Saved!")
                st.rerun()

# --- Recent History (Image style list) ---
if not df.empty:
    display_df = df.iloc[::-1].head(10)
    for idx, row in display_df.iterrows():
        color = "red" if row['Type'] == "Expense" else "green"
        st.markdown(f"""
            <div style="background-color:white; padding:10px; border-radius:5px; margin-bottom:5px; border-left: 5px solid {color};">
                <span style="float:right; color:{color}; font-weight:bold;">{row['Amount']}</span>
                <div style="font-size:12px; color:gray;">{row['Date']}</div>
                <div style="font-weight:bold;">{row['Category']}</div>
                <div style="font-size:14px;">{row['Description']}</div>
            </div>
            """, unsafe_allow_html=True)
