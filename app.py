import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Smart Finance Tracker Pro", layout="wide")

# --- 2. 🎯 CSS (Borderless & Inline) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8f9fa; }
    .header-bar { background: linear-gradient(135deg, #0081C9 0%, #0056b3 100%); padding: 20px; color: white; text-align: center; font-size: 22px; font-weight: 700; margin: -60px -20px 25px -20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .main-summary { background: white; border-radius: 20px; padding: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 25px; }
    .summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .stat-box { padding: 15px; border-radius: 15px; text-align: center; }
    .income-box { background: #e8f5e9; border: 1px solid #c8e6c9; }
    .expense-box { background: #ffebee; border: 1px solid #ffcdd2; }
    .balance-container { grid-column: span 2; background: #f0f7ff; border: 1px solid #d1e3ff; padding: 20px; border-radius: 15px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; }
    .stat-label { font-size: 11px; color: #666; font-weight: 600; text-transform: uppercase; }
    .stat-value { font-size: 18px; font-weight: 700; }
    .balance-val { color: #0081C9; font-size: 22px; }
    .custom-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 25px; }
    .grid-item { background: white; border: 1px solid #eee; border-radius: 15px; height: 85px; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: 600; color: #444 !important; text-decoration: none !important; transition: 0.2s; }
    .row-btn-container div.stButton > button { border: none !important; background: transparent !important; padding: 0 !important; margin: 0 !important; height: 35px !important; width: 35px !important; font-size: 18px !important; box-shadow: none !important; }
    .row-btn-container div.stButton > button:hover { background-color: #eeeeee !important; border-radius: 50% !important; }
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { width: 60px; height: 60px; background: #0081C9; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 30px; box-shadow: 0 4px 15px rgba(0,129,201,0.4); cursor: pointer; }
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
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet = sh.worksheet("Sheet1")
    cat_sheet = sh.worksheet("Categories")
    
    # Opening Balance එක Categories ශීට් එකේ B1 සෙල් එකේ ඇති කියලා හිතමු
    try:
        opening_bal = float(cat_sheet.acell('B1').value.replace(',', ''))
    except:
        opening_bal = 0.0
        
    categories = sorted(list(set([row['CategoryName'] for row in cat_sheet.get_all_records() if row['CategoryName']])))
    df = pd.DataFrame(worksheet.get_all_records())
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"Connection Error: {e}"); st.stop()

# --- 4. Navigation ---
query = st.query_params
form_type, edit_idx = query.get("form"), query.get("edit")
st.markdown('<div class="header-bar">Finance Tracker Pro</div>', unsafe_allow_html=True)

# --- 5. HOME PAGE ---
if not form_type and not edit_idx:
    if not df.empty:
        t_inc = df[df['Type'] == 'Income']['Amount'].sum()
        t_exp = df[df['Type'] == 'Expense']['Amount'].sum()
        current_bal = opening_bal + t_inc - t_exp

        st.markdown(f"""
            <div class="main-summary">
                <div class="summary-grid">
                    <div class="stat-box income-box"><div class="stat-label">Income</div><div class="stat-value" style="color:#2e7d32;">LKR {t_inc:,.0f}</div></div>
                    <div class="stat-box expense-box"><div class="stat-label">Expense</div><div class="stat-value" style="color:#c62828;">LKR {t_exp:,.0f}</div></div>
                </div>
                <div class="balance-container">
                    <div><div class="stat-label">Total Balance</div><div class="stat-value balance-val">LKR {current_bal:,.2f}</div></div>
                    <div style="font-size:10px; color:gray;">Inc. Opening Bal: {opening_bal:,.2f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""<div class="custom-grid"><a href="./?form=Income" target="_self" class="grid-item"><span>💰</span> Income</a><a href="./?form=Expense" target="_self" class="grid-item"><span>💸</span> Expense</a><a href="./?form=Transfer" target="_self" class="grid-item"><span>🔄</span> Transfer</a><a href="./?form=History" target="_self" class="grid-item"><span>📜</span> History</a></div>""", unsafe_allow_html=True)

    if not df.empty:
        st.write("<b>Recent Activity</b>", unsafe_allow_html=True)
        for idx in df.index[-10:][::-1]:
            row = df.loc[idx]
            color = "#28a745" if row['Type'] == 'Income' else "#dc3545"
            st.markdown(f'<div style="background:white; border-radius:12px; margin-bottom:8px; padding:5px; border-left:6px solid {color}; shadow: 0 2px 5px rgba(0,0,0,0.02);">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([0.6, 0.2, 0.1, 0.1])
            with c1: st.markdown(f'<div style="padding-top:5px;"><b>{row["Category"]}</b><br><small>{row["Date"]}</small></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div style="color:{color}; font-weight:700; font-size:18px; padding-top:10px;">{row["Amount"]:,.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="row-btn-container">', unsafe_allow_html=True)
            with c3:
                st.write(" "); (st.button("📝", key=f"e_{idx}") and (st.query_params.update(edit=idx) or st.rerun()))
            with c4:
                st.write(" "); (st.button("🗑️", key=f"d_{idx}") and (worksheet.delete_rows(int(idx)+2) or st.rerun()))
            st.markdown('</div></div>', unsafe_allow_html=True)

# --- 6. HISTORY ---
elif form_type == "History":
    st.subheader("📜 History"); st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("⬅️ Back"): st.query_params.clear(); st.rerun()

# --- 7. MANAGE SETTINGS (Opening Balance Edit) ---
elif form_type == "ManageCats":
    st.subheader("⚙️ Settings")
    
    # 🔥 Section to Edit Opening Balance
    st.write("---")
    st.markdown("#### 💰 Update Opening Balance")
    new_op_bal = st.number_input("Opening Balance (LKR)", value=opening_bal)
    if st.button("Update Balance"):
        cat_sheet.update_acell('B1', new_op_bal)
        st.success("Balance Updated!"); st.rerun()
    
    st.write("---")
    st.markdown("#### ⚙️ Categories")
    new_c = st.text_input("New Category Name")
    if st.button("➕ Add"):
        if new_c: cat_sheet.append_row([new_c]); st.rerun()
    for c in categories:
        col1, col2 = st.columns([0.8, 0.2])
        col1.write(f"• {c}")
        if col2.button("❌", key=f"dc_{c}"):
            cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
    if st.button("⬅️ Back"): st.query_params.clear(); st.rerun()

# --- 8. FORMS ---
elif form_type in ["Income", "Expense", "Transfer"] or edit_idx:
    t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    st.markdown(f"### 📝 {t} Entry")
    f_date, f_cat = st.date_input("Date", date.today()), st.selectbox("Category", categories)
    f_amt, f_desc = st.number_input("Amount", min_value=0.0), st.text_input("Description")
    st.write(" "); b1, b2 = st.columns([0.15, 0.85])
    with b1:
        if st.button("Save ✅"):
            ts = f"{f_date} {datetime.now().strftime('%H:%M:%S')}"; r_data = [ts, f_cat, f_amt, f_desc, t, "Cash", "Bank", ""]
            (worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [r_data]) if edit_idx else worksheet.append_row(r_data))
            st.query_params.clear(); st.rerun()
    with b2:
        if st.button("Cancel ❌"): st.query_params.clear(); st.rerun()

# --- 9. FAB ---
st.markdown("""<div class="fab-wrapper"><div class="fab-list"><a href="./?form=History" target="_self" class="fab-item"><span class="fab-label">History</span><div class="fab-icon" style="background:#007bff;">📜</div></a><a href="./?form=ManageCats" target="_self" class="fab-item"><span class="fab-label">Settings</span><div class="fab-icon" style="background:#6c757d;">⚙️</div></a><a href="./?form=Transfer" target="_self" class="fab-item"><span class="fab-label">Transfer</span><div class="fab-icon" style="background:#fd7e14;">🔄</div></a><a href="./?form=Income" target="_self" class="fab-item"><span class="fab-label">Income</span><div class="fab-icon" style="background:#28a745;">➕</div></a><a href="./?form=Expense" target="_self" class="fab-item"><span class="fab-label">Expense</span><div class="fab-icon" style="background:#dc3545;">➖</div></a></div><div class="fab-main">+</div></div>""", unsafe_allow_html=True)
