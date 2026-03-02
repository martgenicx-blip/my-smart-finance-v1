import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- UI FIX: 2x2 GRID & MOBILE OPTIMIZATION ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    .header-bar {
        background-color: #0081C9; padding: 15px; color: white;
        text-align: center; font-size: 18px; font-weight: bold;
        margin: -60px -20px 20px -20px;
    }

    /* බටන් 4 ලස්සනට 2x2 Grid එකකට ගන්නා රහස මෙන්න */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important; /* Mobile වලදී පේළි දෙකකට කඩන්න */
        gap: 10px !important;
        justify-content: center !important;
    }

    [data-testid="stHorizontalBlock"] > div {
        /* Mobile එකේදී width එක 50% කට වඩා අඩුවෙන් දීලා බටන් 2ක් පේළියට ගන්නවා */
        flex: 1 1 45% !important; 
        min-width: 140px !important;
        max-width: 48% !important;
    }

    div.stButton > button {
        width: 100% !important;
        height: 100px !important;
        border-radius: 12px !important;
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        font-weight: bold !important;
        font-size: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        white-space: pre-wrap !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }

    div.stButton > button:hover {
        border-color: #0081C9 !important;
        background-color: #f0f8ff !important;
    }

    /* Summary & Floating Menu (Unchanged) */
    .summary-table { width: 100%; background: white; border-collapse: collapse; margin-top: 15px; border-radius: 12px; border: 1px solid #eee; overflow: hidden; }
    .summary-table td { padding: 12px; border: 1px solid #eee; text-align: center; }
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 99999 !important; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { width: 60px; height: 60px; background: #0081C9; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 35px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); cursor: pointer; }
    .fab-list { display: none; flex-direction: column; gap: 10px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .bg-income { background-color: #28a745; }
    .bg-expense { background-color: #dc3545; }
    .bg-transfer { background-color: #fd7e14; }
    .bg-trans { background-color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header-bar">Income Expense Tracker</div>', unsafe_allow_html=True)

if "show_form" not in st.session_state: st.session_state.show_form = None

# --- Connection (Sheets) ---
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
    st.error("Connection Error"); st.stop()

# --- 1. THE FIXED BUTTON GRID (2x2 Style) ---
# මෙතන තමයි ඔයාට ඕන පිළිවෙළ තියෙන්නේ
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🟢\nAdd Income", key="btn_inc"): st.session_state.show_form = "Income"
with col2:
    if st.button("🔴\nAdd Expense", key="btn_exp"): st.session_state.show_form = "Expense"
with col3:
    if st.button("🟠\nTransfer", key="btn_trf"): st.session_state.show_form = "Transfer"
with col4:
    if st.button("🔵\nTransactions", key="btn_his"): st.session_state.show_form = "History"

# --- 2. DATA ENTRY FORM ---
if st.session_state.show_form in ["Income", "Expense", "Transfer"]:
    st.write("---")
    with st.form("entry_form", clear_on_submit=True):
        st.subheader(f"📝 New {st.session_state.show_form}")
        d = st.date_input("Date", date.today())
        amt = st.number_input("Amount (LKR)", value=None, placeholder="0.00")
        note = st.text_input("Note")
        if st.form_submit_button("Save Record ✅"):
            if amt:
                ts = f"{d} {datetime.now().strftime('%H:%M:%S')}"
                worksheet.append_row([ts, "General", amt, note, st.session_state.show_form, "", ""])
                st.session_state.show_form = None
                st.rerun()

# --- 3. SUMMARY & TRANSACTIONS (Simplified for beauty) ---
st.markdown(f"""
    <div style="text-align:center; font-size:12px; color:gray; margin-top:20px;">{date.today().strftime('%d %B %Y')}</div>
    <table class="summary-table">
        <tr style="background:#e3f2fd; font-weight:bold;"><td colspan="2" style="text-align:right;">Total Cash</td><td style="color:green; font-size:15px;">38,814.85</td></tr>
    </table>
""", unsafe_allow_html=True)

# --- 4. FLOATING MENU ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-list">
            <div class="fab-item"><div style="background:white; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; box-shadow:0 2px 4px rgba(0,0,0,0.1);">Add Income</div><div class="fab-icon bg-income" style="width:40px; height:40px; border-radius:50%; display:flex; justify-content:center; align-items:center; color:white;">➕</div></div>
            <div class="fab-item"><div style="background:white; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; box-shadow:0 2px 4px rgba(0,0,0,0.1);">Add Expense</div><div class="fab-icon bg-expense" style="width:40px; height:40px; border-radius:50%; display:flex; justify-content:center; align-items:center; color:white;">➖</div></div>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
