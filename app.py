import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Pro", layout="wide")

# --- 2. 🎨 ULTIMATE PREMIUM UI CSS (With Mouse Over Effects) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #fcfcfd; }

    /* Header */
    .header-wrapper {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
        padding: 45px 20px; color: white; border-radius: 0 0 35px 35px;
        text-align: center; margin: -65px -20px 30px -20px;
        box-shadow: 0 12px 30px rgba(0,122,255,0.2);
    }

    /* Cards */
    .main-card {
        background: white; padding: 25px; border-radius: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 25px;
        border: 1px solid #f1f3f5;
    }

    /* 🔥 Main Grid Buttons Hover Effect */
    .grid-btn {
        background: white; border-radius: 20px; padding: 20px; 
        text-align: center; text-decoration: none !important; 
        color: #1c1c1e !important; font-weight: 700; 
        border: 1px solid #f1f3f5; display: block;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .grid-btn:hover {
        border-color: #007AFF;
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,122,255,0.1);
        background-color: #fbfcfe;
    }

    /* Activity Container Hover */
    .activity-container {
        background: white; border-radius: 18px; margin-bottom: 12px;
        display: flex; align-items: center; justify-content: space-between;
        transition: 0.3s ease; border: 1px solid #f8f9fa;
        overflow: hidden; position: relative;
        padding: 15px 20px 15px 28px;
    }
    .activity-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.05);
    }
    .v-line { position: absolute; left: 0; top: 0; bottom: 0; width: 10px; }
    .bg-income { background-color: #34C759; }
    .bg-expense { background-color: #FF3B30; }

    /* 🔥 Action Buttons Hover (Save, Home, etc.) */
    div.stButton > button {
        border-radius: 15px !important; width: 100% !important; height: 50px !important;
        font-weight: 700 !important; transition: all 0.3s ease !important; border: none !important;
    }

    /* Save Button Hover */
    div.stButton > button:contains("Save"), div.stButton > button:contains("Add"), div.stButton > button:contains("Update") {
        background-color: #007AFF !important; color: white !important;
    }
    div.stButton > button:contains("Save"):hover, div.stButton > button:contains("Add"):hover, div.stButton > button:contains("Update"):hover {
        background-color: #0056b3 !important;
        box-shadow: 0 6px 20px rgba(0,86,179,0.4) !important;
        transform: scale(1.02);
    }

    /* Home/Cancel Button Hover */
    div.stButton > button:contains("Cancel"), div.stButton > button:contains("Back"), div.stButton > button:contains("Home") {
        background-color: #F2F2F7 !important; color: #1C1C1E !important;
        border: 1px solid #E5E5EA !important;
    }
    div.stButton > button:contains("Cancel"):hover, div.stButton > button:contains("Back"):hover, div.stButton > button:contains("Home"):hover {
        background-color: #e5e5ea !important;
        border-color: #d1d1d6 !important;
        transform: scale(1.02);
    }

    /* Floating Menu (+) */
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { 
        width: 60px; height: 60px; background: #007AFF; border-radius: 20px; 
        display: flex; justify-content: center; align-items: center; color: white; 
        font-size: 30px; box-shadow: 0 10px 25px rgba(0,122,255,0.4); cursor: pointer; transition: 0.3s;
    }
    .fab-main:hover { transform: rotate(90deg) scale(1.1); }
    .fab-list { display: none; flex-direction: column; gap: 10px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 10px; text-decoration: none !important; transition: 0.2s; }
    .fab-item:hover { transform: translateX(-5px); }
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

# Navigation
q = st.query_params
form_type, edit_idx = q.get("form"), q.get("edit")

st.markdown('<div class="header-wrapper"><h1>FinanceFlow</h1><p style="opacity:0.8">Smart Wealth Tracker</p></div>', unsafe_allow_html=True)

# --- 5. HOME PAGE ---
if not form_type and not edit_idx:
    if not df.empty:
        t_inc, t_exp = df[df['Type'] == 'Income']['Amount'].sum(), df[df['Type'] == 'Expense']['Amount'].sum()
        curr_bal = opening_bal + t_inc - t_exp

        st.markdown(f"""
            <div class="main-card">
                <small style="color:#8e8e93; font-weight:700; text-transform:uppercase;">Balance</small>
                <h1 style="color:#1c1c1e; margin:5px 0; font-size:34px;">LKR {curr_bal:,.2f}</h1>
                <div style="display:flex; gap:30px; margin-top:20px; padding-top:15px; border-top:1px solid #f8f9fa;">
                    <div><small style="color:#8e8e93">Income</small><br><b style="color:#34C759;">+ {t_inc:,.0f}</b></div>
                    <div><small style="color:#8e8e93">Expense</small><br><b style="color:#FF3B30;">- {t_exp:,.0f}</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Action Grid with CSS Class
    st.markdown('<div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:12px; margin-bottom:30px;">'
                '<a href="./?form=Income" target="_self" class="grid-btn">💰 Income</a>'
                '<a href="./?form=Expense" target="_self" class="grid-btn">💸 Expense</a>'
                '<a href="./?form=Transfer" target="_self" class="grid-btn">🔄 Transfer</a>'
                '<a href="./?form=History" target="_self" class="grid-btn">📜 History</a>'
                '</div>', unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<h3 style="font-size:18px; font-weight:700; margin-bottom:15px;">Recent Activity</h3>', unsafe_allow_html=True)
        for i, idx in enumerate(df.index[-10:][::-1]):
            row = df.loc[idx]
            v_line_color = "bg-income" if row['Type'] == 'Income' else "bg-expense"
            st.markdown(f'<div class="activity-container"><div class="v-line {v_line_color}"></div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([0.6, 0.25, 0.07, 0.07])
            with c1: st.markdown(f"<b>{row['Category']}</b><br><small style='color:#8e8e93'>{row['Date']}</small>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div style='font-weight:700; text-align:right; margin-top:8px;'>{row['Amount']:,.0f}</div>", unsafe_allow_html=True)
            with c3: 
                if st.button("📝", key=f"e_{idx}"): st.query_params.update(edit=idx); st.rerun()
            with c4:
                if st.button("🗑️", key=f"d_{idx}"): worksheet.delete_rows(int(idx)+2); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. FORMS ---
elif form_type in ["Income", "Expense", "Transfer"] or edit_idx:
    t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    st.markdown(f'<div class="main-card"><h3>📝 Add {t}</h3></div>', unsafe_allow_html=True)
    f_date = st.date_input("Date", date.today())
    f_cat = st.selectbox("Category", categories)
    f_amt = st.number_input("Amount", min_value=0.0)
    f_desc = st.text_input("Note")
    
    st.markdown("<br>", unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    with c_btn1:
        if st.button("Save Entry ✅"):
            r = [f"{f_date} {datetime.now().strftime('%H:%M:%S')}", f_cat, f_amt, f_desc, t, "Cash", "Bank", ""]
            if edit_idx: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [r])
            else: worksheet.append_row(r)
            st.query_params.clear(); st.rerun()
    with c_btn2:
        if st.button("Cancel ❌"): st.query_params.clear(); st.rerun()
    with c_btn3:
        if st.button("Home 🏠"): st.query_params.clear(); st.rerun()

# --- 7. SETTINGS ---
elif form_type == "ManageCats":
    st.markdown('<div class="main-card"><h3>⚙️ Settings</h3></div>', unsafe_allow_html=True)
    new_ob = st.number_input("Opening Balance", value=opening_bal)
    if st.button("Update Balance 💰"): cat_sheet.update_acell('B1', new_ob); st.rerun()
    st.markdown("#### Categories")
    new_cat = st.text_input("New Category")
    if st.button("Add Category ➕"):
        if new_cat: cat_sheet.append_row([new_cat]); st.rerun()
    for c in categories:
        col1, col2 = st.columns([0.85, 0.15])
        col1.markdown(f"<div style='padding:12px; background:#f8f9fa; border-radius:12px; margin-bottom:5px;'>{c}</div>", unsafe_allow_html=True)
        if col2.button("❌", key=f"del_{c}"):
            cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
    if st.button("Back to Home 🏠"): st.query_params.clear(); st.rerun()

# --- 8. HISTORY ---
elif form_type == "History":
    st.markdown('<div class="main-card"><h3>📜 History</h3></div>', unsafe_allow_html=True)
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("Back Home 🏠"): st.query_params.clear(); st.rerun()

# --- 9. FLOATING ACTION MENU ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-list">
            <a href="./" target="_self" class="fab-item"><span class="fab-label">Home</span><div class="fab-icon" style="background:#000000;">🏠</div></a>
            <a href="./?form=History" target="_self" class="fab-item"><span class="fab-label">History</span><div class="fab-icon" style="background:#007AFF;">📜</div></a>
            <a href="./?form=ManageCats" target="_self" class="fab-item"><span class="fab-label">Settings</span><div class="fab-icon" style="background:#6c757d;">⚙️</div></a>
            <a href="./?form=Transfer" target="_self" class="fab-item"><span class="fab-label">Transfer</span><div class="fab-icon" style="background:#fd7e14;">🔄</div></a>
            <a href="./?form=Income" target="_self" class="fab-item"><span class="fab-label">Income</span><div class="fab-icon" style="background:#28a745;">➕</div></a>
            <a href="./?form=Expense" target="_self" class="fab-item"><span class="fab-label">Expense</span><div class="fab-icon" style="background:#dc3545;">➖</div></a>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
