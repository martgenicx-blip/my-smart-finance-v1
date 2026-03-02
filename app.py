import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CUSTOM CSS (Alignment & Design Fix) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-bar {
        background-color: #0081C9;
        padding: 15px;
        color: white;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin: -60px -20px 20px -20px;
    }
    div[data-testid="stHorizontalBlock"] { gap: 10px !important; }
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        border-radius: 12px !important;
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #eee !important;
        font-weight: bold !important;
        font-size: 15px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    .summary-table {
        width: 100%;
        background: white;
        border-collapse: collapse;
        margin-top: 10px;
        border-radius: 10px;
        border: 1px solid #eee;
    }
    .summary-table td { padding: 12px; border: 1px solid #eee; text-align: center; }
    .fab-wrapper { position: fixed; bottom: 30px; right: 30px; z-index: 9999; }
    .fab-main {
        width: 60px; height: 60px; background: #0081C9; border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        color: white; font-size: 35px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        cursor: pointer; transition: 0.3s;
    }
    .fab-list {
        position: absolute; bottom: 75px; right: 0;
        display: none; flex-direction: column; gap: 12px; align-items: flex-end;
    }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-wrapper:hover .fab-main { transform: rotate(45deg); background: #444; }
    .fab-item { display: flex; align-items: center; gap: 10px; }
    .fab-label {
        color: white; padding: 4px 12px; border-radius: 6px;
        font-size: 13px; font-weight: bold; white-space: nowrap;
    }
    .fab-icon {
        width: 42px; height: 42px; border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        color: white; font-size: 18px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .bg-income { background-color: #28a745; }
    .bg-expense { background-color: #dc3545; }
    .bg-transfer { background-color: #fd7e14; }
    .bg-trans { background-color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header-bar">Income Expense Tracker</div>', unsafe_allow_html=True)

if "show_form" not in st.session_state: st.session_state.show_form = None

# --- Connection ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = {k: st.secrets["connections"]["gsheets"][k] for k in st.secrets["connections"]["gsheets"]}
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet = sh.worksheet("Sheet1")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        df['Date_Only'] = pd.to_datetime(df['Date'], format='mixed').dt.date
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except:
    st.error("Sheet Connection Error"); st.stop()

# --- 1. MAIN BUTTONS GRID ---
col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Income", key="btn_inc"): st.session_state.show_form = "Income"
    if st.button("🔄 Transfer", key="btn_trf"): st.session_state.show_form = "Transfer"
with col2:
    if st.button("➖ Expense", key="btn_exp"): st.session_state.show_form = "Expense"
    if st.button("📜 History", key="btn_his"): st.session_state.show_form = "History"

# --- 2. DATA ENTRY FORM ---
if st.session_state.show_form in ["Income", "Expense", "Transfer"]:
    st.write("---")
    with st.form("entry_form", clear_on_submit=True):
        st.subheader(f"📝 New {st.session_
