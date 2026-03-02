import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Pro", layout="wide")

# --- 2. 🎨 THE "ULTRA MODERN" CSS ---
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

    /* 🔥 STYLING THE SIDEBAR AS A FLOATING MENU */
    [data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #eee !important;
    }
    
    /* Grid Buttons for Home */
    .grid-btn {
        background: white; border-radius: 20px; padding: 20px; text-align: center;
        text-decoration: none !important; color: #1c1c1e !important; font-weight: 700; 
        border: 1px solid #f1f3f5; display: block; transition: all 0.3s ease;
    }
    .grid-btn:hover { border-color: #007AFF; transform: translateY(-5px); box-shadow: 0 12px 25px rgba(0,122,255,0.1); }

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
    </style>
    """, unsafe_allow_html=True)

# --- 3. Google Sheets Connection ---
try:
    creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet, cat_sheet = sh.worksheet("Sheet1"), sh.worksheet("Categories")
    
    try: opening_bal = float(cat_sheet.acell('B1').value.replace(',', ''))
    except: opening_bal = 0.0
    
    categories = sorted(list(set([row['CategoryName'] for row in cat_sheet.get_all_records() if row['CategoryName']])))
    df = pd.DataFrame(worksheet.get_all_records())
    if not df.empty: df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except Exception as e: st.error(f"Error: {e}"); st.stop()

# --- 4. NAVIGATION LOGIC (The Fixed Way) ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Sidebar Menu (පැත්තෙන් එන ලස්සන Floating Menu එකක් වගේ)
with st.sidebar:
    st.markdown("### 🚀 Quick Menu")
    if st.button("🏠 Home", use_container_width=True): st.session_state.page = "Home"; st.rerun()
    if st.button("💰 Add Income", use_container_width=True): st.session_state.page = "Income"; st.rerun()
    if st.button("💸 Add Expense", use_container_width=True): st.session_state.page = "Expense"; st.rerun()
    if st.button("🔄 Transfer", use_container_width=True): st.session_state.page = "Transfer"; st.rerun()
    if st.button("📜 History", use_container_width=True): st.session_state.page = "History"; st.rerun()
    if st.button("⚙️ Settings", use_container_width=True): st.session_state.page = "Settings"; st.rerun()

st.markdown('<div class="header-wrapper"><h1>FinanceFlow</h1><p style="opacity:0.8">Smart Wealth Tracker</p></div>', unsafe_allow_html=True)

# --- 5. HOME PAGE ---
if st.session_state.page == "Home":
    if not df.empty:
        t_inc, t_exp = df[df['Type'] == 'Income']['Amount'].sum(), df[df['Type'] == 'Expense']['Amount'].sum()
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

    # Grid Links (Home page buttons also updated to session state)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💰 Income", use_container_width=True): st.session_state.page = "Income"; st.rerun()
        if st.button("🔄 Transfer", use_container_width=True): st.session_state.page = "Transfer"; st.rerun()
    with c2:
        if st.button("💸 Expense", use_container_width=True): st.session_state.page = "Expense"; st.rerun()
        if st.button("📜 History", use_container_width=True): st.session_state.page = "History"; st.rerun()

    if not df.empty:
        st.markdown('<h3 style="font-size:20px; font-weight:700; margin: 20px 0 15px 0;">Recent Activity</h3>', unsafe_allow_html=True)
        for i, idx in enumerate(df.index[-10:][::-1]):
            row = df.loc[idx]
            v_line_color = "bg-income" if row['Type'] == 'Income' else "bg-expense"
            st.markdown(f'<div class="activity-container"><div class="v-line {v_line_color}"></div>', unsafe_allow_html=True)
            col1, col2 = st.columns([0.8, 0.2])
            with col1: st.markdown(f"<b>{row['Category']}</b><br><small style='color:#8e8e93'>{row['Date']} - {row['Amount']:,.0f}</small>", unsafe_allow_html=True)
            with col2: 
                if st.button("🗑️", key=f"d_{idx}"): worksheet.delete_rows(int(idx)+2); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. OTHER PAGES (Sample Logic) ---
elif st.session_state.page in ["Income", "Expense", "Transfer"]:
    st.markdown(f'<div class="main-card"><h3>📝 Add {st.session_state.page}</h3></div>', unsafe_allow_html=True)
    # Form fields can go here...
    if st.button("Back to Home 🏠"): st.session_state.page = "Home"; st.rerun()

elif st.session_state.page == "History":
    st.markdown('<div class="main-card"><h3>📜 Transaction History</h3></div>', unsafe_allow_html=True)
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("Back to Home 🏠"): st.session_state.page = "Home"; st.rerun()

elif st.session_state.page == "Settings":
    st.markdown('<div class="main-card"><h3>⚙️ Settings</h3></div>', unsafe_allow_html=True)
    # Settings content...
    if st.button("Back to Home 🏠"): st.session_state.page = "Home"; st.rerun()
