import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CUSTOM CSS (Image එකේ තියෙන විදිහටම Design එක) ---
st.markdown("""
    <style>
    /* Top Header Bar */
    .header-bar {
        background-color: #0081C9;
        padding: 10px;
        color: white;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        margin: -60px -20px 20px -20px;
    }
    
    /* Main Navigation Tabs style */
    .nav-tabs {
        display: flex;
        justify-content: space-around;
        background-color: #f8f9fa;
        padding: 10px 0;
        border-bottom: 2px solid #0081C9;
        margin-bottom: 20px;
    }

    /* Action Buttons (Grid) */
    .stButton > button {
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        border-radius: 8px !important;
        height: 100px !important;
        font-weight: bold !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    
    /* Summary Table style */
    .summary-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        margin-bottom: 20px;
        border: 1px solid #ddd;
    }
    .summary-table td {
        padding: 10px;
        border: 1px solid #eee;
        text-align: center;
    }

    /* Transaction Card */
    .trans-card {
        background: white;
        padding: 12px;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Floating Action Button style */
    .fab {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background-color: #0081C9;
        color: white;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        text-align: center;
        line-height: 60px;
        font-size: 30px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        z-index: 999;
        cursor: pointer;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- App Header ---
st.markdown('<div class="header-bar">Income Expense ⌄</div>', unsafe_allow_html=True)
st.markdown('<div class="nav-tabs"><b>HOME</b> <span>CALENDAR</span> <span>NOTEBOOK</span> </div>', unsafe_allow_html=True)

if "show_form" not in st.session_state:
    st.session_state.show_form = None

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
except Exception as e:
    st.error("Connection Error"); st.stop()

# --- Main Grid Buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("⊕\nAdd Income"): st.session_state.show_form = "Income"
    if st.button("⇄\nTransfer"): st.session_state.show_form = "Transfer"
with col2:
    if st.button("⊖\nAdd Expense"): st.session_state.show_form = "Expense"
    if st.button("☰\nTransactions"): st.session_state.show_form = "History"

st.write("---")

# --- Date Range & Summary Table ---
if not df.empty:
    ti = df[df['Type'] == 'Income']['Amount'].sum()
    te = df[df['Type'] == 'Expense']['Amount'].sum()
    bal = ti - te
    
    st.markdown(f"""
        <div style="text-align:center; font-size:14px; margin-bottom:5px;">21-Feb-2026 -> 20-Mar-2026</div>
        <table class="summary-table">
            <tr style="color:gray; font-size:12px;">
                <td style="color:green;">Income</td><td style="color:red;">Expense</td><td>Balance</td>
            </tr>
            <tr style="font-weight:bold;">
                <td>{ti:,.0f}</td><td>{te:,.0f}</td><td>{bal:,.0f}</td>
            </tr>
            <tr style="font-size:13px;">
                <td colspan="2" style="text-align:right;">Previous Balance</td><td style="color:green;">38,814.85</td>
            </tr>
            <tr style="font-weight:bold;">
                <td colspan="2" style="text-align:right;">Balance</td><td style="color:green;">{38814.85 + bal:,.2f}</td>
            </tr>
        </table>
    """, unsafe_allow_html=True)

# --- Form Section ---
if st.session_state.show_form in ["Income", "Expense", "Transfer"]:
    with st.form("entry_form", clear_on_submit=True):
        st.subheader(f"New {st.session_state.show_form}")
        d = st.date_input("Date", date.today())
        amt = st.number_input("Amount", value=None, placeholder="0.00")
        note = st.text_input("Note")
        if st.form_submit_button("Save ✅"):
            if amt:
                ts = f"{d} {datetime.now().strftime('%H:%M:%S')}"
                worksheet.append_row([ts, "General", amt, note, st.session_state.show_form, "", ""])
                st.rerun()

# --- Recent Transactions List ---
st.markdown("<b>Recent Transactions</b>", unsafe_allow_html=True)
if not df.empty:
    latest = df.iloc[::-1].head(10)
    for _, row in latest.iterrows():
        color = "red" if row['Type'] == "Expense" else "green"
        st.markdown(f"""
            <div class="trans-card">
                <div>
                    <div style="font-size:12px; color:gray;">{row['Date']}</div>
                    <div style="font-weight:bold;">{row['Category']}</div>
                    <div style="font-size:11px; background:#eee; display:inline-block; padding:0 5px; border-radius:3px;">Bank</div>
                </div>
                <div style="color:{color}; font-weight:bold; font-size:18px;">
                    {row['Amount']:,.0f}
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- Floating Action Button (FAB) ---
if st.button("+", key="fab_btn"):
    st.session_state.show_form = "Expense"
    st.rerun()
