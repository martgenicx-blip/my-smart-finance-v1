import streamlit as st
import pandas as pd
from datetime import date
from st_gsheets_connection import GSheetsConnection

# --- පිටුවේ සැකසුම් (Page Config) ---
st.set_page_config(page_title="Smart Finance v1", page_icon="💰", layout="wide")

# --- මුරපදය පරීක්ෂාව (Login Logic) ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login to Pocket Finance")
    # මෙතන තමයි ඔයාගේ Password එක තියෙන්නේ
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if pwd == "###1984***":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("වැරදි මුරපදයක්! කරුණාකර නැවත උත්සාහ කරන්න.")
else:
    # --- Google Sheet සම්බන්ධතාවය ---
    try:
        # Secrets වල ඇති විස්තර ඇසුරින් සම්බන්ධ වේ
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # දත්ත කියවීම (ttl=0 කියන්නේ cache නොකර අලුත්ම දත්ත ගන්න කියන එකයි)
        df = conn.read(ttl=0)
        
    except Exception as e:
        st.error(f"❌ Google Sheet එකට සම්බන්ධ විය නොහැක: {e}")
        st.info("කරුණාකර Secrets වල spreadsheet ID එක සහ Google Sheet Share settings පරීක්ෂා කරන්න.")
        st.stop()

    st.title("💰 Smart Finance Tracker")
    
    # Tabs මගින් දත්ත ඇතුළත් කිරීම සහ බැලීම
    tab1, tab2 = st.tabs(["➕ අලුත් දත්ත", "📊 ඉතිහාසය"])

    with tab1:
        st.subheader("අලුත් ගනුදෙනුවක් ඇතුළත් කරන්න")
        with st.form("add_data", clear_on_submit=True):
            col1, col2 = st.columns(2)
            t_type = col1.selectbox("වර්ගය", ["Expense", "Income"])
            t_amt = col2.number_input("මුදල (LKR)", min_value=0.0, step=100.0)
            
            t_cat = st.selectbox("ප්‍රවර්ගය", ["Food", "Travel", "Bills", "Rent", "Salary", "Shopping", "Other"])
            t_note = st.text_input("විස්තරය (Description)")
            
            if st.form_submit_button("Save to Cloud"):
                if t_amt > 0:
                    # අලුත් පේළිය සෑදීම
                    new_row = pd.DataFrame([{
                        "Date": str(date.today()),
                        "Category": t_cat,
                        "Amount": t_amt,
                        "Description": t_note,
                        "Type": t_type
                    }])
                    
                    # පරණ දත්ත සමඟ අලුත් පේළිය එකතු කිරීම
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    
                    # Google Sheet එක Update කිරීම
                    conn.update(data=updated_df)
                    
                    st.success("දත්ත සාර්ථකව Cloud එකට සුරැකුණා! ✅")
                    st.rerun()
                else:
                    st.warning("කරුණාකර මුදලක් ඇතුළත් කරන්න.")

    with tab2:
        st.subheader("පසුගිය ගනුදෙනු විස්තර")
        if not df.empty:
            # අලුත්ම දත්ත උඩට එන සේ පෙන්වීම
            st.dataframe(df.iloc[::-1], use_container_width=True)
        else:
            st.info("දත්ත කිසිවක් මෙතෙක් ඇතුළත් කර නැත.")
