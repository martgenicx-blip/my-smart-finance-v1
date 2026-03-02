import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CSS (FIXING BUTTON FUNCTIONALITY & LOOK) ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f3f6; }
    
    .header-bar {
        background-color: #0081C9; padding: 15px; color: white;
        text-align: center; font-size: 20px; font-weight: bold;
        margin: -60px -20px 20px -20px;
    }

    /* --- 2x2 GRID FIX FOR STREAMLIT BUTTONS --- */
    div[data-testid="column"] {
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }

    /* Button Style */
    div.stButton > button {
        width: 100% !important;
        height: 100px !important;
        border-radius: 12px !important;
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        font-weight: bold !important;
        font-size: 16px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-decoration: none !important;
    }

    div.stButton > button:hover {
        border-color: #0081C9 !important;
        color: #0081C9 !important;
        background-color: #f0f8ff !important;
    }

    /* Quality Form Styling */
    [data-testid="stForm"] {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border: 1px solid #e0e0e0 !important;
    }
    div[data-baseweb="input"] {
        border: 2px solid #d1d1d1 !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #0081C9 !important;
    }

    /* Summary & Recent Trans */
    .summary-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; text-align: center; }
    .sum-grid { display: flex; justify-content: space-around; border-top: 1px solid #eee; padding-top: 10px; margin-top: 10px; }
    .bal-box { background: #e3f2fd; padding: 10px; border-radius: 8px; margin-top: 10px; text-align: right; font-weight: bold; color: green; }
    .trans-card { background: white; padding: 12px; border-radius: 10px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; }

    /* Floating Button */
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 999999 !important; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { width: 60px; height: 60px; background: #0081C9; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 35px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header-bar">Income Expense</div>', unsafe_allow_html=True)

# --- Google Sheets Connection ---
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
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except Exception:
    st.error("Data Load Error"); st.stop()

# Session State for Forms
if "active_form" not in st.session_state:
    st.session_state.active_form = None

# --- 1. ACTION BUTTONS (Real Streamlit Buttons in 2x2 Grid) ---
col1, col2 = st.columns(2)
with col1:
    if st.button("➕\nIncome", key="btn_inc"): st.session_state.active_form = "Income"
    if st.button("🔄\nTransfer", key="btn_trf"): st.session_state.active_form = "Transfer"
with col2:
    if st.button("➖\nExpense", key="btn_exp"): st.session_state.active_form = "Expense"
    if st.button("📜\nHistory", key="btn_his"): st.session_state.active_form = "History"

# --- 2. DATA ENTRY FORM ---
if st.session_state.active_form in ["Income", "Expense", "Transfer"]:
    st.markdown(f"### 📝 New {st.session_state.active_form}")
    with st.form("entry_form", clear_on_submit=True):
        f_date = st.date_input("Select Date", date.today())
        f_amount = st.number_input("Enter Amount (LKR)", value=0.0, step=1.0)
        f_note = st.text_input("Add a Note")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.form_submit_button("Save Record ✅"):
                if f_amount > 0:
                    ts = f"{f_date} {datetime.now().strftime('%H:%M:%S')}"
                    worksheet.append_row([ts, "General", f_amount, f_note, st.session_state.active_form, "", ""])
                    st.session_state.active_form = None
                    st.rerun()
        with col_s2:
            if st.form_submit_button("Cancel ❌"):
                st.session_state.active_form = None
                st.rerun()

# --- 3. SUMMARY CARD ---
if not df.empty:
    total_income = df[df['Type'] == 'Income']['Amount'].sum()
    total_expense = df[df['Type'] == 'Expense']['Amount'].sum()
    current_balance = total_income - total_expense
    prev_balance = 38814.85
    final_total = prev_balance + current_balance

    st.markdown(f"""
        <div class="summary-card">
            <div style="font-size:12px; color:gray;">{date.today().strftime('%d-%b-%Y')}</div>
            <div class="sum-grid">
                <div><span style="color:green; font-size:11px;">Income</span><br><b style="color:green;">{total_income:,.0f}</b></div>
                <div><span style="color:red; font-size:11px;">Expense</span><br><b style="color:red;">{total_expense:,.0f}</b></div>
                <div><span style="color:gray; font-size:11px;">Balance</span><br><b>{current_balance:,.0f}</b></div>
            </div>
            <div style="text-align:right; font-size:12px; color:gray; margin-top:10px;">Previous Balance <span style="color:green; font-weight:bold;">{prev_balance:,.2f}</span></div>
            <div class="bal-box">Total Balance <span>{final_total:,.2f}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 4. RECENT TRANSACTIONS ---
st.write("<b>Recent Transactions</b>", unsafe_allow_html=True)
if not df.empty:
    latest = df.iloc[::-1].head(10)
    for _, row in latest.iterrows():
        color = "#dc3545" if row['Type'] == "Expense" else "#28a745"
        st.markdown(f"""
            <div class="trans-card">
                <div>
                    <div style="font-size:11px; color:gray;">{row['Date']}</div>
                    <div style="font-weight:bold; font-size:14px;">{row['Category']}</div>
                    <div style="background:#eee; display:inline-block; padding:2px 6px; border-radius:4px; font-size:10px; color:#555;">BANK</div>
                </div>
                <div style="color:{color}; font-weight:bold; font-size:16px;">{row['Amount']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

# --- 5. FLOATING ACTION MENU ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
