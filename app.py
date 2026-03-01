import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Finance Tracker Pro", page_icon="💰", layout="wide")

# --- CSS (Design & Hover Effects) ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100% !important;
        height: 70px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        transition: 0.3s !important;
    }
    div.stButton > button:has(div:contains("Income")):hover { background-color: #d4edda !important; border-color: #28a745 !important; }
    div.stButton > button:has(div:contains("Expense")):hover { background-color: #f8d7da !important; border-color: #dc3545 !important; }
    
    .summary-card {
        background-color: white; padding: 15px; border-radius: 10px;
        border: 1px solid #eee; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

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
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- Top Navigation ---
st.title("💰 Finance Tracker Pro")
c1, c2, c3, c4 = st.columns(4)
if c1.button("➕\nIncome"): st.session_state.show_form = "Income"
if c2.button("➖\nExpense"): st.session_state.show_form = "Expense"
if c3.button("🔄\nTransfer"): st.session_state.show_form = "Transfer"
if c4.button("📊\nCharts"): st.session_state.show_form = "Charts"

st.write("---")

# --- 1. Data Entry Forms ---
if st.session_state.show_form in ["Income", "Expense", "Transfer"]:
    with st.container():
        st.subheader(f"Add {st.session_state.show_form}")
        with st.form("entry_form", clear_on_submit=True):
            d = st.date_input("Date", date.today())
            amt = st.number_input("Amount (LKR)", value=None, placeholder="0.00", min_value=0.0)
            
            if st.session_state.show_form == "Transfer":
                f_acc = st.selectbox("From Account", ["Cash", "Bank", "Card"])
                t_acc = st.selectbox("To Account", ["Bank", "Cash", "Card"])
                cat = "Transfer"
            else:
                cat = st.selectbox("Category", ["Food", "Salary", "Bills", "Travel", "Shopping", "Other"])
                f_acc, t_acc = "", ""

            note = st.text_input("Note")
            if st.form_submit_button("Save Record ✅"):
                if amt is not None and amt > 0:
                    ts = f"{d} {datetime.now().strftime('%H:%M:%S')}"
                    worksheet.append_row([ts, cat, amt, note, st.session_state.show_form, f_acc, t_acc])
                    st.success("Saved!"); st.session_state.show_form = None; st.rerun()
                else:
                    st.warning("Please enter a valid amount.")

# --- 2. Summary ---
if not df.empty:
    ti = df[df['Type'] == 'Income']['Amount'].sum()
    te = df[df['Type'] == 'Expense']['Amount'].sum()
    sc1, sc2, sc3 = st.columns(3)
    sc1.markdown(f'<div class="summary-card">Total Income<br><h3 style="color:green;">LKR {ti:,.0f}</h3></div>', unsafe_allow_html=True)
    sc2.markdown(f'<div class="summary-card">Total Expense<br><h3 style="color:red;">LKR {te:,.0f}</h3></div>', unsafe_allow_html=True)
    sc3.markdown(f'<div class="summary-card">Net Balance<br><h3>LKR {ti-te:,.0f}</h3></div>', unsafe_allow_html=True)

# --- History Header & Filtering ---
st.write("---")
st.subheader("📜 Recent Transactions")

if not df.empty:
    f_col1, f_col2 = st.columns(2)
    start_d = f_col1.date_input("Start Date", df['Date_Only'].min())
    end_d = f_col2.date_input("End Date", date.today())

    mask = (df['Date_Only'] >= start_d) & (df['Date_Only'] <= end_d)
    df['row_idx'] = range(2, len(df) + 2)
    filtered_df = df.loc[mask].iloc[::-1]

    if not filtered_df.empty:
        for idx, row in filtered_df.iterrows():
            col_data, col_del = st.columns([0.9, 0.1])
            
            # --- පාට වෙනස් කරන Inline Logic එක මෙන්න ---
            if row['Type'] == "Income":
                text_color = "#28a745" # Green
                mark = "+"
            elif row['Type'] == "Expense":
                text_color = "#dc3545" # Red
                mark = "-"
            else:
                text_color = "#ff8c00" # Orange for Transfer
                mark = "🔄"
            
            with col_data:
                # මෙතන කෙලින්ම style attribute එක පාවිච්චි කළා පාට ස්ථිර කරන්න
                st.markdown(f"""
                    <div style="background:white; padding:15px; border-radius:10px; border-left:8px solid {text_color}; margin-bottom:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <span style="float:right; font-weight:bold; color:{text_color}; font-size:20px;">
                            {mark} LKR {row['Amount']:,.0f}
                        </span>
                        <div style="font-size:12px; color:gray;">📅 {row['Date']}</div>
                        <div style="font-weight:bold; font-size:16px; color:#333;">{row['Category']}</div>
                        <div style="font-size:14px; color:#555;">{row['Description']}</div>
                        {f"<small style='color:orange;'>{row['From_Account']} ➡️ {row['To_Account']}</small>" if row['Type'] == 'Transfer' else ''}
                    </div>
                    """, unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️", key=f"del_{row['row_idx']}"):
                    worksheet.delete_rows(int(row['row_idx']))
                    st.success("Deleted!"); st.rerun()
    else:
        st.info("No records found.")
