import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
import time

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Pro", layout="wide")

# --- 2. 🎨 MOBILE-RESPONSIVE PREMIUM UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        background-color: #f8f9fc; 
    }

    /* Header Styling */
    .header-wrapper {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
        padding: 40px 15px; color: white; border-radius: 0 0 35px 35px;
        text-align: center; margin: -65px -20px 25px -20px;
        box-shadow: 0 10px 30px rgba(0,122,255,0.2);
    }

    /* Premium Balance Card - Responsive Font Sizes */
    .premium-card {
        background: linear-gradient(145deg, #ffffff, #f0f4f8);
        border-radius: 25px; padding: 25px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.8);
        margin-bottom: 20px;
    }
    .balance-label { color: #8E8E93; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .balance-amount { 
        color: #1c1c1e; font-size: calc(24px + 1.5vw); font-weight: 800; 
        letter-spacing: -1px; margin: 10px 0 20px 0; 
    }
    
    .stat-container { display: flex; gap: 15px; border-top: 1px solid rgba(0,0,0,0.05); padding-top: 20px; }
    .stat-box { flex: 1; padding: 12px; border-radius: 15px; background: rgba(255,255,255,0.6); border-left: 4px solid #ddd; }
    .stat-inc { border-left-color: #34C759; }
    .stat-exp { border-left-color: #FF3B30; }
    .stat-title { color: #8E8E93; font-size: 11px; font-weight: 600; }
    .stat-value { font-size: 16px; font-weight: 700; }

    /* Action Grid - Responsive 2 columns */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px; margin-bottom: 25px;
    }
    .grid-btn {
        background: white; border-radius: 18px; padding: 15px; 
        text-align: center; text-decoration: none !important; 
        color: #1c1c1e !important; font-weight: 700; font-size: 14px;
        border: 1px solid #f1f3f5; transition: 0.3s;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    .grid-btn:hover { border-color: #007AFF; transform: translateY(-3px); }

    /* Recent Activity - Mobile Optimized */
    .activity-container {
        background: white; border-radius: 18px; margin-bottom: 12px;
        padding: 15px 15px 15px 22px; position: relative;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); border: 1px solid #f8f9fa;
    }
    .v-line { position: absolute; left: 0; top: 0; bottom: 0; width: 6px; }
    .bg-income { background-color: #34C759; }
    .bg-expense { background-color: #FF3B30; }

    /* FAB - Better Positioning for Mobile */
    .fab-wrapper { position: fixed; bottom: 25px; right: 20px; z-index: 9999; }
    .fab-main { 
        width: 60px; height: 60px; background: linear-gradient(135deg, #007AFF 0%, #0056b3 100%);
        border-radius: 20px; display: flex; justify-content: center; align-items: center; 
        color: white; font-size: 28px; box-shadow: 0 10px 20px rgba(0,122,255,0.3);
    }
    .fab-list { display: none; flex-direction: column; gap: 10px; align-items: flex-end; margin-bottom: 15px; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 10px; text-decoration: none !important; }
    .fab-label { background: white; padding: 6px 12px; border-radius: 10px; font-size: 12px; font-weight: 600; color: #1c1c1e; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .fab-icon { width: 44px; height: 44px; border-radius: 14px; display: flex; justify-content: center; align-items: center; color: white; font-size: 18px; }

    /* Hide standard streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Media Query for very small screens */
    @media (max-width: 480px) {
        .stat-container { flex-direction: column; }
        .balance-amount { font-size: 28px; }
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
    st.error("Connection lost. Please refresh."); st.stop()

q = st.query_params
form_type, edit_idx = q.get("form"), q.get("edit")

st.markdown('<div class="header-wrapper"><h1>FinanceFlow</h1><p style="opacity:0.8; font-size:14px;">Smart Wealth Tracker</p></div>', unsafe_allow_html=True)

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

    # Responsive Action Grid
    st.markdown("""
        <div class="grid-container">
            <a href="./?form=Income" target="_self" class="grid-btn">💰 Income</a>
            <a href="./?form=Expense" target="_self" class="grid-btn">💸 Expense</a>
            <a href="./?form=Transfer" target="_self" class="grid-btn">🔄 Transfer</a>
            <a href="./?form=History" target="_self" class="grid-btn">📜 History</a>
        </div>
    """, unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<h3 style="font-size:18px; font-weight:700; margin-bottom:15px; color:#1c1c1e;">Recent Activity</h3>', unsafe_allow_html=True)
        recent_items = df.tail(10).iloc[::-1]
        for idx_row, row in recent_items.iterrows():
            v_line_color = "bg-income" if row['Type'] == 'Income' else "bg-expense"
            
            # Use Streamlit columns for buttons to ensure they work
            st.markdown(f'<div class="activity-container"><div class="v-line {v_line_color}"></div>', unsafe_allow_html=True)
            col_info, col_amt, col_btns = st.columns([0.5, 0.25, 0.25])
            with col_info:
                st.markdown(f"<b>{row['Category']}</b><br><small style='color:#8e8e93'>{row['Date']}</small>", unsafe_allow_html=True)
            with col_amt:
                st.markdown(f"<div style='font-weight:700; text-align:right; margin-top:5px;'>{row['Amount']:,.0f}</div>", unsafe_allow_html=True)
            with col_btns:
                sub_c1, sub_c2 = st.columns(2)
                with sub_c1:
                    if st.button("📝", key=f"ed_{idx_row}"):
                        st.query_params.update(edit=idx_row); st.rerun()
                with sub_c2:
                    if st.button("🗑️", key=f"dl_{idx_row}"):
                        worksheet.delete_rows(int(idx_row)+2)
                        st.cache_data.clear(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. FORMS (Responsive) ---
elif form_type or edit_idx:
    is_edit = edit_idx is not None
    row_data = df.loc[int(edit_idx)] if is_edit else None
    title = form_type if not is_edit else row_data['Type']
    
    st.markdown(f'<div class="premium-card"><h3 style="margin:0; font-size:18px;">📝 {title}</h3></div>', unsafe_allow_html=True)
    
    with st.container():
        f_date = st.date_input("Date", date.fromisoformat(str(row_data['Date'])) if is_edit else date.today())
        f_cat = st.selectbox("Category", categories, index=categories.index(row_data['Category']) if is_edit and row_data['Category'] in categories else 0)
        f_amt = st.number_input("Amount", min_value=0.0, value=float(row_data['Amount']) if is_edit else 0.0)
        f_desc = st.text_input("Note", value=row_data['Note'] if is_edit else "")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Confirm ✅", use_container_width=True):
            new_data = [str(f_date), f_cat, f_amt, f_desc, title, "Cash", "Bank", ""]
            if is_edit: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [new_data])
            else: worksheet.append_row(new_data)
            st.cache_data.clear(); st.query_params.clear(); st.rerun()
        
        if st.button("Go Back ⬅️", use_container_width=True):
            st.query_params.clear(); st.rerun()

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
