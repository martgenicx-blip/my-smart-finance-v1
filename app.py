import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Smart Finance v1", page_icon="💰")

# --- Login Logic ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login")
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if pwd == "###1984***":
            st.session_state.auth = True
            st.rerun()
else:
    # --- Google Sheets Connection (Direct via gspread) ---
    try:
        # Secrets වලින් දත්ත කියවීම
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
        
        # Sheet ID එක Secrets වලින් හෝ මෙතන කෙලින්ම දෙන්න
        sheet_id = "1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8"
        sh = client.open_by_key(sheet_id)
        worksheet = sh.worksheet("Sheet1") # Sheet එකේ නම Sheet1 විය යුතුයි
        
        # Data කියවීම
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        st.stop()

    st.title("💰 Smart Finance Tracker")
    tab1, tab2 = st.tabs(["➕ Add Data", "📊 History"])

    with tab1:
        with st.form("add_form", clear_on_submit=True):
            t_type = st.selectbox("Type", ["Expense", "Income"])
            t_amt = st.number_input("Amount", min_value=0.0)
            t_cat = st.selectbox("Category", ["Food", "Travel", "Bills", "Salary", "Other"])
            t_note = st.text_input("Description")
            
            if st.form_submit_button("Save"):
                new_row = [str(date.today()), t_cat, t_amt, t_note, t_type]
                worksheet.append_row(new_row)
                st.success("Saved! ✅")
                st.rerun()

    with tab2:
        if not df.empty:
            st.dataframe(df.iloc[::-1], use_container_width=True)
