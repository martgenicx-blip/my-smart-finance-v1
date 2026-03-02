import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CUSTOM CSS (Classic UI + Floating Button) ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f3f6; }
    
    .header-bar {
        background-color: #0081C9; padding: 15px; color: white;
        text-align: center; font-size: 20px; font-weight: bold;
        margin: -60px -20px 20px -20px;
    }

    /* Tabs Styling */
    .tab-bar {
        display: flex; justify-content: space-around; background: white;
        margin: -20px -20px 15px -20px; border-bottom: 1px solid #ddd;
        padding: 10px 0; font-weight: bold; color: gray;
    }
    .tab-active { color: #0081C9; border-bottom: 2px solid #0081C9; padding-bottom: 5px; }

    /* Action Buttons (2x2 Grid) */
    div.stButton > button {
        width: 100% !important; height: 100px !important;
        border-radius: 12px !important; background-color: white !important;
        color: #333 !important; border: 1px solid #ddd !important;
        font-weight: bold !important; font-size: 15px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        margin-bottom: 10px !important;
    }

    /* Summary Card */
    .summary-card {
        background: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px;
        text-align: center;
    }
    .sum-grid { display: flex; justify-content: space-around; border-top: 1px solid #eee; padding-top: 10px; margin-top: 10px; }
    .bal-box { background: #e3f2fd; padding: 10px; border-radius: 8px; margin-top: 10px; text-align: right; font-weight: bold; color: green; }

    /* --- FLOATING ACTION BUTTON (The Star!) --- */
    .fab-wrapper {
        position: fixed; bottom: 30px; right: 25px; z-index: 99999 !important;
        display: flex; flex-direction: column; align-items: flex-end; gap: 12px;
    }
    .fab-main {
        width: 60px; height: 60px; background: #0081C9; border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        color: white; font-size: 35px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        cursor: pointer; transition: 0.3s;
    }
    .fab-list { display: none; flex-direction: column; gap: 10px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-wrapper:hover .fab-main { transform: rotate(45deg); background: #333; }
    .fab-item { display: flex; align-items: center; gap: 10px; }
    .fab-label { background: white; padding: 4px 10px; border-radius: 5px; font-size: 12px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .fab-icon { width: 42px; height: 42px; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 18px; }
    
    .bg-income { background-color: #28a745; }
    .bg-expense { background-color: #dc3545; }
    .bg-transfer { background-color: #fd7e14; }
    .bg-trans { background-color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- Header & Tabs ---
st.markdown('<div class="header-bar">Income Expense ⌄</div>', unsafe_allow_html=True)
st.markdown('<div class="tab-bar"><span class="tab-active">HOME</span><span>CALENDAR</span><span>NOTEBOOK</span></div>', unsafe_allow_html=True)

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
except:
    st.error("Sheet Connection Error"); st.stop()

# --- 1. ACTION BUTTONS (2x2 Grid) ---
col1, col2 = st.columns(2)
with col1:
    if st.button("⊕\nAdd Income", key="btn_inc"): st.session_state.show_form = "Income"
    if st.button("⇄\nTransfer", key="btn_trf"): st.session_state.show_form = "Transfer"
with col2:
    if st.button("⊖\nAdd Expense", key="btn_exp"): st.session_state.show_form = "Expense"
    if st.button("☰\nTransactions", key="btn_his"): st.session_state.show_form = "History"

# --- 2. DATA ENTRY FORM ---
if st.session_state.show_form in ["Income", "Expense", "Transfer"]:
    with st.expander(f"📝 New {st.session_state.show_form}", expanded=True):
        with st.form("entry_form", clear_on_submit=True):
            d = st.date_input("Date", date.today())
            amt = st.number_input("Amount (LKR)", value=None, placeholder="0.00")
            note = st.text_input("Note")
            if st.form_submit_button("Save Record ✅"):
                if amt:
                    ts = f"{d} {datetime.now().strftime('%H:%M:%S')}"
                    worksheet.append_row([ts, "General", amt, note, st.session_state.show_form, "", ""])
                    st.session_state.show_form = None
                    st.rerun()

# --- 3. SUMMARY CARD ---
st.markdown(f"""
    <div class="summary-card">
        <div style="font-size:12px; color:gray;">21-Feb-2026 -> 20-Mar-2026</div>
        <div class="sum-grid">
            <div><span style="color:green; font-size:11px;">Income</span><br><b style="color:green;">0</b></div>
            <div><span style="color:red; font-size:11px;">Expense</span><br><b style="color:red;">0</b></div>
            <div><span style="color:gray; font-size:11px;">Balance</span><br><b>0</b></div>
        </div>
        <div style="text-align:right; font-size:12px; color:gray; margin-top:10px;">Previous Balance <span style="color:green; font-weight:bold;">38,814.85</span></div>
        <div class="bal-box">Balance <span>38,814.85</span></div>
    </div>
""", unsafe_allow_html=True)

# --- 4. RECENT TRANSACTIONS ---
st.write("<b>Recent Transactions</b>", unsafe_allow_html=True)
if not df.empty:
    latest = df.iloc[::-1].head(10)
    for _, row in latest.iterrows():
        color = "#dc3545" if row['Type'] == "Expense" else "#28a745"
        st.markdown(f"""
            <div style="background:white; padding:15px; border-radius:10px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #eee;">
                <div>
                    <div style="font-size:11px; color:gray;">{row['Date']}</div>
                    <div style="font-weight:bold; font-size:14px;">{row['Category']}</div>
                    <div style="background:#eee; display:inline-block; padding:2px 6px; border-radius:4px; font-size:10px; color:#555;">BANK</div>
                </div>
                <div style="color:{color}; font-weight:bold; font-size:16px;">{row['Amount']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

# --- 5. FLOATING ACTION MENU (Back Again!) ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-list">
            <div class="fab-item"><span class="fab-label">Transactions</span><div class="fab-icon bg-trans">📜</div></div>
            <div class="fab-item"><span class="fab-label">Transfer</span><div class="fab-icon bg-transfer">🔄</div></div>
            <div class="fab-item"><span class="fab-label">Add Income</span><div class="fab-icon bg-income">➕</div></div>
            <div class="fab-item"><span class="fab-label">Add Expense</span><div class="fab-icon bg-expense">➖</div></div>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
