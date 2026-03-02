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

    .main-card {
        background: white; padding: 25px; border-radius: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04); margin-bottom: 25px;
        border: 1px solid rgba(0,0,0,0.02);
    }

    /* Primary Grid Links */
    .grid-btn {
        background: white; border-radius: 20px; padding: 20px; 
        text-align: center; text-decoration: none !important; 
        color: #1c1c1e !important; font-weight: 700; 
        border: 1px solid #f1f3f5; display: block;
        transition: all 0.3s ease;
    }
    .grid-btn:hover {
        border-color: #007AFF; transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(0,122,255,0.1);
    }

    /* Button Styling */
    div.stButton > button {
        border-radius: 15px !important; width: 100% !important; height: 50px !important;
        font-weight: 700 !important; transition: all 0.3s ease !important;
    }
    div.stButton > button:hover { transform: scale(1.02); }

    /* Recent Activity */
    .activity-container {
        background: white; border-radius: 18px; margin-bottom: 12px;
        display: flex; align-items: center; justify-content: space-between;
        transition: 0.3s ease; border: 1px solid #f8f9fa;
        overflow: hidden; position: relative; padding: 15px 20px 15px 28px;
    }
    .v-line { position: absolute; left: 0; top: 0; bottom: 0; width: 10px; }
    .bg-income { background-color: #34C759; }
    .bg-expense { background-color: #FF3B30; }

    /* FAB DESIGN */
    .fab-wrapper { position: fixed; bottom: 35px; right: 30px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end; gap: 15px; }
    .fab-main { 
        width: 65px; height: 65px; background: linear-gradient(135deg, #007AFF 0%, #0056b3 100%);
        border-radius: 22px; display: flex; justify-content: center; align-items: center; 
        color: white; font-size: 32px; box-shadow: 0 12px 25px rgba(0,122,255,0.4); cursor: pointer; transition: 0.4s;
    }
    .fab-wrapper:hover .fab-main { transform: rotate(135deg); }
    .fab-list { display: none; flex-direction: column; gap: 12px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 12px; text-decoration: none !important; }
    .fab-label { background: white; padding: 8px 16px; border-radius: 12px; font-size: 14px; font-weight: 600; color: #1c1c1e; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
    .fab-icon { width: 48px; height: 48px; border-radius: 16px; display: flex; justify-content: center; align-items: center; color: white; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Google Sheets Connection with CACHING ---
# 
@st.cache_resource
def get_gsheet_client():
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds)

try:
    client = get_gsheet_client()
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet = sh.worksheet("Sheet1")
    cat_sheet = sh.worksheet("Categories")

    @st.cache_data(ttl=60) # විනාඩියක් යනකම් Data මතක තියාගන්නවා (Quota Error Fix)
    def load_data():
        df_all = pd.DataFrame(worksheet.get_all_records())
        if not df_all.empty:
            df_all['Amount'] = pd.to_numeric(df_all['Amount'], errors='coerce').fillna(0)
        
        # Categories and Opening Balance
        cats = sorted(list(set([row['CategoryName'] for row in cat_sheet.get_all_records() if row['CategoryName']])))
        try: op_bal = float(cat_sheet.acell('B1').value.replace(',', ''))
        except: op_bal = 0.0
        
        return df_all, cats, op_bal

    df, categories, opening_bal = load_data()

except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")
    st.stop()

# Navigation logic
q = st.query_params
form_type = q.get("form")
edit_idx = q.get("edit")

st.markdown('<div class="header-wrapper"><h1>FinanceFlow</h1><p style="opacity:0.8">Smart Wealth Tracker</p></div>', unsafe_allow_html=True)

# --- 5. HOME PAGE ---
if not form_type and not edit_idx:
    if not df.empty:
        t_inc = df[df['Type'] == 'Income']['Amount'].sum()
        t_exp = df[df['Type'] == 'Expense']['Amount'].sum()
        curr_bal = opening_bal + t_inc - t_exp

        st.markdown(f"""
            <div class="main-card">
                <small style="color:#8e8e93; font-weight:700; text-transform:uppercase;">Net Balance</small>
                <h1 style="color:#1c1c1e; margin:5px 0; font-size:36px;">LKR {curr_bal:,.2f}</h1>
                <div style="display:flex; gap:30px; margin-top:20px; padding-top:15px; border-top:1px solid #f8f9fa;">
                    <div><small style="color:#8e8e93">Income</small><br><b style="color:#34C759; font-size:18px;">+ {t_inc:,.0f}</b></div>
                    <div><small style="color:#8e8e93">Expenses</small><br><b style="color:#FF3B30; font-size:18px;">- {t_exp:,.0f}</b></div>
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
        st.markdown('<h3 style="font-size:20px; font-weight:700; margin-bottom:15px;">Recent Activity</h3>', unsafe_allow_html=True)
        for i, idx in enumerate(df.index[-10:][::-1]):
            row = df.loc[idx]
            v_line_color = "bg-income" if row['Type'] == 'Income' else "bg-expense"
            st.markdown(f'<div class="activity-container"><div class="v-line {v_line_color}"></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([0.7, 0.2, 0.1])
            with c1: st.markdown(f"<b>{row['Category']}</b><br><small style='color:#8e8e93'>{row['Date']}</small>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div style='font-weight:700; text-align:right; margin-top:8px;'>{row['Amount']:,.0f}</div>", unsafe_allow_html=True)
            with c3:
                if st.button("🗑️", key=f"d_{idx}"):
                    worksheet.delete_rows(int(idx)+2)
                    st.cache_data.clear() # දත්ත මැකුවම Cache එක Clear කරන්න ඕනේ
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. FORMS (Income / Expense) ---
elif form_type in ["Income", "Expense", "Transfer"]:
    st.markdown(f'<div class="main-card"><h3>📝 Add {form_type}</h3></div>', unsafe_allow_html=True)
    f_date = st.date_input("Date", date.today())
    f_cat = st.selectbox("Category", categories)
    f_amt = st.number_input("Amount", min_value=0.0)
    f_desc = st.text_input("Note")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Save Entry ✅"):
            new_row = [f"{f_date}", f_cat, f_amt, f_desc, form_type, "Cash", "Bank", ""]
            worksheet.append_row(new_row)
            st.cache_data.clear() # Save කළාම අලුත් දත්ත පේන්න Cache එක Clear කළා
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button("Cancel ❌"): st.query_params.clear(); st.rerun()
    with col3:
        if st.button("Home 🏠"): st.query_params.clear(); st.rerun()

# --- 7. HISTORY ---
elif form_type == "History":
    st.markdown('<div class="main-card"><h3>📜 Transaction History</h3></div>', unsafe_allow_html=True)
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("Back Home 🏠"): st.query_params.clear(); st.rerun()

# --- 8. SETTINGS ---
elif form_type == "ManageCats":
    st.markdown('<div class="main-card"><h3>⚙️ Settings</h3></div>', unsafe_allow_html=True)
    # (Settings UI as before)
    if st.button("Back Home 🏠"): st.query_params.clear(); st.rerun()

# --- 9. FLOATING ACTION MENU ---
# 
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
