import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Smart Finance Tracker", layout="wide")

# --- 2. CSS Styles (High Quality UI) ---
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
    /* Form Quality Enhancement */
    [data-testid="stForm"] {
        background-color: #ffffff !important;
        padding: 25px !important;
        border-radius: 15px !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    .trans-card { 
        background: white; padding: 12px 15px; border-radius: 10px; 
        display: flex; justify-content: space-between; 
        align-items: center; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        margin-bottom: 5px;
    }
    .trans-income { border-left: 6px solid #28a745 !important; }
    .trans-expense { border-left: 6px solid #dc3545 !important; }
    
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 999999 !important; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { width: 60px; height: 60px; background: #0081C9; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 35px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); cursor: pointer; }
    .fab-list { display: none; flex-direction: column; gap: 10px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 10px; text-decoration: none !important; }
    .fab-label { background: white; padding: 5px 12px; border-radius: 6px; font-size: 13px; font-weight: bold; color: #333; }
    .fab-icon { width: 45px; height: 45px; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 20px; }
    
    .cat-row { 
        display: flex; justify-content: space-between; align-items: center; 
        background: white; padding: 10px 15px; border-radius: 8px; 
        margin-bottom: 8px; border: 1px solid #eee; font-weight: 500;
    }
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

    all_cat_data = cat_sheet.get_all_records()
    categories = sorted(list(set([row['CategoryName'] for row in all_cat_data if row['CategoryName']])))
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"Connection Error: {str(e)}"); st.stop()

# --- 5. Action Grid ---
st.markdown(f"""
    <div class="custom-grid">
        <a href="./?form=Income" target="_self" class="grid-item"><span>➕</span> Income</a>
        <a href="./?form=Expense" target="_self" class="grid-item"><span>➖</span> Expense</a>
        <a href="./?form=Transfer" target="_self" class="grid-item"><span>🔄</span> Transfer</a>
        <a href="./?form=ManageCats" target="_self" class="grid-item"><span>⚙️</span> Categories</a>
        <a href="./?form=History" target="_self" class="grid-item"><span>📜</span> History</a>
    </div>
""", unsafe_allow_html=True)

query_params = st.query_params
query_form = query_params.get("form")
edit_id = query_params.get("edit")

# --- 6. Manage Categories ---
if query_form == "ManageCats":
    st.subheader("⚙️ Manage Categories")
    new_cat_input = st.text_input("New Category Name")
    if st.button("➕ Add Category", type="primary"):
        if new_cat_input and new_cat_input not in categories:
            cat_sheet.append_row([new_cat_input])
            st.success("Category Added!"); st.rerun()

    st.write("---")
    for c in categories:
        col_c, col_b = st.columns([0.85, 0.15])
        col_c.markdown(f'<div class="cat-row">{c}</div>', unsafe_allow_html=True)
        if col_b.button("➖", key=f"del_{c}"):
            try:
                cell = cat_sheet.find(c)
                cat_sheet.delete_rows(cell.row); st.rerun()
            except: pass

# --- 7. QUALITY DATA ENTRY / EDIT FORM ---
elif query_form in ["Income", "Expense", "Transfer"] or edit_id:
    # 🎯 Identify Record Type
    current_type = query_form
    if edit_id:
        current_type = df.loc[int(edit_id)]['Type']
    
    # 🎯 Filter Categories
    if current_type == "Income":
        show_cats = [c for c in categories if c in ["Salary", "House Rental"]]
    else:
        show_cats = [c for c in categories if c not in ["Salary", "House Rental"]]

    st.markdown(f"### 📝 {'Edit Record' if edit_id else 'New ' + current_type}")
    
    # 🎯 Prepare Default Values for Edit
    def_date = date.today()
    def_cat = show_cats[0] if show_cats else "General"
    def_amt = 0.0
    def_desc = ""
    def_note = ""

    if edit_id:
        row = df.loc[int(edit_id)]
        try: def_date = datetime.strptime(row['Date'].split(' ')[0], '%Y-%m-%d').date()
        except: pass
        def_cat = row['Category']
        def_amt = float(row['Amount'])
        def_desc = row.get('Description', '')
        def_note = row.get('Note', '')

    # 🎯 High Quality Form
    with st.form("quality_form", clear_on_submit=True):
        f_date = st.date_input("Date", def_date)
        f_cat = st.selectbox("Category", show_cats, index=show_cats.index(def_cat) if def_cat in show_cats else 0)
        f_amount = st.number_input("Amount (LKR)", value=def_amt, min_value=0.0, step=10.0)
        f_desc = st.text_input("Description (Optional)", value=def_desc)
        f_note = st.text_area("Additional Note", value=def_note)
        
        btn_label = "Update Record ✅" if edit_id else f"Save {current_type} ✅"
        if st.form_submit_button(btn_label):
            if f_amount > 0:
                ts = f"{f_date} {datetime.now().strftime('%H:%M:%S')}"
                new_data = [ts, f_cat, f_amount, f_desc, current_type, "Cash", "Bank", f_note]
                
                if edit_id:
                    worksheet.update(f'A{int(edit_id)+2}:H{int(edit_id)+2}', [new_data])
                    st.success("Updated!")
                else:
                    worksheet.append_row(new_data)
                    st.success("Saved!")
                
                st.query_params.clear()
                st.rerun()
            else:
                st.warning("Please enter an amount!")

# --- 8. Dashboard ---
if not df.empty and not query_form and not edit_id:
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

    st.write("<b>Recent Transactions</b>")
    for idx in df.index[-10:][::-1]:
        row = df.loc[idx]
        col1, col2 = st.columns([0.78, 0.22])
        col1.markdown(f"""
            <div class="trans-card {'trans-income' if row['Type'] == 'Income' else 'trans-expense'}">
                <div><b>{row['Category']}</b><br><small>{row['Date']}</small></div>
                <div style="font-weight:bold;">{'+' if row['Type'] == 'Income' else '-'}{row['Amount']:,.0f}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            c1, c2 = st.columns(2)
            if c1.button("✏️", key=f"e_{idx}"): st.query_params.update(edit=idx); st.rerun()
            if c2.button("🗑️", key=f"d_{idx}"): worksheet.delete_rows(int(idx) + 2); st.rerun()

# --- 9. Floating Menu ---
st.markdown(f"""
    <div class="fab-wrapper">
        <div class="fab-list">
            <a href="./?form=History" target="_self" class="fab-item"><span class="fab-label">History</span><div class="fab-icon" style="background:#007bff;">📜</div></a>
            <a href="./?form=ManageCats" target="_self" class="fab-item"><span class="fab-label">Settings</span><div class="fab-icon" style="background:#6c757d;">⚙️</div></a>
            <a href="./?form=Transfer" target="_self" class="fab-item"><span class="fab-label">Transfer</span><div class="fab-icon" style="background:#fd7e14;">🔄</div></a>
            <a href="./?form=Income" target="_self" class="fab-item"><span class="fab-label">Income</span><div class="fab-icon" style="background:#28a745;">➕</div></a>
            <a href="./?form=Expense" target="_self" class="fab-item"><span class="fab-label">Expense</span><div class="fab-icon" style="background:#dc3545;">➖</div></a>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
