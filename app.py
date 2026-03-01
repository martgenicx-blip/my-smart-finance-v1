import streamlit as st
import pandas as pd
from datetime import date
from st_gsheets_connection import GSheetsConnection

# Page Setup
st.set_page_config(page_title="Smart Finance v1", page_icon="💰", layout="wide")

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login to Pocket Finance")
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if pwd == "###1984***":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("වැරදි මුරපදයක්!")
else:
    # Google Sheet URL
    url = "https://docs.google.com/spreadsheets/d/1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8/edit#gid=0"
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=url, ttl=0)
    except Exception as e:
        st.error("Google Sheet එකට සම්බන්ධ විය නොහැක.")
        st.stop()

    st.title("💰 Smart Finance Tracker")
    
    # Form to add data
    with st.form("add_data", clear_on_submit=True):
        col1, col2 = st.columns(2)
        t_type = col1.selectbox("Type", ["Expense", "Income"])
        t_amt = col2.number_input("Amount (LKR)", min_value=0.0)
        t_cat = st.selectbox("Category", ["Food", "Travel", "Bills", "Rent", "Salary", "Other"])
        t_note = st.text_input("Description")
        
        if st.form_submit_button("Save Data"):
            if t_amt > 0:
                new_data = pd.DataFrame([[str(date.today()), t_cat, t_amt, t_note, t_type]], 
                                       columns=["Date", "Category", "Amount", "Description", "Type"])
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(spreadsheet=url, data=updated_df)
                st.success("සාර්ථකව සුරැකුණා! ✅")
                st.rerun()

    st.divider()
    st.subheader("Recent Transactions")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)