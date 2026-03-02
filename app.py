import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CUSTOM CSS (Responsive Columns Fix) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    .header-bar {
        background-color: #0081C9; padding: 15px; color: white;
        text-align: center; font-size: 18px; font-weight: bold;
        margin: -60px -20px 20px -20px;
    }

    /* --- RESPONSIVE COLUMNS FIX --- */
    /* Mobile එකේදී බටන් 2 බැගින් පේළි 2කට ගන්න */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: wrap !important; /* මේකෙන් තමයි පල්ලෙහාට ගන්නේ */
        gap: 10px !important;
    }

    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 calc(50% - 10px) !important; /* Mobile: 50% width */
        min-width: calc(50% - 10px) !important;
    }

    /* Desktop එකේදී (800px+) බටන් 4ම එක පේළියට ගන්න */
    @media (min-width: 800px) {
        div[data-testid="stHorizontalBlock"] > div {
            flex: 1 1 0% !important;
            min-width: 0 !important;
        }
    }

    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        border-radius: 12px !important;
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        font-weight: bold !important;
        font-size: 14px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        white-space: pre-wrap !important;
    }
    
    div.stButton > button:hover {
        border-color: #0081C9 !important;
        background-color: #f0f8ff !important;
    }

    /* Summary Table & Floating Menu (Unchanged) */
    .summary-table { width: 100%; background: white; border-collapse: collapse; margin-top: 15px; border-radius: 12px; border: 1px solid #eee; overflow: hidden; }
    .summary-table td { padding: 12px; border: 1px solid #eee; text-align: center; }
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 99999 !important; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { width: 60px; height: 60px; background: #0081C9; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 35px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); cursor: pointer; }
    .fab-list { display: none; flex-direction: column; gap: 10px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 10px; }
    .fab-label { color: white; padding: 5px 12px; border-radius: 6px; font-size: 13px; font-weight: bold; background: rgba(0,0,0,0.7); }
    .fab-icon { width: 45px; height: 45px; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 18px; }
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
    st.error("Connection Error"); st.stop()

# --- MAIN BUTTON GRID ---
# Columns 4ක් දැම්මට Mobile එකේදී CSS එකෙන් මේවා 2x2 කරනවා
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("➕\nIncome", key="btn_inc"): st.session_state.show_form = "Income"
with col2:
    if st.button("➖\nExpense", key="btn_exp"): st.session_state.show_form = "Expense"
with col3:
    if st.button("🔄\nTransfer", key="btn_trf"): st.session_state.show_form = "Transfer"
with col4:
    if st.button("📜\nHistory", key="btn_his"): st.session_state.show_form = "History"

# --- DATA ENTRY FORM ---
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

# --- SUMMARY & TRANSACTIONS (කලින් විදිහමයි) ---
if not df.empty:
    ti = df[df['Type'] == 'Income']['Amount'].sum()
    te = df[df['Type'] == 'Expense']['Amount'].sum()
    bal = ti - te
    st.markdown(f"""
        <div style="text-align:center; font-size:12px; color:gray; margin-top:20px;">{date.today().strftime('%d %B %Y')}</div>
        <table class="summary-table">
            <tr>
                <td><span style="color:gray; font-size:11px;">Income</span><br><b style="color:green; font-size:16px;">{ti:,.0f}</b></td>
                <td><span style="color:gray; font-size:11px;">Expense</span><br><b style="color:red; font-size:16px;">{te:,.0f}</b></td>
                <td><span style="color:gray; font-size:11px;">Balance</span><br><b style="font-size:16px;">{bal:,.0f}</b></td>
            </tr>
            <tr style="background:#fcfcfc;"><td colspan="2" style="text-align:right; color:gray; font-size:12px;">Previous Balance</td><td style="color:green; font-weight:bold;">38,814.85</td></tr>
            <tr style="background:#e3f2fd; font-weight:bold;"><td colspan="2" style="text-align:right;">Total Cash</td><td style="color:green; font-size:15px;">{(38814.85 + bal):,.2f}</td></tr>
        </table>
    """, unsafe_allow_html=True)

# --- RECENT TRANSACTIONS ---
st.markdown("<br><b>Recent Transactions</b>", unsafe_allow_html=True)
if not df.empty:
    latest = df.iloc[::-1].head(10)
    for _, row in latest.iterrows():
        color = "#28a745" if row['Type'] == "Income" else "#dc3545"
        sym = "+" if row['Type'] == "Income" else "-"
        st.markdown(f"""
            <div style="background:white; padding:15px; border-radius:10px; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                <div>
                    <div style="font-size:11px; color:gray;">{row['Date']}</div>
                    <div style="font-weight:bold; font-size:14px; color:#333;">{row['Category']}</div>
                    <div style="font-size:10px; color:#0081C9; font-weight:bold;">BANK</div>
                </div>
                <div style="color:{color}; font-weight:bold; font-size:16px;">{sym} {row['Amount']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

# --- FLOATING MENU ---
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
