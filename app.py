import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CSS (Main Buttons Grid + Floating Menu) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }

    /* Top Blue Header */
    .header-bar {
        background-color: #0081C9;
        padding: 15px;
        color: white;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin: -60px -20px 20px -20px;
    }

    /* Main Grid Buttons Styling */
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        border-radius: 12px !important;
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        font-weight: bold !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }

    /* Summary Table Fix */
    .summary-table {
        width: 100%;
        background: white;
        border-collapse: collapse;
        margin-top: 10px;
        font-size: 13px;
        border: 1px solid #eee;
    }
    .summary-table td { padding: 12px; border: 1px solid #eee; text-align: center; }

    /* --- FAB MENU LOGIC (CSS ONLY) --- */
    .fab-wrapper {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
    }
    .fab-main {
        width: 60px; height: 60px;
        background: #0081C9; border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        color: white; font-size: 35px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        cursor: pointer; transition: 0.3s;
    }
    .fab-list {
        position: absolute; bottom: 70px; right: 0;
        display: none; flex-direction: column; gap: 15px; align-items: flex-end;
    }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-wrapper:hover .fab-main { transform: rotate(45deg); background: #555; }

    .fab-item { display: flex; align-items: center; gap: 10px; }
    .fab-label {
        color: white; padding: 5px 12px; border-radius: 5px;
        font-size: 14px; font-weight: bold; white-space: nowrap;
    }
    .fab-icon {
        width: 45px; height: 45px; border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        color: white; font-size: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .bg-income { background-color: #28a745; }
    .bg-expense { background-color: #dc3545; }
    .bg-transfer { background-color: #fd7e14; }
    .bg-trans { background-color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header-bar">Income Expense ⌄</div>', unsafe_allow_html=True)

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

# --- 1. MAIN BUTTONS GRID (Uda tibuna ewa) ---
col1, col2 = st.columns(2)
with col1:
    if st.button("⊕ Add Income", key="btn_inc"): st.session_state.show_form = "Income"
    if st.button("🔄 Transfer", key="btn_trf"): st.session_state.show_form = "Transfer"
with col2:
    if st.button("⊖ Add Expense", key="btn_exp"): st.session_state.show_form = "Expense"
    if st.button("☰ History", key="btn_his"): st.session_state.show_form = "History"

# --- 2. DATA ENTRY FORM ---
if st.session_state.show_form in ["Income", "Expense", "Transfer"]:
    with st.form("entry_form", clear_on_submit=True):
        st.subheader(f"New {st.session_state.show_form}")
        d = st.date_input("Date", date.today())
        amt = st.number_input("Amount", value=None, placeholder="0.00")
        note = st.text_input("Note")
        if st.form_submit_button("Save Record ✅"):
            if amt:
                ts = f"{d} {datetime.now().strftime('%H:%M:%S')}"
                worksheet.append_row([ts, "General", amt, note, st.session_state.show_form, "", ""])
                st.session_state.show_form = None
                st.rerun()

# --- 3. SUMMARY TABLE ---
if not df.empty:
    ti = df[df['Type'] == 'Income']['Amount'].sum()
    te = df[df['Type'] == 'Expense']['Amount'].sum()
    bal = ti - te
    st.markdown(f"""
        <div style="text-align:center; font-size:12px; color:gray; margin-top:15px;">{date.today().strftime('%d-%b-%Y')}</div>
        <table class="summary-table">
            <tr>
                <td><span style="color:gray; font-size:11px;">Income</span><br><b style="color:green;">{ti:,.0f}</b></td>
                <td><span style="color:gray; font-size:11px;">Expense</span><br><b style="color:red;">{te:,.0f}</b></td>
                <td><span style="color:gray; font-size:11px;">Balance</span><br><b>{bal:,.0f}</b></td>
            </tr>
            <tr><td colspan="2" style="text-align:right; color:gray;">Previous Balance</td><td style="color:green;">38,814.85</td></tr>
            <tr style="font-weight:bold; background:#e3f2fd;"><td colspan="2" style="text-align:right;">Total Balance</td><td style="color:green;">{(38814.85 + bal):,.2f}</td></tr>
        </table>
    """, unsafe_allow_html=True)

# --- 4. TRANSACTION LIST ---
st.write("---")
if not df.empty:
    latest = df.iloc[::-1].head(10)
    for _, row in latest.iterrows():
        color = "red" if row['Type'] == "Expense" else "green"
        sym = "-" if row['Type'] == "Expense" else "+"
        st.markdown(f"""
            <div style="background:white; padding:12px; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:11px; color:gray;">{row['Date']}</div>
                    <div style="font-weight:bold; font-size:14px;">{row['Category']}</div>
                    <div style="font-size:10px; color:#0081C9; font-weight:bold;">BANK</div>
                </div>
                <div style="color:{color}; font-weight:bold; font-size:16px;">{sym} {row['Amount']:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

# --- 5. FLOATING MENU (CSS ONLY) ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-list">
            <div class="fab-item"><span class="fab-label bg-trans">Transactions</span><div class="fab-icon bg-trans">☰</div></div>
            <div class="fab-item"><span class="fab-label bg-transfer">Transfer</span><div class="fab-icon bg-transfer">⇄</div></div>
            <div class="fab-item"><span class="fab-label bg-income">Add Income</span><div class="fab-icon bg-income">⊕</div></div>
            <div class="fab-item"><span class="fab-label bg-expense">Add Expense</span><div class="fab-icon bg-expense">⊖</div></div>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
