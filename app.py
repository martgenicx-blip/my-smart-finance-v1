import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# --- පිටුවේ සැකසුම් ---
st.set_page_config(page_title="Smart Finance v1", page_icon="💰", layout="wide")

# --- Custom CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .delete-btn>button { background-color: #ff4b4b; color: white; border: none; }
    .delete-btn>button:hover { background-color: #ff3333; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- මුරපදය පරීක්ෂාව ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, col_mid, _ = st.columns([1, 1, 1])
    with col_mid:
        st.title("🔐 Login")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if pwd == "###1984***":
                st.session_state.auth = True
                st.rerun()
    st.stop()

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
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"],
    }
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet = sh.worksheet("Sheet1")
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- Dashboard ---
st.title("💰 Smart Finance Dashboard")

if not df.empty:
    total_inc = df[df['Type'] == 'Income']['Amount'].sum()
    total_exp = df[df['Type'] == 'Expense']['Amount'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Income", f"LKR {total_inc:,.2f}")
    m2.metric("Total Expense", f"LKR {total_exp:,.2f}")
    m3.metric("Balance", f"LKR {total_inc - total_exp:,.2f}")

st.divider()

tab1, tab2, tab3 = st.tabs(["➕ Add Entry", "📊 Analysis", "🗑️ Manage Data"])

with tab1:
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        t_type = c1.selectbox("Type", ["Expense", "Income"])
        t_amt = c2.number_input("Amount", min_value=0.0)
        t_cat = st.selectbox("Category", ["Food", "Travel", "Bills", "Salary", "Shopping", "Other"])
        t_note = st.text_input("Description")
        if st.form_submit_button("Save Entry"):
            worksheet.append_row([str(date.today()), t_cat, t_amt, t_note, t_type])
            st.success("Saved! ✅")
            st.rerun()

with tab2:
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            exp_df = df[df['Type'] == 'Expense']
            if not exp_df.empty:
                st.plotly_chart(px.pie(exp_df, values='Amount', names='Category', hole=0.4), use_container_width=True)
        with c2:
            st.plotly_chart(px.bar(df.groupby('Type')['Amount'].sum().reset_index(), x='Type', y='Amount', color='Type'), use_container_width=True)

with tab3:
    st.subheader("Delete Entries")
    if not df.empty:
        # පේළි අංකය සමඟ දත්ත පෙන්වමු
        display_df = df.copy()
        display_df['Row ID'] = range(2, len(df) + 2) # Google Sheet එකේ පේළි අංකය (Header එක නිසා +2)
        
        st.write("අන්තිමට ඇතුළත් කළ දත්ත (පහළින්ම තියෙන්නේ අලුත්ම එක):")
        st.dataframe(display_df.tail(10), use_container_width=True)
        
        row_to_delete = st.number_input("මකන්න ඕන පේළියේ Row ID එක ලබා දෙන්න", min_value=2, max_value=len(df)+1, step=1)
        
        st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
        if st.button(f"Delete Row {row_to_delete} Forever 🗑️"):
            worksheet.delete_rows(int(row_to_delete))
            st.warning(f"Row {row_to_delete} deleted!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("මකන්න දත්ත කිසිවක් නැත.")
