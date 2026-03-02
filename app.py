import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CSS (KEEPING EVERYTHING SAME + FLOATING BTN FIX) ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f3f6; }
    .header-bar {
        background-color: #0081C9; padding: 15px; color: white;
        text-align: center; font-size: 20px; font-weight: bold;
        margin: -60px -20px 20px -20px;
    }
    /* Button Grid (2x2) */
    .custom-grid {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 12px; margin-top: 10px; margin-bottom: 20px;
    }
    .grid-item {
        background: white; border: 1px solid #ddd; border-radius: 12px;
        height: 90px; display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        font-weight: bold; color: #333; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        cursor: pointer; text-decoration: none; font-size: 14px;
    }
    /* Summary Card */
    .summary-card {
        background: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; text-align: center;
    }
    .sum-grid { display: flex; justify-content: space-around; border-top: 1px solid #eee; padding-top: 10px; margin-top: 10px; }
    .bal-box { background: #e3f2fd; padding: 10px; border-radius: 8px; margin-top: 10px; text-align: right; font-weight: bold; color: green; }
    
    .trans-card {
        background: white; padding: 12px; border-radius: 10px; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee;
    }

    /* --- FLOATING ACTION MENU --- */
    .fab-wrapper {
        position: fixed; bottom: 30px; right: 25px; z-index: 999999 !important;
        display: flex; flex-direction: column; align-items: flex-end; gap: 12px;
    }
    .fab-main {
        width: 60px; height: 60px; background: #0081C9; border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        color: white; font-size: 35px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        cursor: pointer; transition: 0.3s ease;
    }
    .fab-list {
        display: none; flex-direction: column; gap: 10px; align-items: flex-end;
    }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-wrapper:hover .fab-main { transform: rotate(45deg); background: #333; }
    
    .fab-item { display: flex; align-items: center; gap: 10px; text-decoration: none; }
    .fab-label {
        background: white; padding: 5px 12px; border-radius: 6px;
        font-size: 13px; font-weight: bold; color: #333; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .fab-icon {
        width: 45px; height: 45px; border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        color: white; font-size: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header-bar">Income Expense ⌄</div>', unsafe_allow_html=True)

# --- Connection to Google Sheets ---
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

# --- 1. ACTION BUTTONS (STAYING THE SAME) ---
st.markdown("""
    <div class="custom-grid">
        <a href="/?form=Income" target="_self" class="grid-item"><span>➕</span> Income</a>
        <a href="/?form=Expense" target="_self" class="grid-item"><span>➖</span> Expense</a>
        <a href="/?form=Transfer" target="_self" class="grid-item"><span>🔄</span> Transfer</a>
        <a href="/?form=History" target="_self" class="grid-item"><span>📜</span> History</a>
    </div>
""", unsafe_allow_html=True)

# URL Params Handling
query_form = st.query_params.get("form")

# --- 2. DATA ENTRY FORM ---
if query_form in ["Income", "Expense", "Transfer"]:
    st.write(f"### New {query_form}")
    with st.form("entry_form", clear_on_submit=True):
        d = st.date_input("Date", date.today())
        amt = st.number_input("Amount (LKR)", value=0.0)
        note = st.text_input("Note")
        if st.form_submit_button("Save Record ✅"):
            ts = f"{d} {datetime.now().strftime('%H:%M:%S')}"
            worksheet.append_row([ts, "General", amt, note, query_form, "", ""])
            st.query_params.clear()
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

# --- 5. FLOATING ACTION MENU (FIXED & FUNCTIONAL) ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-list">
            <a href="/?form=History" target="_self" class="fab-item">
                <span class="fab-label">History</span><div class="fab-icon" style="background:#007bff;">📜</div>
            </a>
            <a href="/?form=Transfer" target="_self" class="fab-item">
                <span class="fab-label">Transfer</span><div class="fab-icon" style="background:#fd7e14;">🔄</div>
            </a>
            <a href="/?form=Income" target="_self" class="fab-item">
                <span class="fab-label">Income</span><div class="fab-icon" style="background:#28a745;">➕</div>
            </a>
            <a href="/?form=Expense" target="_self" class="fab-item">
                <span class="fab-label">Expense</span><div class="fab-icon" style="background:#dc3545;">➖</div>
            </a>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
