import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
import time

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Pro", layout="wide")

# --- 2. 🎨 PREMIUM RESPONSIVE UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8f9fc; }

    .header-wrapper {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
        padding: 40px 15px; color: white; border-radius: 0 0 35px 35px;
        text-align: center; margin: -65px -20px 25px -20px;
        box-shadow: 0 10px 30px rgba(0,122,255,0.2);
    }

    .premium-card {
        background: linear-gradient(145deg, #ffffff, #f0f4f8);
        border-radius: 25px; padding: 25px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.8);
        margin-bottom: 20px;
    }
    .balance-amount { color: #1c1c1e; font-size: 32px; font-weight: 800; letter-spacing: -1px; margin: 10px 0; }
    
    .stat-container { display: flex; gap: 10px; border-top: 1px solid rgba(0,0,0,0.05); padding-top: 20px; }
    .stat-box { flex: 1; padding: 12px; border-radius: 15px; background: rgba(255,255,255,0.6); border-left: 4px solid #ddd; }
    .stat-inc { border-left-color: #34C759; }
    .stat-exp { border-left-color: #FF3B30; }

    .grid-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 25px; }
    .grid-btn {
        background: white; border-radius: 18px; padding: 18px; 
        text-align: center; text-decoration: none !important; 
        color: #1c1c1e !important; font-weight: 700; font-size: 15px;
        border: 1px solid #f1f3f5; box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
        display: block;
    }
    .grid-btn:hover {
        transform: translateY(-5px);
        border-color: #007AFF;
        box-shadow: 0 8px 20px rgba(0,122,255,0.15);
    }

    /* 🔥 IMPROVED COLOR SHADOW ACTIVITY CARDS */
    .activity-container {
        background: white; border-radius: 18px; margin-bottom: 16px;
        padding: 15px 15px 15px 22px; position: relative;
        display: flex; align-items: center; justify-content: space-between;
        border: 1px solid rgba(255,255,255,0.7);
        transition: 0.3s ease;
    }
    
    /* Dynamic Shadows via Classes */
    .shadow-income {
        box-shadow: 0 8px 20px rgba(52, 199, 89, 0.12);
    }
    .shadow-expense {
        box-shadow: 0 8px 20px rgba(255, 59, 48, 0.12);
    }

    .v-line { position: absolute; left: 0; top: 0; bottom: 0; width: 6px; border-radius: 6px 0 0 6px; }
    .bg-income { background-color: #34C759; }
    .bg-expense { background-color: #FF3B30; }

    [data-testid="column"] {
        display: flex; align-items: center; justify-content: flex-end; gap: 4px !important;
    }
    
    /* FAB */
    .fab-wrapper { position: fixed; bottom: 25px; right: 20px; z-index: 9999; }
    .fab-main { 
        width: 60px; height: 60px; background: linear-gradient(135deg, #007AFF 0%, #0056b3 100%);
        border-radius: 20px; display: flex; justify-content: center; align-items: center; 
        color: white; font-size: 28px; box-shadow: 0 10px 20px rgba(0,122,255,0.3);
    }
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
    st.error("Sheet Connection Error"); st.stop()

q = st.query_params
form_type, edit_idx = q.get("form"), q.get("edit")

st.markdown('<div class="header-wrapper"><h1>FinanceFlow</h1></div>', unsafe_allow_html=True)

# --- 5. HOME PAGE ---
if not form_type and not edit_idx:
    if not df.empty:
        t_inc, t_exp = df[df['Type'] == 'Income']['Amount'].sum(), df[df['Type'] == 'Expense']['Amount'].sum()
        curr_bal = opening_bal + t_inc - t_exp
        st.markdown(f'<div class="premium-card"><div class="balance-label">Net Balance</div><div class="balance-amount">LKR {curr_bal:,.2f}</div><div class="stat-container"><div class="stat-box stat-inc"><div class="stat-title">Income</div><div class="stat-value" style="color:#34C759">+{t_inc:,.0f}</div></div><div class="stat-box stat-exp"><div class="stat-title">Expense</div><div class="stat-value" style="color:#FF3B30">-{t_exp:,.0f}</div></div></div></div>', unsafe_allow_html=True)

    st.markdown('<div class="grid-container"><a href="./?form=Income" target="_self" class="grid-btn">💰 Income</a><a href="./?form=Expense" target="_self" class="grid-btn">💸 Expense</a><a href="./?form=Transfer" target="_self" class="grid-btn">🔄 Transfer</a><a href="./?form=History" target="_self" class="grid-btn">📜 History</a></div>', unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<h3 style="font-size:18px; font-weight:700; margin-bottom:15px;">Recent Activity</h3>', unsafe_allow_html=True)
        recent_items = df.tail(10).iloc[::-1]
        for idx_row, row in recent_items.iterrows():
            is_income = row['Type'] == 'Income'
            v_line_color = "bg-income" if is_income else "bg-expense"
            shadow_class = "shadow-income" if is_income else "shadow-expense"
            text_color = "#34C759" if is_income else "#FF3B30"
            prefix = "+" if is_income else "-"
            
            # Applying dynamic shadow class here
            st.markdown(f'<div class="activity-container {shadow_class}"><div class="v-line {v_line_color}"></div>', unsafe_allow_html=True)
            
            c_left, c_right = st.columns([0.65, 0.35])
            with c_left:
                st.markdown(f"<b>{row['Category']}</b><br><small style='color:#8e8e93'>{row['Date']}</small>", unsafe_allow_html=True)
            with c_right:
                st.markdown(f"<div style='font-weight:800; text-align:right; color:{text_color}; margin-bottom:5px;'>{prefix} {row['Amount']:,.0f}</div>", unsafe_allow_html=True)
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("📝", key=f"e_{idx_row}"): st.query_params.update(edit=idx_row); st.rerun()
                with btn_col2:
                    if st.button("🗑️", key=f"d_{idx_row}"):
                        worksheet.delete_rows(int(idx_row)+2)
                        st.cache_data.clear(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. FORMS ---
elif form_type or edit_idx:
    is_edit = edit_idx is not None
    row_data = df.loc[int(edit_idx)] if is_edit else None
    t = form_type if not is_edit else row_data['Type']
    st.markdown(f'<div class="premium-card"><h3>📝 {t}</h3></div>', unsafe_allow_html=True)
    f_date = st.date_input("Date", date.fromisoformat(str(row_data['Date'])) if is_edit else date.today())
    f_cat = st.selectbox("Category", categories, index=categories.index(row_data['Category']) if is_edit and row_data['Category'] in categories else 0)
    f_amt = st.number_input("Amount", min_value=0.0, value=float(row_data['Amount']) if is_edit else 0.0)
    if st.button("Confirm ✅", use_container_width=True):
        new_row = [str(f_date), f_cat, f_amt, "", t, "Cash", "Bank", ""]
        if is_edit: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [new_row])
        else: worksheet.append_row(new_row)
        st.cache_data.clear(); st.query_params.clear(); st.rerun()
    if st.button("Back 🏠", use_container_width=True): st.query_params.clear(); st.rerun()

# --- 9. FAB ---
st.markdown("""<div class="fab-wrapper"><div class="fab-list"><a href="./" target="_self" class="fab-item"><span class="fab-label">Home</span><div class="fab-icon" style="background:#1c1c1e;">🏠</div></a><a href="./?form=Income" target="_self" class="fab-item"><span class="fab-label">Income</span><div class="fab-icon" style="background:#34C759;">➕</div></a><a href="./?form=Expense" target="_self" class="fab-item"><span class="fab-label">Expense</span><div class="fab-icon" style="background:#FF3B30;">➖</div></a></div><div class="fab-main">+</div></div>""", unsafe_allow_html=True)
