import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Smart Finance Tracker", layout="wide")

# --- 2. CSS Styles (UI Quality Enhancement) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8f9fa; }
    
    /* Header Style */
    .header-bar {
        background: linear-gradient(135deg, #0081C9 0%, #0056b3 100%);
        padding: 20px; color: white;
        text-align: center; font-size: 22px; font-weight: 700;
        margin: -60px -20px 25px -20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* 🔥 සුපිරි Summary Card Style */
    .main-summary {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    .summary-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
    }
    .stat-box {
        padding: 15px;
        border-radius: 15px;
        text-align: center;
    }
    .income-box { background: #e8f5e9; border: 1px solid #c8e6c9; }
    .expense-box { background: #ffebee; border: 1px solid #ffcdd2; }
    .balance-container {
        grid-column: span 2;
        background: #f0f7ff;
        border: 1px solid #d1e3ff;
        padding: 20px;
        border-radius: 15px;
        margin-top: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .stat-label { font-size: 12px; color: #666; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; }
    .stat-value { font-size: 20px; font-weight: 700; }
    .income-val { color: #2e7d32; }
    .expense-val { color: #c62828; }
    .balance-val { color: #0081C9; font-size: 24px; }

    /* Action Grid */
    .custom-grid {
        display: grid; grid-template-columns: 1fr 1fr;
        gap: 12px; margin-bottom: 25px;
    }
    .grid-item {
        background: white; border: 1px solid #eee; border-radius: 15px;
        height: 85px; display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        font-weight: 600; color: #444 !important; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        text-decoration: none !important; font-size: 14px;
        transition: transform 0.2s;
    }
    .grid-item:active { transform: scale(0.95); }

    /* Transaction Cards */
    .trans-card { 
        background: white; padding: 15px; border-radius: 15px; 
        display: flex; justify-content: space-between; 
        align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 10px; border-left: 6px solid #ccc;
    }
    .trans-income { border-left-color: #28a745; }
    .trans-expense { border-left-color: #dc3545; }
    
    /* FAB Menu */
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 999; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { width: 60px; height: 60px; background: #0081C9; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 30px; box-shadow: 0 4px 15px rgba(0,129,201,0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Header ---
st.markdown('<div class="header-bar">Finance Dashboard</div>', unsafe_allow_html=True)

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
    st.error("Sheet එකට Connect වෙන්න බැහැ මචං!"); st.stop()

# --- 5. Summary Section (NEW & QUALITY) ---
if not df.empty:
    t_income = df[df['Type'] == 'Income']['Amount'].sum()
    t_expense = df[df['Type'] == 'Expense']['Amount'].sum()
    c_balance = t_income - t_expense
    prev_balance = 38814.85
    total_net = prev_balance + c_balance

    st.markdown(f"""
        <div class="main-summary">
            <div class="summary-grid">
                <div class="stat-box income-box">
                    <div class="stat-label">Income</div>
                    <div class="stat-value income-val">LKR {t_income:,.0f}</div>
                </div>
                <div class="stat-box expense-box">
                    <div class="stat-label">Expense</div>
                    <div class="stat-value expense-val">LKR {t_expense:,.0f}</div>
                </div>
            </div>
            <div class="balance-container">
                <div>
                    <div class="stat-label">Available Balance</div>
                    <div class="stat-value balance-val">LKR {total_net:,.2f}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 10px; color: #888;">Net Gain/Loss</div>
                    <div style="font-weight: bold; color: {'#2e7d32' if c_balance >=0 else '#c62828'};">
                        {'+' if c_balance >=0 else ''}{c_balance:,.0f}
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 6. Action Grid ---
st.markdown(f"""
    <div class="custom-grid">
        <a href="./?form=Income" target="_self" class="grid-item"><span>💰</span> Income</a>
        <a href="./?form=Expense" target="_self" class="grid-item"><span>💸</span> Expense</a>
        <a href="./?form=Transfer" target="_self" class="grid-item"><span>🔄</span> Transfer</a>
        <a href="./?form=ManageCats" target="_self" class="grid-item"><span>⚙️</span> Settings</a>
    </div>
""", unsafe_allow_html=True)

query_params = st.query_params
query_form = query_params.get("form")
edit_id = query_params.get("edit")

# --- 7. Data Entry / Manage Cats / Edit (Simplified for Quality) ---
if query_form == "ManageCats":
    st.subheader("⚙️ Settings")
    new_cat = st.text_input("New Category")
    if st.button("Add Now", type="primary"):
        if new_cat and new_cat not in categories:
            cat_sheet.append_row([new_cat]); st.rerun()
    st.write("---")
    for c in categories:
        col_c, col_b = st.columns([0.8, 0.2])
        col_c.write(f"📍 {c}")
        if col_b.button("➖", key=f"del_{c}"):
            cell = cat_sheet.find(c)
            cat_sheet.delete_rows(cell.row); st.rerun()

elif query_form in ["Income", "Expense", "Transfer"] or edit_id:
    # (Data Entry Logic - කලින් Quality එකටම තියෙනවා)
    ctype = query_form if not edit_id else df.loc[int(edit_id)]['Type']
    scats = [c for c in categories if c in ["Salary", "House Rental"]] if ctype=="Income" else [c for c in categories if c not in ["Salary", "House Rental"]]
    
    st.markdown(f"### 📝 {ctype}")
    with st.form("entry_form"):
        f_date = st.date_input("Date", date.today())
        f_cat = st.selectbox("Category", scats)
        f_amt = st.number_input("Amount", min_value=0.0)
        f_desc = st.text_input("Description")
        if st.form_submit_button("Save Record ✅"):
            ts = f"{f_date} {datetime.now().strftime('%H:%M:%S')}"
            row = [ts, f_cat, f_amt, f_desc, ctype, "Cash", "Bank", ""]
            if edit_id: worksheet.update(f'A{int(edit_id)+2}:H{int(edit_id)+2}', [row])
            else: worksheet.append_row(row)
            st.query_params.clear(); st.rerun()

# --- 8. Recent Transactions ---
if not query_form and not edit_id and not df.empty:
    st.write("<b>Recent Activity</b>", unsafe_allow_html=True)
    for idx in df.index[-10:][::-1]:
        row = df.loc[idx]
        is_inc = row['Type'] == 'Income'
        st.markdown(f"""
            <div class="trans-card {'trans-income' if is_inc else 'trans-expense'}">
                <div>
                    <div style="font-weight:700; font-size:14px;">{row['Category']}</div>
                    <div style="font-size:10px; color:#888;">{row['Date']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-weight:700; color:{'#28a745' if is_inc else '#dc3545'};">
                        {'+' if is_inc else '-'}{row['Amount']:,.0f}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        # Edit/Delete Buttons below card for better touch targets
        c1, c2, c3 = st.columns([0.7, 0.15, 0.15])
        if c2.button("✏️", key=f"e_{idx}"): st.query_params.update(edit=idx); st.rerun()
        if c3.button("🗑️", key=f"d_{idx}"): worksheet.delete_rows(int(idx)+2); st.rerun()

# --- 9. Floating Menu ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
