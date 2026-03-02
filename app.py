import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Pro", layout="wide")

# --- 2. 🎨 PREMIUM MODERN UI & FLOATING MENU CSS ---
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
        box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 20px;
        border: 1px solid #f1f3f5;
    }

    /* 🔥 MODERN RECENT ACTIVITY (With Left Color Line) */
    .activity-container {
        background: white; border-radius: 18px; padding: 12px 18px; margin-bottom: 12px;
        display: flex; align-items: center; justify-content: space-between;
        transition: 0.3s ease; border: 1px solid #f8f9fa;
        box-shadow: 0 2px 8px rgba(0,0,0,0.01);
    }
    .activity-container:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.05); }
    
    .line-income { border-left: 5px solid #34C759 !important; }
    .line-expense { border-left: 5px solid #FF3B30 !important; }
    .line-transfer { border-left: 5px solid #AF52DE !important; }

    /* 🚀 FLOATING ACTION MENU (The + Button Menu) */
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { 
        width: 60px; height: 60px; background: #007AFF; border-radius: 20px; 
        display: flex; justify-content: center; align-items: center; color: white; 
        font-size: 30px; box-shadow: 0 10px 25px rgba(0,122,255,0.4); cursor: pointer; 
        transition: 0.3s;
    }
    .fab-list { display: none; flex-direction: column; gap: 10px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 10px; text-decoration: none !important; }
    .fab-label { background: white; padding: 6px 14px; border-radius: 10px; font-size: 13px; font-weight: 600; color: #333; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .fab-icon { width: 45px; height: 45px; border-radius: 15px; display: flex; justify-content: center; align-items: center; color: white; font-size: 20px; }
    .fab-main:hover { transform: rotate(45deg); }

    /* Fix Streamlit Button Backgrounds */
    div.stButton > button {
        border: none !important; background: #f1f3f5 !important;
        border-radius: 12px !important; width: 38px !important; height: 38px !important;
        color: #444 !important; transition: 0.2s; padding: 0 !important;
    }
    div.stButton > button:hover { background: #e2e6ea !important; color: #007AFF !important; }

    .action-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 25px; }
    .grid-btn { background: white; border-radius: 20px; padding: 22px; text-align: center; text-decoration: none !important; color: #1c1c1e !important; font-weight: 700; border: 1px solid #f1f3f5; transition: 0.3s; }
    .grid-btn:hover { border-color: #007AFF; transform: translateY(-3px); }
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

st.markdown('<div class="header-wrapper"><h1>FinanceFlow</h1><p style="opacity:0.8">Smart Money Tracker</p></div>', unsafe_allow_html=True)

# --- 5. HOME PAGE ---
if not form_type and not edit_idx:
    if not df.empty:
        t_inc, t_exp = df[df['Type'] == 'Income']['Amount'].sum(), df[df['Type'] == 'Expense']['Amount'].sum()
        curr_bal = opening_bal + t_inc - t_exp

        st.markdown(f"""
            <div class="main-card">
                <small style="color:#8e8e93; font-weight:700; text-transform:uppercase;">Net Worth</small>
                <h1 style="color:#1c1c1e; margin:5px 0; font-size:34px;">LKR {curr_bal:,.2f}</h1>
                <div style="display:flex; gap:30px; margin-top:20px; padding-top:15px; border-top:1px solid #f8f9fa;">
                    <div><small style="color:#8e8e93">Income</small><br><b style="color:#34C759; font-size:18px;">+ {t_inc:,.0f}</b></div>
                    <div><small style="color:#8e8e93">Expenses</small><br><b style="color:#FF3B30; font-size:18px;">- {t_exp:,.0f}</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Grid Links
    st.markdown('<div class="action-grid">'
                '<a href="./?form=Income" target="_self" class="grid-btn">💰 Income</a>'
                '<a href="./?form=Expense" target="_self" class="grid-btn">💸 Expense</a>'
                '<a href="./?form=Transfer" target="_self" class="grid-btn">🔄 Transfer</a>'
                '<a href="./?form=History" target="_self" class="grid-btn">📜 History</a>'
                '</div>', unsafe_allow_html=True)

    # Recent Activity
    if not df.empty:
        st.markdown('<h3 style="font-size:18px; font-weight:700; margin-bottom:15px;">Recent Transactions</h3>', unsafe_allow_html=True)
        for i, idx in enumerate(df.index[-8:][::-1]):
            row = df.loc[idx]
            is_inc = row['Type'] == 'Income'
            line_class = "line-income" if is_inc else "line-expense"
            amt_color = "#34C759" if is_inc else "#FF3B30"
            
            st.markdown(f'<div class="activity-container {line_class}">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([0.6, 0.25, 0.07, 0.07])
            with c1: st.markdown(f"<b>{row['Category']}</b><br><small style='color:#8e8e93'>{row['Date']}</small>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div style='color:{amt_color}; font-weight:700; text-align:right; margin-top:8px;'>{row['Amount']:,.0f}</div>", unsafe_allow_html=True)
            with c3: 
                if st.button("📝", key=f"e_{idx}"): st.query_params.update(edit=idx); st.rerun()
            with c4:
                if st.button("🗑️", key=f"d_{idx}"): worksheet.delete_rows(int(idx)+2); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. SETTINGS ---
elif form_type == "ManageCats":
    st.markdown('<div class="main-card"><h3>⚙️ Settings</h3></div>', unsafe_allow_html=True)
    new_ob = st.number_input("Opening Balance", value=opening_bal)
    if st.button("Update Balance"): cat_sheet.update_acell('B1', new_ob); st.rerun()
    
    st.markdown("#### Categories")
    new_cat = st.text_input("New Category")
    if st.button("Add"):
        if new_cat: cat_sheet.append_row([new_cat]); st.rerun()
    for c in categories:
        col1, col2 = st.columns([0.85, 0.15])
        col1.markdown(f"<div style='padding:10px; background:#f8f9fa; border-radius:10px; margin-bottom:5px;'>{c}</div>", unsafe_allow_html=True)
        if col2.button("❌", key=f"del_{c}"):
            cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
    if st.button("⬅️ Back"): st.query_params.clear(); st.rerun()

# --- 7. HISTORY ---
elif form_type == "History":
    st.markdown('<div class="main-card"><h3>📜 History</h3></div>', unsafe_allow_html=True)
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("⬅️ Back Home"): st.query_params.clear(); st.rerun()

# --- 8. FORMS (Income/Expense) ---
elif form_type in ["Income", "Expense", "Transfer"] or edit_idx:
    t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    st.markdown(f'<div class="main-card"><h3>📝 {t} Entry</h3></div>', unsafe_allow_html=True)
    f_date = st.date_input("Date", date.today())
    f_cat = st.selectbox("Category", categories)
    f_amt = st.number_input("Amount", min_value=0.0)
    f_desc = st.text_input("Note")
    st.write(" ")
    b1, b2 = st.columns([0.2, 0.8])
    with b1:
        if st.button("Save"):
            r = [f"{f_date} {datetime.now().strftime('%H:%M:%S')}", f_cat, f_amt, f_desc, t, "Cash", "Bank", ""]
            if edit_idx: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [r])
            else: worksheet.append_row(r)
            st.query_params.clear(); st.rerun()
    with b2:
        if st.button("Cancel"): st.query_params.clear(); st.rerun()

# --- 9. 🔥 THE FLOATING ACTION MENU (+) ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-list">
            <a href="./?form=History" target="_self" class="fab-item"><span class="fab-label">History</span><div class="fab-icon" style="background:#007AFF;">📜</div></a>
            <a href="./?form=ManageCats" target="_self" class="fab-item"><span class="fab-label">Settings</span><div class="fab-icon" style="background:#6c757d;">⚙️</div></a>
            <a href="./?form=Transfer" target="_self" class="fab-item"><span class="fab-label">Transfer</span><div class="fab-icon" style="background:#fd7e14;">🔄</div></a>
            <a href="./?form=Income" target="_self" class="fab-item"><span class="fab-label">Income</span><div class="fab-icon" style="background:#28a745;">➕</div></a>
            <a href="./?form=Expense" target="_self" class="fab-item"><span class="fab-label">Expense</span><div class="fab-icon" style="background:#dc3545;">➖</div></a>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
