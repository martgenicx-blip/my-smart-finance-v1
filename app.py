import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CUSTOM CSS (Image එකේ තියෙන Floating Menu එක හදන්න) ---
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

    /* Summary Table Styling */
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

    /* --- Floating Action Button & Menu (Image_2 Style) --- */
    .fab-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 10px;
    }

    /* The Main Blue Button */
    .fab-main {
        background-color: #0081C9;
        color: white;
        border: none;
        width: 55px;
        height: 55px;
        border-radius: 50%;
        font-size: 30px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* The Floating Menu Items (Labels + Icons) */
    .fab-item-container {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Small Floating Icon Buttons */
    .fab-item-icon {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        border: none;
        color: white;
        font-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        cursor: pointer;
    }

    /* Item Labels (Background colors match Image_2) */
    .fab-label {
        padding: 5px 10px;
        border-radius: 5px;
        color: white;
        font-size: 13px;
        font-weight: bold;
    }

    /* Color definitions from image_2.png */
    .bg-income { background-color: #28a745; }
    .bg-expense { background-color: #dc3545; }
    .bg-transfer { background-color: #fd7e14; }
    .bg-trans { background-color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header-bar">Income Expense ⌄</div>', unsafe_allow_html=True)

# Session State for Menu and Forms
if "menu_open" not in st.session_state: st.session_state.menu_open = False
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
    st.error("Connection Lost"); st.stop()

# --- Summary Table ---
if not df.empty:
    ti = df[df['Type'] == 'Income']['Amount'].sum()
    te = df[df['Type'] == 'Expense']['Amount'].sum()
    bal = ti - te
    st.markdown(f"""
        <div style="text-align:center; font-size:12px; color:gray; margin-top:10px;">21-Feb-2026 -> 20-Mar-2026</div>
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
            <tr style="font-weight:bold; background:#e3f2fd;">
                <td colspan="2" style="text-align:right;">Total Balance</td>
                <td style="color:green;">{(38814.85 + bal):,.2f}</td>
            </tr>
        </table>
    """, unsafe_allow_html=True)

# --- Data Entry Form ---
if st.session_state.show_form:
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
                st.session_state.menu_open = False
                st.rerun()

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

# --- Dynamic Floating Menu Logic (Image_2 Style) ---
fab_html = '<div class="fab-container">'

if st.session_state.menu_open:
    # 1. Transactions Item (Blue)
    fab_html += f'<div class="fab-item-container"><span class="fab-label bg-trans">Transactions</span><button class="fab-item-icon bg-trans" onclick="document.getElementById(\'trans_trigger\').click()">☰</button></div>'
    # 2. Transfer Item (Orange)
    fab_html += f'<div class="fab-item-container"><span class="fab-label bg-transfer">Transfer</span><button class="fab-item-icon bg-transfer" onclick="document.getElementById(\'transfer_trigger\').click()">⇄</button></div>'
    # 3. Add Income Item (Green)
    fab_html += f'<div class="fab-item-container"><span class="fab-label bg-income">Add Income</span><button class="fab-item-icon bg-income" onclick="document.getElementById(\'income_trigger\').click()">⊕</button></div>'
    # 4. Add Expense Item (Red)
    fab_html += f'<div class="fab-item-container"><span class="fab-label bg-expense">Add Expense</span><button class="fab-item-icon bg-expense" onclick="document.getElementById(\'expense_trigger\').click()">⊖</button></div>'
    
    # The Close Button (X)
    main_btn_content = 'X'
else:
    # The Open Button (+)
    main_btn_content = '+'

fab_html += f'<button class="fab-main">{main_btn_content}</button></div>'

# Render the FAB and Menu
st.markdown(fab_html, unsafe_allow_html=True)

# Invisible Streamlit buttons to handle clicks from the HTML menu
col_triggers = st.columns(5)
with col_triggers[0]: 
    if st.button("income_trigger", key="income_trigger"): 
        st.session_state.show_form = "Income"
        st.rerun()
with col_triggers[1]:
    if st.button("expense_trigger", key="expense_trigger"):
        st.session_state.show_form = "Expense"
        st.rerun()
with col_triggers[2]:
    if st.button("transfer_trigger", key="transfer_trigger"):
        st.session_state.show_form = "Transfer"
        st.rerun()
with col_triggers[3]:
    if st.button("trans_trigger", key="trans_trigger"):
        st.session_state.show_form = "History"
        st.rerun()
with col_triggers[4]:
    # Hidden button to toggle the main menu
    if st.button("Toggle Menu", key="main_fab_trigger"):
        st.session_state.menu_open = not st.session_state.menu_open
        st.rerun()

# CSS to hide the invisible trigger buttons
st.markdown("<style>#income_trigger, #expense_trigger, #transfer_trigger, #trans_trigger, #main_fab_trigger { display: none; }</style>", unsafe_allow_html=True)
