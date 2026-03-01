import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection
# --- පිටුවේ සැකසුම් (Page Config) ---
st.set_page_config(page_title="Smart Finance v1", page_icon="💰", layout="wide")

# --- මුරපදය පරීක්ෂාව (Login Logic) ---
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
            st.error("වැරදි මුරපදයක්! කරුණාකර නැවත උත්සාහ කරන්න.")
else:
    # ඔයාගේ Google Sheet URL එක
    url = "https://docs.google.com/spreadsheets/d/1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8/edit#gid=0"
    
    # සම්බන්ධතාවය ගොඩනැගීම (Secrets හරහා)
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=url, ttl=0)
    except Exception as e:
        st.error("Google Sheet එකට සම්බන්ධ විය නොහැක. කරුණාකර Secrets සහ Share Settings පරීක්ෂා කරන්න.")
        st.stop()

    st.title("💰 Smart Finance Tracker")
    
    # Tabs මගින් දත්ත ඇතුළත් කිරීම සහ බැලීම
    tab1, tab2 = st.tabs(["➕ අලුත් දත්ත", "📊 ඉතිහාසය"])

    with tab1:
        with st.form("add_data", clear_on_submit=True):
            col1, col2 = st.columns(2)
            t_type = col1.selectbox("වර්ගය", ["Expense", "Income"])
            t_amt = col2.number_input("මුදල (LKR)", min_value=0.0, step=100.0)
            t_cat = st.selectbox("ප්‍රවර්ගය", ["Food", "Travel", "Bills", "Rent", "Salary", "Other"])
            t_note = st.text_input("විස්තරය")
            
            if st.form_submit_button("Save to Cloud"):
                if t_amt > 0:
                    new_row = pd.DataFrame([[str(date.today()), t_cat, t_amt, t_note, t_type]], 
                                           columns=["Date", "Category", "Amount", "Description", "Type"])
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(spreadsheet=url, data=updated_df)
                    st.success("සාර්ථකව සුරැකුණා! ✅")
                    st.rerun()

    with tab2:
        if not df.empty:
            st.dataframe(df.iloc[::-1], use_container_width=True)
        else:
            st.info("දත්ත කිසිවක් නැත.")