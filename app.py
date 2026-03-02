import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Pro", layout="wide")

# --- 2. 🎨 CLEAN MODERN UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f4f7fa; }

    /* Header */
    .header-wrapper {
        background: linear-gradient(135deg, #007AFF 0%, #0056D6 100%);
        padding: 45px 15px; color: white; border-radius: 0 0 40px 40px;
        text-align: center; margin: -65px -20px 25px -20px;
        box-shadow: 0 10px 30px rgba(0,122,255,0.15);
    }

    /* Main Balance Card */
    .premium-card {
        background: white; border-radius: 30px; padding: 30px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.03);
        border: 1px solid rgba(0,0,0,0.02);
        margin-bottom: 25px;
    }
    .balance-amount { color: #1c1c1e; font-size: 38px; font-weight: 800; letter-spacing: -1.5px; margin: 10px 0; }
    
    .stat-container { display: flex; gap: 12px; margin-top: 20px; }
    .stat-box { flex: 1; padding: 15px; border-radius: 20px; background: #f9fafb; border: 1px solid #f1f3f5; }
    .stat-inc-val { color: #34C759; font-weight: 700; font-size: 18px; }
    .stat-exp-val { color: #FF3B30; font-weight: 700; font-size: 18px; }

    /* Action Grid */
    .grid-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 30px; }
    .grid-btn {
        background: white; border-radius: 20px; padding: 18px; 
        text-align: center; text-decoration: none !important; 
        color: #1c1c1e !important; font-weight: 700; border: 1px solid #edf2f7;
        transition: 0.3s ease;
    }
    .grid-btn:hover { border-color: #007AFF; transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,122,255,0.1); }

    /* Activity List - Clean Look */
    .activity-container {
        background: white; border-radius: 22px; margin-bottom: 12px;
        padding: 16px 18px 16px 28px; position: relative;
        border: 1px solid #f1f3f5; display: flex; align-items: center; justify-content: space-between;
        transition: 0.2s;
    }
    .activity-container:hover { border-color: #e2e8f0; }
    .v-line { position: absolute; left: 0; top: 15px; bottom: 15px; width: 6px; border-radius: 0 10px 10px 0; }
    .bg-income { background-color: #34C759; }
    .bg-expense { background-color: #FF3B30; }

    /* Mobile Buttons Force Inline */
    [data-testid="column"] { display: flex; align-items: center; justify-content: flex-end; gap: 8px !important; }

    /* NEW PREMIUM FAB */
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 1000; }
    .fab-main { 
        width: 65px; height: 65px; background: #007AFF;
        border-radius: 22px; display: flex; justify-content: center; align-items: center; 
        color: white; font-size: 32px; box-shadow: 0 12px 24px rgba(0,122,255,0.4);
        cursor: pointer; transition: 0.4s;
    }
    .fab-list { display: none; flex-direction: column; gap: 12px; align-items: flex-end; margin-bottom: 15px; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 12px; text-decoration: none !important; }
    .fab-label { background: #1c1c1e; padding: 8px 16px; border-radius: 12px; font-size: 13px; font-weight: 600; color: white; }
    .fab-icon { width: 48px; height: 48px; border-radius: 16px; display: flex; justify-content: center; align-items: center; color: white; font-size: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Data Connection ---
@st.cache_resource
def get_gsheet_client():
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds)

try:
    client = get_gsheet_client()
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet, cat_sheet = sh.worksheet("Sheet1"), sh.worksheet("Categories")

    @st.cache_data(ttl=30)
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
        st.markdown(f"""
            <div class="premium-card">
                <small style="color:#8E8E93; font-weight:700; text-transform:uppercase;">Current Balance</small>
                <div class="balance-amount">LKR {curr_bal:,.2f}</div>
                <div class="stat-container">
                    <div class="stat-box"><small>Income</small><div class="stat-inc-val">+{t_inc:,.0f}</div></div>
                    <div class="stat-box"><small>Expense</small><div class="stat-exp-val">-{t_exp:,.0f}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="grid-container"><a href="./?form=Income" target="_self" class="grid-btn">💰 Income</a><a href="./?form=Expense" target="_self" class="grid-btn">💸 Expense</a><a href="./?form=Transfer" target="_self" class="grid-btn">🔄 Transfer</a><a href="./?form=History" target="_self" class="grid-btn">📜 History</a></div>', unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<p style="font-weight:700; color:#1c1c1e; margin-bottom:15px; font-size:18px;">Recent Activity</p>', unsafe_allow_html=True)
        recent_items = df.tail(10).iloc[::-1]
        for idx_row, row in recent_items.iterrows():
            is_inc = row['Type'] == 'Income'
            v_color, t_color, sym = ("bg-income", "#34C759", "+") if is_inc else ("bg-expense", "#FF3B30", "-")
            
            st.markdown(f'<div class="activity-container"><div class="v-line {v_color}"></div>', unsafe_allow_html=True)
            c1, c2 = st.columns([0.65, 0.35])
            with c1: st.markdown(f"<b>{row['Category']}</b><br><small style='color:#8e8e93'>{row['Date']}</small>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div style='font-weight:700; text-align:right; color:{t_color}'>{sym} {row['Amount']:,.0f}</div>", unsafe_allow_html=True)
                sc1, sc2 = st.columns(2)
                with sc1:
                    if st.button("📝", key=f"e_{idx_row}"): st.query_params.update(edit=idx_row); st.rerun()
                with sc2:
                    if st.button("🗑️", key=f"d_{idx_row}"): worksheet.delete_rows(int(idx_row)+2); st.cache_data.clear(); st.rerun()
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
    
    if st.button("Save ✅", use_container_width=True):
        new_row = [str(f_date), f_cat, f_amt, "", t, "Cash", "Bank", ""]
        if is_edit: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [new_row])
        else: worksheet.append_row(new_row)
        st.cache_data.clear(); st.query_params.clear(); st.rerun()
    if st.button("Back 🏠", use_container_width=True): st.query_params.clear(); st.rerun()

# --- 9. NEW PREMIUM FAB ---
st.markdown("""
<div class="fab-wrapper">
    <div class="fab-list">
        <a href="./" target="_self" class="fab-item"><span class="fab-label">Home</span><div class="fab-icon" style="background:#1c1c1e;">🏠</div></a>
        <a href="./?form=Income" target="_self" class="fab-item"><span class="fab-label">Income</span><div class="fab-icon" style="background:#34C759;">➕</div></a>
        <a href="./?form=Expense" target="_self" class="fab-item"><span class="fab-label">Expense</span><div class="fab-icon" style="background:#FF3B30;">➖</div></a>
    </div>
    <div class="fab-main">+</div>
</div>
""", unsafe_allow_html=True)
