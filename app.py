import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CUSTOM CSS (Mobile & Desktop Responsive Design) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Header Bar */
    .header-bar {
        background-color: #0081C9;
        padding: 15px;
        color: white;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin: -60px -20px 20px -20px;
    }

    /* --- GRID LOGIC --- */
    /* Mobile එකේදී 2x2 Grid එකක් පේන්න */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
    }
    
    [data-testid="stHorizontalBlock"] > div {
        flex: 1 1 calc(50% - 10px) !important; /* Mobile එකේදී බාගයක් ගන්න */
        min-width: calc(50% - 10px) !important;
    }

    /* Desktop එකේදී (800px ට වැඩි Screen) පේළියට පේන්න */
    @media (min-width: 800px) {
        [data-testid="stHorizontalBlock"] > div {
            flex: 1 1 0% !important;
            min-width: 0 !important;
        }
    }

    /* Button Styling */
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        border-radius: 12px !important;
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #eee !important;
        font-weight: bold !important;
        font-size: 14px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }

    /* Summary Table */
    .summary-table {
        width: 100%;
        background: white;
        border-collapse: collapse;
        margin-top: 10px;
        border-radius: 8px;
        border: 1px solid #eee;
        overflow: hidden;
    }
    .summary-table td { padding: 10px; border: 1px solid #eee; text-align: center; font-size: 13px; }

    /* --- FLOATING ACTION BUTTON (Image Style) --- */
    .fab-wrapper {
        position: fixed;
        bottom: 30px;
        right: 25px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 15px;
    }
    .fab-main {
        width: 55px; height: 55px;
        background: #0081C9; border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        color: white; font-size: 30px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        cursor: pointer;
        transition: transform 0.3s;
    }
    .fab-list {
        display: none;
        flex-direction: column;
        gap: 12px;
        align-items: flex-end;
    }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-wrapper:hover .fab-main { transform: rotate(45deg); background: #0073b3; }

    .fab-item { display: flex; align-items: center; gap: 10px; }
    .fab-label {
        color: white; padding: 4px 10px; border-radius: 5px;
        font-size: 12px; font-weight: bold; white-space: nowrap;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .fab-icon {
        width: 45px; height: 45px; border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        color: white; font-size: 18px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .bg-income { background-color: #5cb85c; }
    .bg-expense { background-color: #d9534f; }
    .bg-transfer { background-color: #f0ad4e; }
    .bg-trans { background-color: #5bc0de; }
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
    st.error("Connection Error"); st.stop()

# --- 1. RESPONSIVE BUTTON GRID (Income, Expense, Transfer, Transactions) ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("➕ Income"): st.session_state.show_form = "Income"
with col2:
    if st.button("➖ Expense"): st.session_state.show_form = "Expense"
with col3:
    if st.button("🔄 Transfer"): st.session_state.show_form = "Transfer"
with col4:
    if st.button("📜 Transactions"): st.session_state.show_form = "History"

# --- 2. DATA ENTRY FORM ---
if st.session_state.show_form in ["Income", "Expense", "Transfer"]:
    st.write("---")
    with st.form("entry_form", clear_on_submit=True):
        st.subheader(f"New {st.session_state.show_form}")
        d = st.date_input("Date", date.today())
        amt = st.number_input("Amount", value=None, placeholder="0.00")
        note = st.text_input("Note")
        if st.form_submit_button("Save Record"):
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
                <td><span style="color:green;">Income</span><br><b>{ti:,.0f}</b></td>
                <td><span style="color:red;">Expense</span><br><b>{te:,.0f}</b></td>
                <td><span>Balance</span><br><b>{bal:,.0f}</b></td>
            </tr>
            <tr style="background:#f9f9f9;"><td colspan="2" style="text-align:right; color:gray;">Previous Balance</td><td style="color:green;">38,814.85</td></tr>
            <tr style="background:#e3f2fd; font-weight:bold;"><td colspan="2" style="text-align:right;">Total Balance</td><td style="color:green;">{(38814.85 + bal):,.2f}</td></tr>
        </table>
    """, unsafe_allow_html=True)

# --- 4. RECENT TRANSACTIONS ---
st.write("<br><b>Recent Transactions</b>", unsafe_allow_html=True)
if not df.empty:
    latest = df.iloc[::-1].head(8)
    for _, row in latest.iterrows():
        color = "#d9534f" if row['Type'] == "Expense" else "#5cb85c"
        st.markdown(f"""
            <div style="background:white; padding:12px; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:11px; color:gray;">{row['Date']}</div>
                    <div style="font-weight:bold; font-size:14px;">{row['Category']}</div>
                    <div style="font-size:10px; color:#0081C9; font-weight:bold;">BANK</div>
                </div>
                <div style="color:{color}; font-weight:bold; font-size:16px;">{row['Amount']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

# --- 5. FLOATING ACTION MENU (Mobile Image Style) ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-list">
            <div class="fab-item"><span class="fab-label bg-trans">Transactions</span><div class="fab-icon bg-trans">📜</div></div>
            <div class="fab-item"><span class="fab-label bg-transfer">Transfer</span><div class="fab-icon bg-transfer">🔄</div></div>
            <div class="fab-item"><span class="fab-label bg-income">Add Income</span><div class="fab-icon bg-income">➕</div></div>
            <div class="fab-item"><span class="fab-label bg-expense">Add Expense</span><div class="fab-icon bg-expense">➖</div></div>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
