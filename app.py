import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CSS (Image එකේ තියෙන විදිහටම Buttons හදන්න) ---
st.markdown("""
    <style>
    /* Main Background */
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

    /* Grid Layout for Buttons */
    .button-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        padding: 10px;
    }

    /* Custom Button Styling */
    .custom-btn {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        cursor: pointer;
        transition: 0.3s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .custom-btn:hover { background-color: #f1f1f1; border-color: #0081C9; }
    .btn-icon { font-size: 24px; margin-bottom: 5px; display: block; }
    .btn-text { font-size: 13px; font-weight: bold; color: #333; }

    /* Summary Table Styling */
    .summary-table {
        width: 100%;
        background: white;
        border-collapse: collapse;
        margin-top: 10px;
        font-size: 13px;
    }
    .summary-table td { padding: 12px; border: 1px solid #eee; text-align: center; }
    .label { color: gray; font-size: 11px; }

    /* Floating Action Button */
    .fab-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header-bar">Income Expense ⌄</div>', unsafe_allow_html=True)

if "show_form" not in st.session_state:
    st.session_state.show_form = None

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
        df['Date_Only'] = pd.to_datetime(df['Date'], format='mixed').dt.date
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except:
    st.error("Connection Lost"); st.stop()

# --- Custom Button Grid (Actionable Buttons) ---
# Streamlit බටන් පාවිච්චි කරන්නේ logic එකට විතරයි, පෙනුම columns වලින් හදනවා
c1, c2 = st.columns(2)
with c1:
    if st.button("➕ Add Income", use_container_width=True): st.session_state.show_form = "Income"
    if st.button("🔄 Transfer", use_container_width=True): st.session_state.show_form = "Transfer"
with c2:
    if st.button("➖ Add Expense", use_container_width=True): st.session_state.show_form = "Expense"
    if st.button("📊 Transactions", use_container_width=True): st.session_state.show_form = "History"

# --- Data Entry Form ---
if st.session_state.show_form in ["Income", "Expense", "Transfer"]:
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

# --- Summary Table (As per Image) ---
if not df.empty:
    ti = df[df['Type'] == 'Income']['Amount'].sum()
    te = df[df['Type'] == 'Expense']['Amount'].sum()
    bal = ti - te
    
    st.markdown(f"""
        <div style="text-align:center; font-size:12px; color:gray; margin-top:15px;">21-Feb-2026 -> 20-Mar-2026</div>
        <table class="summary-table">
            <tr>
                <td><span class="label">Income</span><br><b style="color:green;">{ti:,.0f}</b></td>
                <td><span class="label">Expense</span><br><b style="color:red;">{te:,.0f}</b></td>
                <td><span class="label">Balance</span><br><b>{bal:,.0f}</b></td>
            </tr>
            <tr>
                <td colspan="2" style="text-align:right; color:gray;">Previous Balance</td>
                <td style="color:green;">38,814.85</td>
            </tr>
            <tr style="background:#f0f8ff;">
                <td colspan="2" style="text-align:right; font-weight:bold;">Total Balance</td>
                <td style="color:green; font-weight:bold;">{(38814.85 + bal):,.2f}</td>
            </tr>
        </table>
    """, unsafe_allow_html=True)

# --- Recent Transactions List ---
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
                <div style="color:{color}; font-weight:bold; font-size:16px;">
                    {sym} {row['Amount']:,.0f}
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- Floating Action Button ---
st.markdown("""
    <div class="fab-container">
        <button style="background:#0081C9; color:white; border:none; width:55px; height:55px; border-radius:50%; font-size:30px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            +
        </button>
    </div>
""", unsafe_allow_html=True)
