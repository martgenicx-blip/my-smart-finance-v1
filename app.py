import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CSS (හරියටම image_2.png එකේ විදිහටම Floating Menu එක) ---
st.markdown("""
    <style>
    /* Main App Background */
    .stApp { background-color: #f8f9fa; }

    /* Blue Header Bar */
    .header-bar {
        background-color: #0081C9;
        padding: 15px;
        color: white;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin: -60px -20px 20px -20px;
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
    .label { color: gray; font-size: 11px; }

    /* --- FAB MENU LOGIC (CSS ONLY) --- */
    .fab-wrapper {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
    }

    .fab-main {
        width: 60px;
        height: 60px;
        background: #0081C9;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        font-size: 35px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        cursor: pointer;
        transition: transform 0.3s;
    }

    /* Menu Items Container */
    .fab-list {
        position: absolute;
        bottom: 70px;
        right: 0;
        display: none; /* Default Hidden */
        flex-direction: column;
        gap: 15px;
        align-items: flex-end;
    }

    /* Show menu when wrapper is hovered/clicked */
    .fab-wrapper:hover .fab-list {
        display: flex;
    }
    .fab-wrapper:hover .fab-main {
        transform: rotate(45deg); /* Plus becomes X */
        background: #555;
    }

    .fab-item {
        display: flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
    }

    .fab-label {
        color: white;
        padding: 5px 12px;
        border-radius: 5px;
        font-size: 14px;
        font-weight: bold;
        white-space: nowrap;
    }

    .fab-icon {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        font-size: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    /* Colors from Image_2 */
    .bg-income { background-color: #28a745; }
    .bg-expense { background-color: #dc3545; }
    .bg-transfer { background-color: #fd7e14; }
    .bg-trans { background-color: #007bff; }

    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header-bar">Income Expense ⌄</div>', unsafe_allow_html=True)

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

# --- Summary Table ---
if not df.empty:
    ti = df[df['Type'] == 'Income']['Amount'].sum()
    te = df[df['Type'] == 'Expense']['Amount'].sum()
    bal = ti - te
    st.markdown(f"""
        <div style="text-align:center; font-size:12px; color:gray; margin-top:10px;">{date.today().strftime('%d-%b-%Y')}</div>
        <table class="summary-table">
            <tr>
                <td><span class="label">Income</span><br><b style="color:green;">{ti:,.0f}</b></td>
                <td><span class="label">Expense</span><br><b style="color:red;">{te:,.0f}</b></td>
                <td><span class="label">Balance</span><br><b>{bal:,.0f}</b></td>
            </tr>
            <tr><td colspan="2" style="text-align:right; color:gray;">Previous Balance</td><td style="color:green;">38,814.85</td></tr>
            <tr style="font-weight:bold; background:#e3f2fd;"><td colspan="2" style="text-align:right;">Total Balance</td><td style="color:green;">{(38814.85 + bal):,.2f}</td></tr>
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
                <div style="color:{color}; font-weight:bold; font-size:16px;">{sym} {row['Amount']:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

# --- CSS Floating Menu HTML ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-list">
            <div class="fab-item">
                <span class="fab-label bg-trans">Transactions</span>
                <div class="fab-icon bg-trans">☰</div>
            </div>
            <div class="fab-item">
                <span class="fab-label bg-transfer">Transfer</span>
                <div class="fab-icon bg-transfer">⇄</div>
            </div>
            <div class="fab-item">
                <span class="fab-label bg-income">Add Income</span>
                <div class="fab-icon bg-income">⊕</div>
            </div>
            <div class="fab-item">
                <span class="fab-label bg-expense">Add Expense</span>
                <div class="fab-icon bg-expense">⊖</div>
            </div>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)

# --- Forms Section ---
st.write("---")
with st.expander("📝 Quick Entry Form"):
    t_type = st.selectbox("Type", ["Income", "Expense", "Transfer"])
    amt = st.number_input("Amount (LKR)", value=None, placeholder="0.00")
    note = st.text_input("Note")
    if st.button("Save Record ✅"):
        if amt:
            ts = f"{date.today()} {datetime.now().strftime('%H:%M:%S')}"
            worksheet.append_row([ts, "General", amt, note, t_type, "", ""])
            st.success("Saved!"); st.rerun()
