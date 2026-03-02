import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- 2. CSS Styles ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f3f6; }
    .header-bar {
        background-color: #0081C9; padding: 15px; color: white;
        text-align: center; font-size: 20px; font-weight: bold;
        margin: -60px -20px 20px -20px;
    }
    .custom-grid {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 12px; margin-top: 10px; margin-bottom: 20px;
    }
    .grid-item {
        background: white; border: 1px solid #ddd; border-radius: 12px;
        height: 90px; display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        font-weight: bold; color: #333 !important; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        cursor: pointer; text-decoration: none !important;
        font-size: 14px;
    }
    [data-testid="stForm"] {
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border: 1px solid #e0e0e0 !important;
    }
    .summary-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; text-align: center; }
    .sum-grid { display: flex; justify-content: space-around; border-top: 1px solid #eee; padding-top: 10px; margin-top: 10px; }
    .bal-box { background: #e3f2fd; padding: 10px; border-radius: 8px; margin-top: 10px; text-align: right; font-weight: bold; color: green; }
    
    .trans-card { 
        background: white; padding: 12px 15px; border-radius: 10px; 
        display: flex; justify-content: space-between; 
        align-items: center; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        margin-bottom: 5px;
    }
    .trans-income { border-left: 6px solid #28a745 !important; }
    .trans-expense { border-left: 6px solid #dc3545 !important; }
    
    /* Buttons area styling */
    .action-btns { display: flex; gap: 5px; justify-content: flex-end; }
    
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 999999 !important; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { width: 60px; height: 60px; background: #0081C9; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 35px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); cursor: pointer; }
    .fab-list { display: none; flex-direction: column; gap: 10px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 10px; text-decoration: none !important; }
    .fab-label { background: white; padding: 5px 12px; border-radius: 6px; font-size: 13px; font-weight: bold; color: #333; }
    .fab-icon { width: 45px; height: 45px; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Header ---
st.markdown('<div class="header-bar">Smart Finance Tracker</div>', unsafe_allow_html=True)

# --- 4. Google Sheets Connection ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = {k: st.secrets["connections"]["gsheets"][k] for k in st.secrets["connections"]["gsheets"]}
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet = sh.worksheet("Sheet1")
    cat_sheet = sh.worksheet("Categories")

    categories = [row['CategoryName'] for row in cat_sheet.get_all_records()]
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"Connection Error: {str(e)}"); st.stop()

# --- 5. Action Buttons ---
st.markdown(f"""
    <div class="custom-grid">
        <a href="./?form=Income" target="_self" class="grid-item"><span>➕</span> Income</a>
        <a href="./?form=Expense" target="_self" class="grid-item"><span>➖</span> Expense</a>
        <a href="./?form=Transfer" target="_self" class="grid-item"><span>🔄</span> Transfer</a>
        <a href="./?form=History" target="_self" class="grid-item"><span>📜</span> History</a>
    </div>
""", unsafe_allow_html=True)

query_params = st.query_params
query_form = query_params.get("form")
edit_id = query_params.get("edit")

# --- 6. DATA ENTRY / EDIT FORM ---
if query_form in ["Income", "Expense", "Transfer"] or edit_id:
    title = f"Edit Record" if edit_id else f"New {query_form}"
    st.markdown(f"### 📝 {title}")
    
    # පරණ දත්ත ලබා ගැනීම (Edit නම්)
    default_vals = {"Date": date.today(), "Category": categories[0], "Amount": 0.0, "Description": "", "Note": "", "Type": query_form}
    if edit_id:
        row_idx = int(edit_id)
        target_row = df.loc[row_idx]
        try:
            default_vals["Date"] = datetime.strptime(target_row['Date'].split(' ')[0], '%Y-%m-%d').date()
        except: pass
        default_vals["Category"] = target_row['Category']
        default_vals["Amount"] = float(target_row['Amount'])
        default_vals["Description"] = target_row.get('Description', '')
        default_vals["Note"] = target_row.get('Note', '')
        default_vals["Type"] = target_row['Type']

    with st.form("entry_form", clear_on_submit=True):
        f_date = st.date_input("Date", default_vals["Date"])
        f_cat = st.selectbox("Category", categories, index=categories.index(default_vals["Category"]) if default_vals["Category"] in categories else 0)
        f_amount = st.number_input("Amount (LKR)", value=default_vals["Amount"], step=10.0)
        f_desc = st.text_input("Description", value=default_vals["Description"])
        f_note = st.text_area("Note", value=default_vals["Note"])
        
        if st.form_submit_button("Save Changes ✅" if edit_id else "Save Record ✅"):
            if f_amount > 0:
                ts = f"{f_date} {datetime.now().strftime('%H:%M:%S')}"
                new_data = [ts, f_cat, f_amount, f_desc, default_vals["Type"], "Cash", "Bank", f_note]
                
                if edit_id:
                    worksheet.update(f'A{int(edit_id)+2}:H{int(edit_id)+2}', [new_data])
                    st.success("Updated Successfully!")
                else:
                    worksheet.append_row(new_data)
                
                st.query_params.clear()
                st.rerun()

# --- 7. Summary Dashboard ---
if not df.empty:
    total_income = df[df['Type'] == 'Income']['Amount'].sum()
    total_expense = df[df['Type'] == 'Expense']['Amount'].sum()
    current_balance = total_income - total_expense
    final_total = 38814.85 + current_balance

    st.markdown(f"""
        <div class="summary-card">
            <div class="sum-grid">
                <div><span style="color:green; font-size:11px;">Income</span><br><b style="color:green;">{total_income:,.0f}</b></div>
                <div><span style="color:red; font-size:11px;">Expense</span><br><b style="color:red;">{total_expense:,.0f}</b></div>
                <div><span style="color:gray; font-size:11px;">Balance</span><br><b>{current_balance:,.0f}</b></div>
            </div>
            <div class="bal-box">Total Balance <span>{final_total:,.2f}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 8. Recent Transactions with EDIT & DELETE ---
st.write("<b>Recent Transactions</b>", unsafe_allow_html=True)
if not df.empty:
    latest_indices = df.index[-10:][::-1]
    for idx in latest_indices:
        row = df.loc[idx]
        card_class = "trans-income" if row['Type'] == "Income" else "trans-expense"
        amount_color = "#28a745" if row['Type'] == "Income" else "#dc3545"
        
        # UI Layout
        col_info, col_actions = st.columns([0.75, 0.25])
        
        with col_info:
            st.markdown(f"""
                <div class="trans-card {card_class}">
                    <div>
                        <div style="font-size:10px; color:gray;">{row['Date']}</div>
                        <div style="font-weight:bold; font-size:13px;">{row['Category']}</div>
                        <div style="font-size:11px; color:#666;">{row.get('Description', '')}</div>
                    </div>
                    <div style="color:{amount_color}; font-weight:bold; font-size:15px; text-align:right;">
                        {"+" if row['Type'] == "Income" else "-"}{row['Amount']:,.0f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col_actions:
            c_edit, c_del = st.columns(2)
            with c_edit:
                if st.button("✏️", key=f"ed_{idx}"):
                    st.query_params.update(edit=idx)
                    st.rerun()
            with c_del:
                if st.button("🗑️", key=f"de_{idx}"):
                    worksheet.delete_rows(int(idx) + 2)
                    st.rerun()
        st.markdown('<div style="margin-bottom: 8px;"></div>', unsafe_allow_html=True)

# --- 9. Floating Menu ---
st.markdown(f"""
    <div class="fab-wrapper">
        <div class="fab-list">
            <a href="./?form=History" target="_self" class="fab-item"><span class="fab-label">History</span><div class="fab-icon" style="background:#007bff;">📜</div></a>
            <a href="./?form=Transfer" target="_self" class="fab-item"><span class="fab-label">Transfer</span><div class="fab-icon" style="background:#fd7e14;">🔄</div></a>
            <a href="./?form=Income" target="_self" class="fab-item"><span class="fab-label">Income</span><div class="fab-icon" style="background:#28a745;">➕</div></a>
            <a href="./?form=Expense" target="_self" class="fab-item"><span class="fab-label">Expense</span><div class="fab-icon" style="background:#dc3545;">➖</div></a>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
