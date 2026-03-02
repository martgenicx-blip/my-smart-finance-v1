import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Finance Tracker Pro", layout="wide")

# --- 2. Professional UI Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; font-size: 14px; }
    
    /* Table Header Style */
    .table-header {
        background-color: #f8f9fa; border-bottom: 2px solid #dee2e6;
        padding: 10px 0; font-weight: 700; text-align: center; color: #333;
    }
    
    /* Data Row Style */
    .data-row {
        background-color: white; border-bottom: 1px solid #eee;
        padding: 12px 0; align-items: center; display: flex;
    }

    /* Button Reset */
    div.stButton > button {
        width: 100% !important; border-radius: 4px !important;
        height: 35px !important; background: transparent !important;
        border: 1px solid #ddd !important; font-size: 18px !important;
        padding: 0 !important; margin: 0 !important;
    }
    div.stButton > button:hover { border-color: #0081C9 !important; background: #f0f7ff !important; }
    
    .income-amt { color: #28a745; font-weight: 700; text-align: right; }
    .expense-amt { color: #dc3545; font-weight: 700; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GSheets Setup ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = {k: st.secrets["connections"]["gsheets"][k] for k in st.secrets["connections"]["gsheets"]}
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet, cat_sheet = sh.worksheet("Sheet1"), sh.worksheet("Categories")
    
    categories = sorted(list(set([row['CategoryName'] for row in cat_sheet.get_all_records() if row['CategoryName']])))
    df = pd.DataFrame(worksheet.get_all_records())
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except:
    st.error("Connection Error!"); st.stop()

# --- 4. Navigation Logic ---
query = st.query_params
form_type = query.get("form")
edit_idx = query.get("edit")

# --- 5. HOME PAGE ---
if not form_type and not edit_idx:
    # Top Summary (Optional but helpful)
    st.markdown('<h2 style="text-align:center;">Recent Transactions</h2>', unsafe_allow_html=True)

    # --- TABLE HEADERS ---
    h1, h2, h3, h4 = st.columns([0.6, 0.2, 0.1, 0.1])
    h1.markdown('<div class="table-header">Item & Information</div>', unsafe_allow_html=True)
    h2.markdown('<div class="table-header">Amount</div>', unsafe_allow_html=True)
    h4_title = "Quick Action"
    h3.markdown(f'<div class="table-header" style="border-right:none;">Quick</div>', unsafe_allow_html=True)
    h4.markdown(f'<div class="table-header" style="border-left:none;">Action</div>', unsafe_allow_html=True)

    # --- DATA ROWS ---
    if not df.empty:
        for idx in df.index[-15:][::-1]:
            row = df.loc[idx]
            is_inc = row['Type'] == 'Income'
            amt_class = "income-amt" if is_inc else "expense-amt"
            prefix = "+" if is_inc else "-"

            # Row Start
            r1, r2, r3, r4 = st.columns([0.6, 0.2, 0.1, 0.1])
            
            with r1:
                st.markdown(f'<div style="padding: 10px 0 0 10px; font-size:16px;">{row["Category"]}</div>', unsafe_allow_html=True)
            
            with r2:
                st.markdown(f'<div class="{amt_class}" style="padding-top:10px; font-size:16px;">{prefix}{row["Amount"]:,.0f}</div>', unsafe_allow_html=True)
            
            with r3:
                if st.button("📝", key=f"edit_{idx}"):
                    st.query_params.update(edit=idx); st.rerun()
            
            with r4:
                if st.button("🗑️", key=f"del_{idx}"):
                    worksheet.delete_rows(int(idx)+2); st.rerun()
            
            st.markdown('<div style="border-bottom:1px solid #eee;"></div>', unsafe_allow_html=True)

# --- 6. CATEGORY MANAGEMENT ---
elif form_type == "ManageCats":
    st.subheader("Manage Categories")
    new_cat = st.text_input("New Category")
    if st.button("Add"):
        if new_cat: cat_sheet.append_row([new_cat]); st.rerun()
    for c in categories:
        col1, col2 = st.columns([0.8, 0.2])
        col1.write(c)
        if col2.button("Del", key=f"c_{c}"):
            cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
    if st.button("Back"): st.query_params.clear(); st.rerun()

# --- 7. EDIT/ADD FORM ---
elif edit_idx or form_type in ["Income", "Expense"]:
    st.subheader("Transaction Entry")
    with st.form("my_form"):
        f_cat = st.selectbox("Category", categories)
        f_amt = st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Save"):
            ts = f"{date.today()}"
            r_type = "Income" if form_type == "Income" else "Expense"
            data = [ts, f_cat, f_amt, "", r_type, "Cash", "Bank", ""]
            if edit_idx: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [data])
            else: worksheet.append_row(data)
            st.query_params.clear(); st.rerun()
    if st.button("Cancel"): st.query_params.clear(); st.rerun()

# --- 8. FAB ---
st.markdown("""<div style="position:fixed; bottom:20px; right:20px; z-index:100;">
    <a href="./?form=ManageCats" target="_self" style="text-decoration:none;">
        <div style="background:#0081C9; color:white; width:50px; height:50px; border-radius:50%; display:flex; justify-content:center; align-items:center; font-size:24px; box-shadow:0 4px 10px rgba(0,0,0,0.3);">⚙️</div>
    </a>
</div>""", unsafe_allow_html=True)
