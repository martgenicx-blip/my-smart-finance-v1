import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Finance Tracker Ultra", page_icon="💰", layout="wide")

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
    div.stButton > button:has(div:contains("Transfer")):hover { background-color: #fff3cd !important; border-color: #ffc107 !important; }
    
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
st.title("💰 Finance Tracker Ultra")
c1, c2, c3, c4 = st.columns(4)
if c1.button("➕\nIncome"): st.session_state.show_form = "Income"
if c2.button("➖\nExpense"): st.session_state.show_form = "Expense"
if c3.button("🔄\nTransfer"): st.session_state.show_form = "Transfer"
if c4.button("📊\nCharts"): st.session_state.show_form = "Charts"

# --- 1. Data Entry Forms ---
if st.session_state.show_form in ["Income", "Expense", "Transfer"]:
    with st.container():
        st.subheader(f"New {st.session_state.show_form}")
        with st.form("entry_form", clear_on_submit=True):
            d = st.date_input("Date", date.today())
            amt = st.number_input("Amount", min_value=0.0)
            
            if st.session_state.show_form == "Transfer":
                f_acc = st.selectbox("From Account", ["Cash", "Bank", "Card"])
                t_acc = st.selectbox("To Account", ["Bank", "Cash", "Card"])
                cat = "Transfer"
            else:
                cat = st.selectbox("Category", ["Food", "Salary", "Bills", "Travel", "Shopping", "Other"])
                f_acc, t_acc = "", ""

            note = st.text_input("Note")
            if st.form_submit_button("Save ✅"):
                ts = f"{d} {datetime.now().strftime('%H:%M:%S')}"
                worksheet.append_row([ts, cat, amt, note, st.session_state.show_form, f_acc, t_acc])
                st.success("Saved!"); st.session_state.show_form = None; st.rerun()

# --- 2. Summary ---
if not df.empty:
    ti = df[df['Type'] == 'Income']['Amount'].sum()
    te = df[df['Type'] == 'Expense']['Amount'].sum()
    sc1, sc2, sc3 = st.columns(3)
    sc1.markdown(f'<div class="summary-card">Income<br><h3 style="color:green;">{ti:,.0f}</h3></div>', unsafe_allow_html=True)
    sc2.markdown(f'<div class="summary-card">Expense<br><h3 style="color:red;">{te:,.0f}</h3></div>', unsafe_allow_html=True)
    sc3.markdown(f'<div class="summary-card">Balance<br><h3>{ti-te:,.0f}</h3></div>', unsafe_allow_html=True)

# --- 3. Charts ---
if st.session_state.show_form == "Charts" and not df.empty:
    st.write("---")
    st.subheader("Visual Analysis")
    ch1, ch2 = st.columns(2)
    exp_df = df[df['Type'] == 'Expense']
    if not exp_df.empty:
        ch1.plotly_chart(px.pie(exp_df, values='Amount', names='Category', title="Expenses by Category"), use_container_width=True)
    
    daily = df.groupby('Date_Only')['Amount'].sum().reset_index()
    ch2.plotly_chart(px.line(daily, x='Date_Only', y='Amount', title="Daily Spending Trend"), use_container_width=True)

# --- 4. History with Delete ---
st.write("---")
st.subheader("📜 Recent Transactions")
if not df.empty:
    # Google Sheet එකේ row index එක හොයාගන්න ID එකක් දාමු
    df['row_idx'] = range(2, len(df) + 2)
    display_df = df.iloc[::-1].head(15)
    
    for _, row in display_df.iterrows():
        col1, col2 = st.columns([0.9, 0.1])
        color = "green" if row['Type'] == "Income" else "red" if row['Type'] == "Expense" else "orange"
        
        with col1:
            st.markdown(f"""
                <div style="background:white; padding:10px; border-radius:8px; border-left:6px solid {color}; margin-bottom:5px;">
                    <span style="float:right; font-weight:bold; color:{color};">{row['Amount']:,.0f}</span>
                    <small>{row['Date']}</small><br><b>{row['Category']}</b> - {row['Description']}
                    {f" <br><small>({row['From_Account']} ➡️ {row['To_Account']})</small>" if row['Type'] == 'Transfer' else ''}
                </div>
                """, unsafe_allow_html=True)
        with col2:
            if st.button("🗑️", key=f"del_{row['row_idx']}"):
                worksheet.delete_rows(int(row['row_idx']))
                st.success("Deleted!"); st.rerun()
