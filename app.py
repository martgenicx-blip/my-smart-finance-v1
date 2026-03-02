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
    .grid-item {
        background: white; border: 1px solid #eee; border-radius: 15px; height: 85px; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 600; color: #444 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        text-decoration: none !important; transition: 0.2s;
    }

    /* 🔥 සම්පූර්ණ පේළියම එකම White BG එකක් කරන එක */
    .trans-row-container {
        background: white;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        border-left: 6px solid #ccc;
    }
    
    /* Button ඉඩ අඩු කරන්න */
    div.stButton > button {
        padding: 2px 5px !important;
        height: 35px !important;
        width: 100% !important;
        border-radius: 8px !important;
    }

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

# --- 4. Header ---
st.markdown('<div class="header-bar">Finance Tracker Pro</div>', unsafe_allow_html=True)

# --- 5. Summary & Action Grid ---
query = st.query_params
form_type = query.get("form")
edit_idx = query.get("edit")

if not form_type and not edit_idx and not df.empty:
    t_inc = df[df['Type'] == 'Income']['Amount'].sum()
    t_exp = df[df['Type'] == 'Expense']['Amount'].sum()
    final_bal = 38814.85 + (t_inc - t_exp)

    st.markdown(f"""
        <div class="main-summary">
            <div class="summary-grid">
                <div class="stat-box income-box"><div class="stat-label">Income</div><div class="stat-value" style="color:#2e7d32;">LKR {t_inc:,.0f}</div></div>
                <div class="stat-box expense-box"><div class="stat-label">Expense</div><div class="stat-value" style="color:#c62828;">LKR {t_exp:,.0f}</div></div>
            </div>
            <div class="balance-container">
                <div><div class="stat-label">Total Balance</div><div class="stat-value balance-val">LKR {final_bal:,.2f}</div></div>
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

# --- 6. Forms ---
if form_type == "ManageCats":
    st.subheader("⚙️ Manage Categories")
    new_c = st.text_input("New Category")
    if st.button("➕ Add"):
        if new_c: cat_sheet.append_row([new_c]); st.rerun()

elif form_type or edit_idx:
    st.markdown(f"### 📝 Entry Form")
    # (Simplified for space - keep your logic here)
    with st.form("f"):
        st.write("Data Entry")
        if st.form_submit_button("Save"): st.query_params.clear(); st.rerun()

# --- 7. Recent Transactions (🎯 THE INLINE FIX) ---
if not form_type and not edit_idx and not df.empty:
    st.write("<b>Recent Activity</b>", unsafe_allow_html=True)
    for idx in df.index[-10:][::-1]:
        row = df.loc[idx]
        color = "#28a745" if row['Type'] == 'Income' else "#dc3545"
        
        # 💡 මෙන්න මෙතන තමයි සේරම එකම සුදු පේළියට ගත්තේ
        with st.container():
            col_info, col_amt, col_ed, col_del = st.columns([0.45, 0.25, 0.15, 0.15])
            
            # සම්පූර්ණ Container එකටම Style එකක් දානවා (CSS හරහා)
            st.markdown(f"""
                <style>
                [data-testid="column"]:nth-child(1) {{ background: white; border-radius: 15px 0 0 15px; border-left: 6px solid {color}; }}
                </style>
                """, unsafe_allow_html=True)
            
            with col_info:
                st.markdown(f"""<div style="padding:10px 5px;"><b>{row['Category']}</b><br><small>{row['Date']}</small></div>""", unsafe_allow_html=True)
            with col_amt:
                st.markdown(f"""<div style="height:100%; display:flex; align-items:center; font-weight:700; color:{color};">LKR {row['Amount']:,.0f}</div>""", unsafe_allow_html=True)
            with col_ed:
                st.write("") # Spacer
                if st.button("✏️", key=f"e_{idx}"): st.query_params.update(edit=idx); st.rerun()
            with col_del:
                st.write("") # Spacer
                if st.button("🗑️", key=f"d_{idx}"): worksheet.delete_rows(int(idx)+2); st.rerun()

# --- 8. FAB Menu ---
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
