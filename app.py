import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# --- Page Config (Mobile Optimization) ---
# Title: Income Expense Tracker
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- CUSTOM CSS (Classic image_0.png Style - අඟලටම) ---
st.markdown("""
    <style>
    /* මුළු App එකේම පසුබිම */
    .stApp { background-color: #f1f3f6; }
    
    /* උඩ නිල් පාට Header එක */
    .header-bar {
        background-color: #0081C9; padding: 15px; color: white;
        text-align: center; font-size: 20px; font-weight: bold;
        margin: -60px -20px 20px -20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    /* Tabs Styling (HOME, CALENDAR, NOTEBOOK) */
    div[data-testid="stMarkdownContainer"] ul { list-style: none; padding: 0; display: flex; justify-content: space-around; background: #fff; margin: -20px -20px 10px -20px; border-bottom: 2px solid #eee; }
    div[data-testid="stMarkdownContainer"] ul li { padding: 10px; font-weight: bold; color: gray; cursor: pointer; }
    div[data-testid="stMarkdownContainer"] ul li:first-child { color: #0081C9; border-bottom: 2px solid #0081C9; }

    /* Action Buttons (Add Income, etc.) */
    div.stButton > button {
        width: 100% !important; height: 110px !important;
        border-radius: 10px !important; background-color: white !important;
        color: #333 !important; border: 1px solid #ddd !important;
        font-weight: bold !important; font-size: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        margin-bottom: 15px !important;
    }
    div.stButton > button:hover { border-color: #0081C9 !important; background-color: #f0f8ff !important; }

    /* Summary Card Styling */
    .summary-card {
        background: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08); margin-bottom: 20px;
        text-align: center;
    }
    .summary-row { display: flex; justify-content: space-around; border-top: 1px solid #eee; padding-top: 10px; margin-top: 10px;}
    .sum-val { font-size: 18px; font-weight: bold; }
    .inc-val { color: green; } .exp-val { color: red; }
    .prev-bal { text-align: right; color: green; font-weight: bold; }
    .bal-row { text-align: right; color: green; font-weight: bold; font-size: 17px; background: #e3f2fd; padding: 10px; border-radius: 8px;}

    /* Transaction Card Style */
    .trans-card {
        background: white; padding: 15px; border-radius: 10px;
        margin-bottom: 10px; border-bottom: 1px solid #eee;
        display: flex; justify-content: space-between; align-items: center;
    }
    .bank-tag { background: #eee; padding: 2px 6px; border-radius: 4px; font-size: 11px; color: #555;}
    </style>
    """, unsafe_allow_html=True)

# --- App Header ---
st.markdown('<div class="header-bar">Income Expense ⌄</div>', unsafe_allow_html=True)

# Tabs
st.markdown("""<ul><li>HOME</li><li>CALENDAR</li><li>NOTEBOOK</li></ul>""", unsafe_allow_html=True)

if "show_form" not in st.session_state: st.session_state.show_form = None

# --- Connection (Google Sheets) ---
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

# --- 1. ACTION BUTTONS GRID (Classic Image_0.png Style) ---
# Columns 2 බැගින් ලස්සනට
col1, col2 = st.columns(2)
with col1:
    if st.button("⊕\nAdd Income", key="btn_inc"): st.session_state.show_form = "Income"
    if st.button("⇄\nTransfer", key="btn_trf"): st.session_state.show_form = "Transfer"
with col2:
    if st.button("⊖\nAdd Expense", key="btn_exp"): st.session_state.show_form = "Expense"
    if st.button("☰\nTransactions", key="btn_his"): st.session_state.show_form = "History"

# --- 2. DATA ENTRY FORM (Popup style expanser) ---
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

# --- 3. SUMMARY CARD (As in Image_0.png) ---
# Date period: 21-Feb-2026 -> 20-Mar-2026
# Previous balance and Balance: 38,814.85
st.markdown(f"""
    <div class="summary-card">
        <div style="font-size:13px; color:gray;">21-Feb-2026 -> 20-Mar-2026</div>
        <div class="summary-row">
            <div><span style="color:green;">Income</span><br><span class="inc-val">0</span></div>
            <div><span style="color:red;">Expense</span><br><span class="exp-val">0</span></div>
            <div><span>Balance</span><br><span class="sum-val">0</span></div>
        </div>
        <div style="text-align:right; color:gray; padding:10px 0;">Previous Balance <span class="prev-bal">38,814.85</span></div>
        <div class="bal-row">Balance <span style="font-size:18px;">38,814.85</span></div>
    </div>
""", unsafe_allow_html=True)

# --- 4. RECENT TRANSACTIONS LIST ---
st.write("<b>Recent Transactions</b>", unsafe_allow_html=True)
if not df.empty:
    latest = df.iloc[::-1].head(10)
    for _, row in latest.iterrows():
        color = "#d9534f" if row['Type'] == "Expense" else "#5cb85c"
        st.markdown(f"""
            <div class="trans-card">
                <div>
                    <div style="font-size:11px; color:gray;">{row['Date']}</div>
                    <div style="font-weight:bold; font-size:14px;">{row['Category']}</div>
                    <div class="bank-tag">BANK</div>
                </div>
                <div style="color:{color}; font-weight:bold; font-size:16px;">
                    {row['Amount']:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)
