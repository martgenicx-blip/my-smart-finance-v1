import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# --- පිටුවේ සැකසුම් ---
st.set_page_config(page_title="Smart Finance v1", page_icon="💰", layout="wide")

# --- Custom CSS (ලස්සන කරන්න සහ බොත්තම් වල පාට වෙනස් කරන්න) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3.5em; transition: 0.3s; }
    /* Income Button - Green */
    div.stButton > button:first-child[aria-label*="Income"] {
        background-color: #2ecc71; color: white; border: none;
    }
    /* Expense Button - Orange */
    div.stButton > button:first-child[aria-label*="Expense"] {
        background-color: #e67e22; color: white; border: none;
    }
    .record-box { padding: 10px; border-bottom: 1px solid #ddd; }
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
        if st.button("Login 🚀"):
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

# --- Dashboard Content ---
st.title("💰 Smart Finance Tracker")

if not df.empty:
    total_inc = df[df['Type'] == 'Income']['Amount'].sum()
    total_exp = df[df['Type'] == 'Expense']['Amount'].sum()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Income", f"LKR {total_inc:,.2f}")
    m2.metric("Total Expense", f"LKR {total_exp:,.2f}")
    m3.metric("Balance", f"LKR {total_inc - total_exp:,.2f}")

st.divider()

tab1, tab2, tab3 = st.tabs(["➕ Add Entry", "📊 Analysis", "📜 History & Delete"])

with tab1:
    st.subheader("Add New Transaction")
    with st.container():
        c_amt, c_cat = st.columns(2)
        t_amt = c_amt.number_input("Amount (LKR)", min_value=0.0, step=100.0)
        t_cat = c_cat.selectbox("Category", ["Food", "Travel", "Bills", "Salary", "Shopping", "Other"])
        t_note = st.text_input("Description (Optional)")
        
        st.write("Save as:")
        btn_inc, btn_exp = st.columns(2)
        
        # Income Button (Green + Plus)
        if btn_inc.button("➕ Save as Income"):
            if t_amt > 0:
                worksheet.append_row([str(date.today()), t_cat, t_amt, t_note, "Income"])
                st.success("Income Saved! 💸")
                st.rerun()
            else: st.warning("කරුණාකර මුදලක් ඇතුළත් කරන්න.")

        # Expense Button (Orange + Minus)
        if btn_exp.button("➖ Save as Expense"):
            if t_amt > 0:
                worksheet.append_row([str(date.today()), t_cat, t_amt, t_note, "Expense"])
                st.error("Expense Saved! 📉")
                st.rerun()
            else: st.warning("කරුණාකර මුදලක් ඇතුළත් කරන්න.")

with tab2:
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Expense Distribution")
            exp_df = df[df['Type'] == 'Expense']
            if not exp_df.empty:
                st.plotly_chart(px.pie(exp_df, values='Amount', names='Category', hole=0.4), use_container_width=True)
        with c2:
            st.subheader("Income vs Expense")
            sum_df = df.groupby('Type')['Amount'].sum().reset_index()
            st.plotly_chart(px.bar(sum_df, x='Type', y='Amount', color='Type', color_discrete_map={"Income": "#2ecc71", "Expense": "#e67e22"}), use_container_width=True)

with tab3:
    st.subheader("History & Delete")
    if not df.empty:
        display_df = df.copy()
        display_df['Row_ID'] = range(2, len(df) + 2)
        display_df = display_df.iloc[::-1]

        for idx, row in display_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1.5, 2.5, 1])
            icon = "➕" if row['Type'] == "Income" else "➖"
            color = "green" if row['Type'] == "Income" else "orange"
            
            col1.write(f"📅 {row['Date']}")
            col2.write(f"🏷️ {row['Category']}")
            col3.markdown(f"<span style='color:{color}; font-weight:bold;'>{icon} {row['Amount']}</span>", unsafe_allow_html=True)
            col4.write(f"📝 {row['Description']}")
            
            if col5.button("🗑️", key=f"del_{row['Row_ID']}"):
                worksheet.delete_rows(int(row['Row_ID']))
                st.rerun()
            st.divider()
