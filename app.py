import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
import time

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Pro", layout="wide")

# --- 2. 🎨 ULTIMATE PREMIUM UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8f9fc; }

    .header-wrapper {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
        padding: 50px 20px; color: white; border-radius: 0 0 40px 40px;
        text-align: center; margin: -65px -20px 30px -20px;
        box-shadow: 0 15px 35px rgba(0,122,255,0.25);
    }

    /* PREMIUM BALANCE CARD */
    .premium-card {
        background: linear-gradient(145deg, #ffffff, #f0f4f8);
        border-radius: 30px; padding: 35px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.8);
        margin-bottom: 30px; position: relative; overflow: hidden;
    }
    .balance-label { color: #8E8E93; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px; }
    .balance-amount { color: #1c1c1e; font-size: 42px; font-weight: 800; letter-spacing: -1px; margin-bottom: 25px; }
    .stat-container { display: flex; gap: 20px; padding-top: 25px; border-top: 1px solid rgba(0,0,0,0.05); }
    .stat-box { flex: 1; padding: 15px; border-radius: 20px; background: rgba(255,255,255,0.5); }
    .stat-inc { border-left: 5px solid #34C759; }
    .stat-exp { border-left: 5px solid #FF3B30; }
    .stat-title { color: #8E8E93; font-size: 12px; font-weight: 600; margin-bottom: 4px; }
    .stat-value { font-size: 18px; font-weight: 700; }

    /* Buttons */
    .grid-btn {
        background: white; border-radius: 20px; padding: 20px; 
        text-align: center; text-decoration: none !important; 
        color: #1c1c1e !important; font-weight: 700; 
        border: 1px solid #f1f3f5; display: block; transition: all 0.3s ease;
    }
    .grid-btn:hover { border-color: #007AFF; transform: translateY(-5px); box-shadow: 0 12px 25px rgba(0,122,255,0.1); }
    
    div.stButton > button { border-radius: 12px !important; transition: 0.3s !important; }

    /* 🔥 IMPROVED ACTIVITY CARD SPACING */
    .activity-container {
        background: white; 
        border-radius: 20px; 
        margin-bottom: 15px; /* වැඩිපුර ඉඩක් දුන්නා */
        display: flex; align-items: center; justify-content: space-between;
        transition: 0.3s ease; 
        border: 1px solid rgba(0,0,0,0.03);
        overflow: hidden; 
        position: relative; 
        padding: 18px 15px 18px 28px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); /* ලස්සන Soft Shadow එකක් */
    }
    .activity-container:hover {
        transform: scale(1.01);
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    }
    .v-line { position: absolute; left: 0; top: 0; bottom: 0; width: 8px; }
    .bg-income { background-color: #34C759; }
    .bg-expense { background-color: #FF3B30; }

    /* FAB */
    .fab-wrapper { position: fixed; bottom: 35px; right: 30px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end; gap: 15px; }
    .fab-main { 
        width: 65px; height: 65px; background: linear-gradient(135deg, #007AFF 0%, #0056b3 100%);
        border-radius: 22px; display: flex; justify-content: center; align-items: center; 
        color: white; font-size: 32px; box-shadow: 0 12px 25px rgba(0,122,255,0.4); cursor: pointer;
    }
    .fab-list { display: none; flex-direction: column; gap: 12px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 12px; text-decoration: none !important; }
    .fab-label { background: white; padding: 8px 16px; border-radius: 12px; font-size: 14px; font-weight: 600; color: #1c1c1e; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
    .fab-icon { width: 48px; height: 48px; border-radius: 16px; display: flex; justify-content: center; align-items: center; color: white; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Data Connection (Cached) ---
@st.cache_resource
def get_gsheet_client():
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds)

try:
    client = get_gsheet_client()
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet, cat_sheet = sh.worksheet("Sheet1"), sh.worksheet("Categories")

    @st.cache_data(ttl=60)
    def load_data():
        df_all = pd.DataFrame(worksheet.get_all_records())
        if not df_all.empty: df_all['Amount'] = pd.to_numeric(df_all['Amount'], errors='coerce').fillna(0)
        cats = sorted(list(set([row['CategoryName'] for row in cat_sheet.get_all_records() if row['CategoryName']])))
        try: op_bal = float(cat_sheet.acell('B1').value.replace(',', ''))
        except: op_bal = 0.0
        return df_all, cats, op_bal

    df, categories, opening_bal = load_data()
except Exception as e:
    st.error(f"Error: {e}"); st.stop()

q = st.query_params
form_type, edit_idx = q.get("form"), q.get("edit")

st.markdown('<div class="header-wrapper"><h1>FinanceFlow</h1><p style="opacity:0.8">Smart Wealth Tracker</p></div>', unsafe_allow_html=True)

# --- 5. HOME PAGE ---
if not form_type and not edit_idx:
    if not df.empty:
        t_inc = df[df['Type'] == 'Income']['Amount'].sum()
        t_exp = df[df['Type'] == 'Expense']['Amount'].sum()
        curr_bal = opening_bal + t_inc - t_exp

        st.markdown(f"""
            <div class="premium-card">
                <div class="balance-label">Net Balance</div>
                <div class="balance-amount">LKR {curr_bal:,.2f}</div>
                <div class="stat-container">
                    <div class="stat-box stat-inc">
                        <div class="stat-title">Income</div>
                        <div class="stat-value" style="color: #34C759;">+ {t_inc:,.0f}</div>
                    </div>
                    <div class="stat-box stat-exp">
                        <div class="stat-title">Expenses</div>
                        <div class="stat-value" style="color: #FF3B30;">- {t_exp:,.0f}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Action Grid
    st.markdown('<div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:15px; margin-bottom:30px;">'
                '<a href="./?form=Income" target="_self" class="grid-btn">💰 Income</a>'
                '<a href="./?form=Expense" target="_self" class="grid-btn">💸 Expense</a>'
                '<a href="./?form=Transfer" target="_self" class="grid-btn">🔄 Transfer</a>'
                '<a href="./?form=History" target="_self" class="grid-btn">📜 History</a>'
                '</div>', unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<h3 style="font-size:20px; font-weight:700; margin: 10px 0 20px 0;">Recent Activity</h3>', unsafe_allow_html=True)
        recent_items = df.tail(10).iloc[::-1]
        for idx_row, row in recent_items.iterrows():
            v_line_color = "bg-income" if row['Type'] == 'Income' else "bg-expense"
            st.markdown(f'<div class="activity-container"><div class="v-line {v_line_color}"></div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([0.5, 0.25, 0.12, 0.12])
            with c1: st.markdown(f"<b>{row['Category']}</b><br><small style='color:#8e8e93'>{row['Date']}</small>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div style='font-weight:800; text-align:right; margin-top:8px; font-size:16px;'>{row['Amount']:,.0f}</div>", unsafe_allow_html=True)
            with c3:
                if st.button("📝", key=f"edit_{idx_row}"):
                    st.query_params.update(edit=idx_row)
                    st.rerun()
            with c4:
                if st.button("🗑️", key=f"del_{idx_row}"):
                    worksheet.delete_rows(int(idx_row)+2)
                    st.cache_data.clear(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. FORMS (Add & Edit - Remains Same) ---
elif form_type or edit_idx:
    is_edit = edit_idx is not None
    row_data = df.loc[int(edit_idx)] if is_edit else None
    t = form_type if not is_edit else row_data['Type']
    st.markdown(f'<div class="premium-card"><h3>📝 {"Edit" if is_edit else "Add"} {t}</h3></div>', unsafe_allow_html=True)
    f_date = st.date_input("Date", date.fromisoformat(str(row_data['Date'])) if is_edit else date.today())
    f_cat = st.selectbox("Category", categories, index=categories.index(row_data['Category']) if is_edit and row_data['Category'] in categories else 0)
    f_amt = st.number_input("Amount", min_value=0.0, value=float(row_data['Amount']) if is_edit else 0.0)
    f_desc = st.text_input("Note", value=row_data['Note'] if is_edit else "")
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Update ✅" if is_edit else "Save Entry ✅"):
            new_row = [str(f_date), f_cat, f_amt, f_desc, t, "Cash", "Bank", ""]
            if is_edit: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [new_row])
            else: worksheet.append_row(new_row)
            st.cache_data.clear(); st.query_params.clear(); st.rerun()
    with col2:
        if st.button("Cancel ❌"): st.query_params.clear(); st.rerun()
    with col3:
        if st.button("Home 🏠"): st.query_params.clear(); st.rerun()

# --- 9. FLOATING ACTION MENU ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-list">
            <a href="./" target="_self" class="fab-item"><span class="fab-label">Home</span><div class="fab-icon" style="background:#1c1c1e;">🏠</div></a>
            <a href="./?form=History" target="_self" class="fab-item"><span class="fab-label">History</span><div class="fab-icon" style="background:#007AFF;">📜</div></a>
            <a href="./?form=ManageCats" target="_self" class="fab-item"><span class="fab-label">Settings</span><div class="fab-icon" style="background:#5856D6;">⚙️</div></a>
            <a href="./?form=Transfer" target="_self" class="fab-item"><span class="fab-label">Transfer</span><div class="fab-icon" style="background:#FF9500;">🔄</div></a>
            <a href="./?form=Income" target="_self" class="fab-item"><span class="fab-label">Income</span><div class="fab-icon" style="background:#34C759;">➕</div></a>
            <a href="./?form=Expense" target="_self" class="fab-item"><span class="fab-label">Expense</span><div class="fab-icon" style="background:#FF3B30;">➖</div></a>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
