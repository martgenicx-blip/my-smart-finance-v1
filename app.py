import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Smart Finance Tracker", layout="wide")

# --- 2. CSS Styles ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8f9fa; }
    
    .header-bar {
        background: linear-gradient(135deg, #0081C9 0%, #0056b3 100%);
        padding: 20px; color: white; text-align: center; font-size: 22px; font-weight: 700;
        margin: -60px -20px 25px -20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* Transaction Row Container */
    .trans-row {
        background: white; border-radius: 12px; padding: 10px 15px;
        display: flex; align-items: center; margin-bottom: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03); border-left: 5px solid #ccc;
    }
    
    /* Button Style Fixes */
    div.stButton > button {
        padding: 2px 5px !important; border-radius: 8px !important;
        height: 32px !important; width: 35px !important;
        font-size: 14px !important; border: 1px solid #eee !important;
    }

    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { width: 60px; height: 60px; background: #0081C9; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 30px; box-shadow: 0 4px 15px rgba(0,129,201,0.4); }
    .fab-list { display: none; flex-direction: column; gap: 10px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 10px; text-decoration: none !important; }
    .fab-label { background: white; padding: 5px 12px; border-radius: 8px; font-size: 12px; font-weight: 600; color: #333; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .fab-icon { width: 45px; height: 45px; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Google Sheets Connection ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = {k: st.secrets["connections"]["gsheets"][k] for k in st.secrets["connections"]["gsheets"]}
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet = sh.worksheet("Sheet1")
    cat_sheet = sh.worksheet("Categories")
    categories = sorted(list(set([row['CategoryName'] for row in cat_sheet.get_all_records() if row['CategoryName']])))
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except:
    st.error("Connection Failed!"); st.stop()

# --- 4. Header & Routing ---
st.markdown('<div class="header-bar">Finance Tracker Pro</div>', unsafe_allow_html=True)
query = st.query_params
form_type = query.get("form")
edit_idx = query.get("edit")

# --- 5. Home Content ---
if not form_type and not edit_idx:
    # Summary Box
    if not df.empty:
        t_inc = df[df['Type'] == 'Income']['Amount'].sum()
        t_exp = df[df['Type'] == 'Expense']['Amount'].sum()
        bal = 38814.85 + (t_inc - t_exp)
        st.markdown(f"""<div style="background:white; border-radius:15px; padding:15px; margin-bottom:20px; box-shadow:0 2px 10px rgba(0,0,0,0.03); display:flex; justify-content:space-around; text-align:center;">
            <div><small style="color:gray;">INCOME</small><br><b style="color:#28a745;">LKR {t_inc:,.0f}</b></div>
            <div><small style="color:gray;">EXPENSE</small><br><b style="color:#dc3545;">LKR {t_exp:,.0f}</b></div>
            <div><small style="color:gray;">TOTAL</small><br><b style="color:#0081C9;">LKR {bal:,.0f}</b></div>
        </div>""", unsafe_allow_html=True)

    st.write("<b>Recent Activity</b>", unsafe_allow_html=True)

    # 🔥 🎯 එකම ROW එකක සේරම තියෙන කොටස
    for idx in df.index[-10:][::-1]:
        row = df.loc[idx]
        is_inc = row['Type'] == 'Income'
        color = "#28a745" if is_inc else "#dc3545"

        # Columns බෙදීම: Info(0.4), Amount(0.3), Edit(0.15), Delete(0.15)
        c1, c2, c3, c4 = st.columns([0.4, 0.3, 0.15, 0.15])
        
        with c1:
            st.markdown(f"""<div style="border-left:5px solid {color}; padding-left:10px;">
                <b>{row['Category']}</b><br><small style="color:gray;">{row['Date']}</small>
            </div>""", unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"""<div style="height:100%; display:flex; align-items:center; font-weight:700; color:{color};">
                {'+' if is_inc else '-'}{row['Amount']:,.0f}
            </div>""", unsafe_allow_html=True)
            
        with c3:
            st.write("") # vertical spacer
            if st.button("✏️", key=f"e_{idx}"):
                st.query_params.update(edit=idx); st.rerun()
                
        with c4:
            st.write("") # vertical spacer
            if st.button("🗑️", key=f"d_{idx}"):
                worksheet.delete_rows(int(idx)+2); st.rerun()
        
        st.markdown('<hr style="margin: 5px 0; opacity: 0.1;">', unsafe_allow_html=True)

# --- 6. History Section ---
elif form_type == "History":
    st.subheader("📜 History")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("Back"): st.query_params.clear(); st.rerun()

# --- 7. Manage Categories ---
elif form_type == "ManageCats":
    st.subheader("⚙️ Categories")
    new_cat = st.text_input("New Category")
    if st.button("➕ Add"):
        if new_cat: cat_sheet.append_row([new_cat]); st.rerun()
    for c in categories:
        col1, col2 = st.columns([0.8, 0.2])
        col1.write(f"• {c}")
        if col2.button("➖", key=f"del_{c}"):
            cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
    if st.button("Back"): st.query_params.clear(); st.rerun()

# --- 8. Income/Expense Forms ---
elif form_type in ["Income", "Expense"] or edit_idx:
    curr_t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    with st.form("entry_form"):
        f_cat = st.selectbox("Category", categories)
        f_amt = st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Save"):
            ts = f"{date.today()} {datetime.now().strftime('%H:%M:%S')}"
            r = [ts, f_cat, f_amt, "", curr_t, "Cash", "Bank", ""]
            if edit_idx: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [r])
            else: worksheet.append_row(r)
            st.query_params.clear(); st.rerun()
    if st.button("Cancel"): st.query_params.clear(); st.rerun()

# --- 9. FAB Menu ---
st.markdown("""<div class="fab-wrapper">
    <div class="fab-list">
        <a href="./?form=History" target="_self" class="fab-item"><span class="fab-label">History</span><div class="fab-icon" style="background:#007bff;">📜</div></a>
        <a href="./?form=ManageCats" target="_self" class="fab-item"><span class="fab-label">Settings</span><div class="fab-icon" style="background:#6c757d;">⚙️</div></a>
        <a href="./?form=Income" target="_self" class="fab-item"><span class="fab-label">Income</span><div class="fab-icon" style="background:#28a745;">➕</div></a>
        <a href="./?form=Expense" target="_self" class="fab-item"><span class="fab-label">Expense</span><div class="fab-icon" style="background:#dc3545;">➖</div></a>
    </div>
    <div class="fab-main">+</div>
</div>""", unsafe_allow_html=True)
