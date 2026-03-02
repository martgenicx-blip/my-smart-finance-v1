import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Smart Finance Tracker", layout="wide")

# --- 2. CSS Styles (Ultra Professional UI) ---
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

    /* Summary Card */
    .main-summary { background: white; border-radius: 20px; padding: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 25px; }
    .summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .stat-box { padding: 15px; border-radius: 15px; text-align: center; }
    .income-box { background: #e8f5e9; border: 1px solid #c8e6c9; }
    .expense-box { background: #ffebee; border: 1px solid #ffcdd2; }
    .balance-container { grid-column: span 2; background: #f0f7ff; border: 1px solid #d1e3ff; padding: 15px; border-radius: 15px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; }
    
    /* Action Grid */
    .custom-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 25px; }
    .grid-item {
        background: white; border: 1px solid #eee; border-radius: 15px; height: 85px; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 600; color: #444 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        text-decoration: none !important;
    }

    /* 🔥 Transaction Row Style - Making it Inline */
    .trans-row {
        background: white; border-radius: 15px; padding: 10px 15px;
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 8px; border-left: 6px solid #ccc;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .trans-income { border-left-color: #28a745; }
    .trans-expense { border-left-color: #dc3545; }

    /* Button Styling */
    div.stButton > button {
        padding: 2px 10px !important;
        border-radius: 8px !important;
        border: 1px solid #eee !important;
        height: 32px !important;
        background-color: white !important;
    }

    /* FAB Menu */
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

# --- 4. Routing ---
query = st.query_params
form_type = query.get("form")
edit_idx = query.get("edit")

# --- 5. Header ---
st.markdown('<div class="header-bar">Finance Tracker Pro</div>', unsafe_allow_html=True)

# --- 6. Summary Section ---
if not df.empty and not form_type and not edit_idx:
    t_inc = df[df['Type'] == 'Income']['Amount'].sum()
    t_exp = df[df['Type'] == 'Expense']['Amount'].sum()
    bal = t_inc - t_exp
    final_bal = 38814.85 + bal

    st.markdown(f"""
        <div class="main-summary">
            <div class="summary-grid">
                <div class="stat-box income-box"><div style="font-size:11px;color:#666;">INCOME</div><div style="font-weight:700;color:#2e7d32;">LKR {t_inc:,.0f}</div></div>
                <div class="stat-box expense-box"><div style="font-size:11px;color:#666;">EXPENSE</div><div style="font-weight:700;color:#c62828;">LKR {t_exp:,.0f}</div></div>
            </div>
            <div class="balance-container">
                <div><div style="font-size:11px;color:#666;">TOTAL BALANCE</div><div style="font-size:22px;font-weight:700;color:#0081C9;">LKR {final_bal:,.2f}</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="custom-grid">
            <a href="./?form=Income" target="_self" class="grid-item"><span>💰</span> Income</a>
            <a href="./?form=Expense" target="_self" class="grid-item"><span>💸</span> Expense</a>
            <a href="./?form=Transfer" target="_self" class="grid-item"><span>🔄</span> Transfer</a>
            <a href="./?form=History" target="_self" class="grid-item"><span>📜</span> History</a>
        </div>
    """, unsafe_allow_html=True)

# --- 7. Activity (🔥 THE INLINE FIX) ---
if not form_type and not edit_idx and not df.empty:
    st.write("<b>Recent Activity</b>", unsafe_allow_html=True)
    
    for idx in df.index[-10:][::-1]:
        row = df.loc[idx]
        is_inc = row['Type'] == 'Income'
        
        # 🎯 Desktop එකේදී එකම පේළියක ඔක්කොම ලස්සනට පේන්න columns 4ක් ගත්තා
        c_info, c_amt, c_edit, c_del = st.columns([0.5, 0.25, 0.12, 0.13])
        
        with c_info:
            st.markdown(f"""
                <div class="trans-row {'trans-income' if is_inc else 'trans-expense'}">
                    <div><b>{row['Category']}</b><br><small>{row['Date']}</small></div>
                </div>""", unsafe_allow_html=True)
        
        with c_amt:
            st.markdown(f"""
                <div style="height:55px; display:flex; align-items:center; font-weight:700; color:{'#28a745' if is_inc else '#dc3545'};">
                    {'+' if is_inc else '-'}{row['Amount']:,.0f}
                </div>""", unsafe_allow_html=True)
        
        with c_edit:
            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True) # Vertical alignment
            if st.button("✏️", key=f"ed_{idx}"):
                st.query_params.update(edit=idx); st.rerun()
                
        with c_del:
            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
            if st.button("🗑️", key=f"dl_{idx}"):
                worksheet.delete_rows(int(idx)+2); st.rerun()

# --- 8. Forms (Logic unchanged) ---
if form_type == "ManageCats":
    st.subheader("⚙️ Settings")
    new_c = st.text_input("New Category")
    if st.button("➕ Add"):
        if new_c: cat_sheet.append_row([new_c]); st.rerun()

elif form_type in ["Income", "Expense", "Transfer"] or edit_idx:
    curr_t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    scats = [c for c in categories if (c in ["Salary", "House Rental"] if curr_t=="Income" else c not in ["Salary", "House Rental"])]
    with st.form("f"):
        f_cat = st.selectbox("Category", scats)
        f_amt = st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Save"):
            ts = f"{date.today()} {datetime.now().strftime('%H:%M:%S')}"
            r = [ts, f_cat, f_amt, "", curr_t, "Cash", "Bank", ""]
            if edit_idx: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [r])
            else: worksheet.append_row(r)
            st.query_params.clear(); st.rerun()

# --- 9. FAB Menu ---
st.markdown("""
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
