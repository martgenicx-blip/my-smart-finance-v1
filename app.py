import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", page_icon="💰", layout="wide")

# --- CSS (බොත්තම් 4ම එකම size එකට සහ ලස්සනට ගන්න) ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        display: block !important;
    }
    div.stButton > button:hover {
        border-color: #2196F3 !important;
        background-color: #f0f8ff !important;
    }
    .summary-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #eee;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State (බොත්තම එබුවම Form එක පෙන්වන්න) ---
if "show_form" not in st.session_state:
    st.session_state.show_form = None

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
st.title("💰 Finance Tracker")

# --- මෙන්න එකම Size එකේ බොත්තම් 4 ---
c1, c2, c3, c4 = st.columns(4)

if c1.button("➕\nIncome"):
    st.session_state.show_form = "Income"
if c2.button("➖\nExpense"):
    st.session_state.show_form = "Expense"
if c3.button("🔄\nTransfer"):
    st.info("Transfer feature coming soon!")
if c4.button("📑\nHistory"):
    st.session_state.show_form = "History"

st.write("---")

# --- Form එක පෙන්වන කොටස (බොත්තම එබූ විට) ---
if st.session_state.show_form in ["Income", "Expense"]:
    t_type = st.session_state.show_form
    with st.container():
        st.subheader(f"New {t_type} Entry")
        with st.form("entry_form", clear_on_submit=True):
            amt = st.number_input("Amount (LKR)", min_value=0.0, step=100.0)
            cat = st.selectbox("Category", ["Food", "Salary", "Bills", "Travel", "Shopping", "Other"])
            note = st.text_input("Description")
            sub_col1, sub_col2 = st.columns([1, 4])
            if sub_col1.form_submit_button("Save ✅"):
                if amt > 0:
                    worksheet.append_row([str(date.today()), cat, amt, note, t_type])
                    st.success("Saved Successfully!")
                    st.session_state.show_form = None
                    st.rerun()
            if sub_col2.form_submit_button("Cancel ❌"):
                st.session_state.show_form = None
                st.rerun()

# --- Summary Section ---
if not df.empty:
    total_inc = df[df['Type'] == 'Income']['Amount'].sum()
    total_exp = df[df['Type'] == 'Expense']['Amount'].sum()
    
    sc1, sc2, sc3 = st.columns(3)
    sc1.markdown(f'<div class="summary-card"><p>Income</p><h2 style="color:green;">{total_inc:,.0f}</h2></div>', unsafe_allow_html=True)
    sc2.markdown(f'<div class="summary-card"><p>Expense</p><h2 style="color:red;">{total_exp:,.0f}</h2></div>', unsafe_allow_html=True)
    sc3.markdown(f'<div class="summary-card"><p>Balance</p><h2>{total_inc - total_exp:,.0f}</h2></div>', unsafe_allow_html=True)

st.write("### Recent Transactions")

# --- Transaction History List ---
if not df.empty:
    display_df = df.iloc[::-1].head(10)
    for idx, row in display_df.iterrows():
        color = "#ff4b4b" if row['Type'] == "Expense" else "#28a745"
        st.markdown(f"""
            <div style="background-color:white; padding:15px; border-radius:10px; margin-bottom:10px; border-left: 8px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <span style="float:right; color:{color}; font-weight:bold; font-size:18px;">LKR {row['Amount']:,.0f}</span>
                <div style="font-size:12px; color:gray;">{row['Date']}</div>
                <div style="font-weight:bold; font-size:16px;">{row['Category']}</div>
                <div style="font-size:14px; color:#555;">{row['Description']}</div>
            </div>
            """, unsafe_allow_html=True)
