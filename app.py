import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Finance Tracker Pro", page_icon="💰", layout="wide")

# --- CSS (Hover Colors & Layout) ---
st.markdown("""
    <style>
    /* බොත්තම් වල සාමාන්‍ය පෙනුම */
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        background-color: #f8f9fa !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        transition: 0.3s !important;
    }

    /* Income Hover - Green */
    div.stButton > button:has(div:contains("Income")):hover {
        background-color: #d4edda !important;
        border-color: #28a745 !important;
        color: #155724 !important;
    }

    /* Expense Hover - Red/Orange */
    div.stButton > button:has(div:contains("Expense")):hover {
        background-color: #f8d7da !important;
        border-color: #dc3545 !important;
        color: #721c24 !important;
    }

    .summary-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #eee;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

if "show_form" not in st.session_state:
    st.session_state.show_form = None

# --- Google Sheets Connection ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheetsheets"]["client_x509_cert_url"],
    }
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet = sh.worksheet("Sheet1")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    # Date column එක හරියට format කරගමු filter කරන්න ලේසි වෙන්න
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- UI Header ---
st.title("💰 Finance Tracker Pro")

c1, c2, c3, c4 = st.columns(4)
if c1.button("➕\nIncome"): st.session_state.show_form = "Income"
if c2.button("➖\nExpense"): st.session_state.show_form = "Expense"
if c3.button("🔄\nTransfer"): st.info("Coming Soon!")
if c4.button("📑\nHistory"): st.session_state.show_form = "History"

st.write("---")

# --- 1. Data Entry with Date Picker ---
if st.session_state.show_form in ["Income", "Expense"]:
    t_type = st.session_state.show_form
    with st.container():
        st.subheader(f"Add New {t_type}")
        with st.form("entry_form", clear_on_submit=True):
            # මෙතනින් පුළුවන් පරණ දිනයක් වුණත් තෝරන්න
            selected_date = st.date_input("Select Date", date.today())
            amt = st.number_input("Amount (LKR)", min_value=0.0, step=100.0)
            cat = st.selectbox("Category", ["Food", "Salary", "Bills", "Travel", "Medical", "Shopping", "Other"])
            note = st.text_input("Description")
            
            if st.form_submit_button("Save Record ✅"):
                if amt > 0:
                    # වෙලාවත් එක්කම Save කරනවා (නමුත් date එක ඔයා තෝරපු එක)
                    current_time = datetime.now().strftime("%H:%M:%S")
                    final_timestamp = f"{selected_date} {current_time}"
                    worksheet.append_row([final_timestamp, cat, amt, note, t_type])
                    st.success(f"Record added for {selected_date}!")
                    st.session_state.show_form = None
                    st.rerun()

# --- 2. Summary Section ---
if not df.empty:
    total_inc = df[df['Type'] == 'Income']['Amount'].sum()
    total_exp = df[df['Type'] == 'Expense']['Amount'].sum()
    
    sc1, sc2, sc3 = st.columns(3)
    sc1.markdown(f'<div class="summary-card"><p>Total Income</p><h2 style="color:green;">LKR {total_inc:,.0f}</h2></div>', unsafe_allow_html=True)
    sc2.markdown(f'<div class="summary-card"><p>Total Expense</p><h2 style="color:red;">LKR {total_exp:,.0f}</h2></div>', unsafe_allow_html=True)
    sc3.markdown(f'<div class="summary-card"><p>Net Balance</p><h2>LKR {total_inc - total_exp:,.0f}</h2></div>', unsafe_allow_html=True)

st.write("---")

# --- 3. Date Filtering & History ---
st.write("### 🔍 Filter & History")
if not df.empty:
    f_col1, f_col2 = st.columns(2)
    start_date = f_col1.date_input("Start Date", df['Date'].min())
    end_date = f_col2.date_input("End Date", date.today())

    # Filter දත්ත
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    filtered_df = df.loc[mask].iloc[::-1] # අලුත් ඒවා උඩට

    if not filtered_df.empty:
        for idx, row in filtered_df.iterrows():
            color = "#ff4b4b" if row['Type'] == "Expense" else "#28a745"
            st.markdown(f"""
                <div style="background-color:white; padding:15px; border-radius:10px; margin-bottom:10px; border-left: 8px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <span style="float:right; color:{color}; font-weight:bold; font-size:18px;">LKR {row['Amount']:,.0f}</span>
                    <div style="font-size:12px; color:gray;">📅 {row['Date']} | {row['Type']}</div>
                    <div style="font-weight:bold; font-size:16px;">{row['Category']}</div>
                    <div style="font-size:14px; color:#555;">{row['Description']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("තෝරාගත් කාලය ඇතුළත දත්ත කිසිවක් නැත.")
