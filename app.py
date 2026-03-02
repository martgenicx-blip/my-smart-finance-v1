import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Pro", layout="wide")

# --- 2. 🎨 PREMIUM MODERN UI & VERTICAL COLOR BARS ---
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

    /* Summary Card */
    .main-card {
        background: white; padding: 25px; border-radius: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-bottom: 20px;
        border: 1px solid #f1f3f5;
    }

    /* 🔥 MODERN RECENT ACTIVITY (Fixed Vertical Left Line) */
    .activity-container {
        background: white; border-radius: 16px; margin-bottom: 12px;
        display: flex; align-items: center; justify-content: space-between;
        transition: 0.3s ease; border: 1px solid #f8f9fa;
        box-shadow: 0 2px 8px rgba(0,0,0,0.01);
        overflow: hidden; position: relative;
        padding: 12px 18px 12px 25px; /* Left padding is more for the line */
    }
    .activity-container:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.05); }
    
    /* The Vertical Line inside the row */
    .v-line {
        position: absolute; left: 0; top: 0; bottom: 0;
        width: 8px; /* Thick vertical line */
    }
    .bg-income { background-color: #34C759; }
    .bg-expense { background-color: #FF3B30; }
    .bg-transfer { background-color: #AF52DE; }

    /* Floating Action Menu */
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

    /* Button Fixes */
    div.stButton > button {
        border: none !important; background: #f1f3f5 !important;
        border-radius: 12px !important; width: 38px !important; height: 38px !important;
        color: #444 !important; transition: 0.2s; padding: 0 !important;
    }
    div.stButton > button:hover { background: #e2e6ea !important; color: #007AFF !important; }
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

    # Recent Activity
    if not df.empty:
        st.markdown('<h3 style="font-size:18px; font-weight:700; margin-bottom:15px; color:#1c1c1e;">Recent Activity</h3>', unsafe_allow_html=True)
        for i, idx in enumerate(df.index[-10:][::-1]):
            row = df.loc[idx]
            is_inc = row['Type'] == 'Income'
            v_line_color = "bg-income" if is_inc else "bg-expense"
            amt_color = "#34C759" if is_inc else "#FF3B30"
            
            # 🔥 Row with Vertical Line at the absolute left
            st.markdown(f'''
                <div class="activity-container">
                    <div class="v-line {v_line_color}"></div>
            ''', unsafe_allow_html=True)
            
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
    if st.button("➕ Add Category"):
        if new_cat: cat_sheet.append_row([new_cat]); st.rerun()
    for c in categories:
        col1, col2 = st.columns([0.85, 0.15])
        col1.markdown(f"<div style='padding:12px; background:#f8f9fa; border-radius:12px; margin-bottom:5px;'>{c}</div>", unsafe_allow_html=True)
        if col2.button("❌", key=f"del_{c}"):
            cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
    if st.button("⬅️ Back"): st.query_params.clear(); st.rerun()

# --- 7. HISTORY & FORMS ---
elif form_type == "History":
    st.markdown('<div class="main-card"><h3>📜 History</h3></div>', unsafe_allow_html=True)
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("⬅️ Back Home"): st.query_params.clear(); st.rerun()

elif form_type in ["Income", "Expense", "Transfer"] or edit_idx:
    t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    st.markdown(f'<div class="main-card"><h3>📝 {t} Entry</h3></div>', unsafe_allow_html=True)
    f_date, f_cat = st.date_input("Date", date.today()), st.selectbox("Category", categories)
    f_amt, f_desc = st.number_input("Amount", min_value=0.0), st.text_input("Note")
    st.write(" "); b1, b2 = st.columns([0.2, 0.8])
    with b1:
        if st.button("Save"):
            r = [f"{f_date} {datetime.now().strftime('%H:%M:%S')}", f_cat, f_amt, f_desc, t, "Cash", "Bank", ""]
            (worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [r]) if edit_idx else worksheet.append_row(r))
            st.query_params.clear(); st.rerun()
    with b2:
        if st.button("Cancel"): st.query_params.clear(); st.rerun()

# --- 8. 🔥 THE FLOATING ACTION MENU (+) ---
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
