import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Smart Finance Tracker", layout="wide")

# --- 2. CSS Styles (Custom UI) ---
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

    /* 🔥 Transaction Row Design */
    .trans-row {
        background: white; border-radius: 12px; padding: 12px 15px;
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 8px; border-left: 5px solid #ccc;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    .income-border { border-left-color: #28a745; }
    .expense-border { border-left-color: #dc3545; }

    /* Button Styling */
    div.stButton > button {
        padding: 2px 8px !important; border-radius: 8px !important;
        height: 32px !important; width: 35px !important;
        border: 1px solid #eee !important; background: #fff !important;
        transition: 0.2s;
    }
    div.stButton > button:hover { background: #f0f2f6 !important; border-color: #0081C9 !important; }

    /* FAB */
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
    st.error("Sheet Connection Failed!"); st.stop()

# --- 4. Header & Routing ---
st.markdown('<div class="header-bar">Finance Tracker Pro</div>', unsafe_allow_html=True)
query = st.query_params
form_type = query.get("form")
edit_idx = query.get("edit")

# --- 5. CATEGORY SETTINGS (FIXED) ---
if form_type == "ManageCats":
    st.subheader("⚙️ Manage Categories")
    with st.container():
        new_c = st.text_input("New Category Name")
        if st.button("➕ Add", key="add_cat_btn"):
            if new_c:
                cat_sheet.append_row([new_c])
                st.success(f"Added: {new_c}")
                st.rerun()
    
    st.write("---")
    for c in categories:
        col1, col2 = st.columns([0.8, 0.2])
        col1.write(f"• {c}")
        if col2.button("➖", key=f"del_{c}"):
            cell = cat_sheet.find(c)
            cat_sheet.delete_rows(cell.row)
            st.rerun()
    if st.button("Back to Home"):
        st.query_params.clear(); st.rerun()

# --- 6. INCOME/EXPENSE FORM ---
elif form_type in ["Income", "Expense", "Transfer"] or edit_idx:
    curr_type = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    st.subheader(f"📝 {curr_type} Entry")
    with st.form("entry_form"):
        f_date = st.date_input("Date", date.today())
        f_cat = st.selectbox("Category", categories)
        f_amt = st.number_input("Amount", min_value=0.0)
        f_desc = st.text_input("Description")
        if st.form_submit_button("Save ✅"):
            ts = f"{f_date} {datetime.now().strftime('%H:%M:%S')}"
            row_data = [ts, f_cat, f_amt, f_desc, curr_type, "Cash", "Bank", ""]
            if edit_idx: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [row_data])
            else: worksheet.append_row(row_data)
            st.query_params.clear(); st.rerun()
    if st.button("Cancel"):
        st.query_params.clear(); st.rerun()

# --- 7. HOME PAGE (RECENT ACTIVITY - QUALITY UI) ---
elif not form_type and not edit_idx:
    # Summary
    if not df.empty:
        t_inc, t_exp = df[df['Type'] == 'Income']['Amount'].sum(), df[df['Type'] == 'Expense']['Amount'].sum()
        bal = 38814.85 + (t_inc - t_exp)
        st.markdown(f"""
            <div style="background:white; border-radius:15px; padding:15px; text-align:center; box-shadow:0 4px 10px rgba(0,0,0,0.03); margin-bottom:20px;">
                <small style="color:gray;">TOTAL BALANCE</small><br><b style="font-size:24px; color:#0081C9;">LKR {bal:,.2f}</b>
            </div>
        """, unsafe_allow_html=True)

    st.write("<b>Recent Activity</b>", unsafe_allow_html=True)
    
    # 🔥 The Quality Inline Row Implementation
    for idx in df.index[-10:][::-1]:
        row = df.loc[idx]
        is_inc = row['Type'] == 'Income'
        border_cls = "income-border" if is_inc else "expense-border"
        amt_color = "#28a745" if is_inc else "#dc3545"
        
        # Wrapping buttons and info into columns within a styled container
        with st.container():
            c_info, c_amt, c_edit, c_del = st.columns([0.4, 0.3, 0.15, 0.15])
            
            # Using custom HTML for the white background strip
            with c_info:
                st.markdown(f"""
                    <div style="padding:5px 0 5px 10px; border-left:5px solid {'#28a745' if is_inc else '#dc3545'}; margin-left:-15px;">
                        <b>{row['Category']}</b><br><small style="color:gray;">{row['Date']}</small>
                    </div>
                """, unsafe_allow_html=True)
            
            with c_amt:
                st.markdown(f"""<div style="height:45px; display:flex; align-items:center; font-weight:700; color:{amt_color};">LKR {row['Amount']:,.0f}</div>""", unsafe_allow_html=True)
            
            with c_edit:
                st.write("") # vertical spacing
                if st.button("✏️", key=f"ed_{idx}"):
                    st.query_params.update(edit=idx); st.rerun()
            
            with c_del:
                st.write("") # vertical spacing
                if st.button("🗑️", key=f"dl_{idx}"):
                    worksheet.delete_rows(int(idx)+2); st.rerun()
            
            st.markdown('<div style="margin-top:-10px; border-bottom:1px solid #eee; margin-bottom:10px;"></div>', unsafe_allow_html=True)

# --- 8. FAB MENU ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-list">
            <a href="./?form=ManageCats" target="_self" class="fab-item"><span class="fab-label">Settings</span><div class="fab-icon" style="background:#6c757d;">⚙️</div></a>
            <a href="./?form=Income" target="_self" class="fab-item"><span class="fab-label">Income</span><div class="fab-icon" style="background:#28a745;">➕</div></a>
            <a href="./?form=Expense" target="_self" class="fab-item"><span class="fab-label">Expense</span><div class="fab-icon" style="background:#dc3545;">➖</div></a>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
