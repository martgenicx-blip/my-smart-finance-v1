import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Elite", layout="wide")

# --- 2. 🎨 PREMIUM MODERN UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #fcfcfd; }

    /* Header Styling */
    .header-wrapper {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
        padding: 50px 20px; color: white; border-radius: 0 0 40px 40px;
        text-align: center; margin: -65px -20px 30px -20px;
        box-shadow: 0 15px 35px rgba(0,122,255,0.15);
    }

    /* Main Balance Card */
    .main-card {
        background: white; padding: 30px; border-radius: 28px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.03); margin-bottom: 25px;
        border: 1px solid #f1f3f5;
    }

    /* 🔥 MODERN RECENT ACTIVITY (Left Color Line) */
    .activity-container {
        background: white; border-radius: 20px; padding: 15px 20px; margin-bottom: 12px;
        display: flex; align-items: center; justify-content: space-between;
        transition: all 0.3s ease; border: 1px solid #f8f9fa;
        box-shadow: 0 2px 10px rgba(0,0,0,0.01);
    }
    .activity-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(0,0,0,0.05);
    }
    .line-income { border-left: 5px solid #34C759 !important; }
    .line-expense { border-left: 5px solid #FF3B30 !important; }
    .line-transfer { border-left: 5px solid #AF52DE !important; }

    /* Action Grid Icons */
    .grid-link {
        background: white; border-radius: 24px; padding: 25px; text-align: center;
        text-decoration: none !important; color: #1c1c1e !important; font-weight: 700;
        transition: 0.3s; border: 1px solid #f1f3f5; display: block;
    }
    .grid-link:hover { background: #f8f9ff; border-color: #007AFF; transform: scale(1.02); }

    /* Floating Button (Fixed) */
    .floating-btn {
        position: fixed; bottom: 35px; right: 30px; z-index: 9999;
        width: 65px; height: 65px; background: #007AFF; border-radius: 22px;
        display: flex; justify-content: center; align-items: center;
        box-shadow: 0 10px 30px rgba(0,122,255,0.4); cursor: pointer;
        transition: 0.3s; text-decoration: none !important;
    }
    .floating-btn:hover { transform: rotate(90deg) scale(1.1); background: #0056b3; }

    /* Hide Streamlit Garbage & Fix Button Logic */
    div.stButton > button {
        border: none !important; background: #f1f3f5 !important;
        border-radius: 14px !important; width: 42px !important; height: 42px !important;
        color: #444 !important; transition: 0.2s; padding: 0 !important;
    }
    div.stButton > button:hover { background: #e2e6ea !important; color: #007AFF !important; }
    
    .save-btn div.stButton > button {
        background: #007AFF !important; color: white !important;
        width: 100% !important; height: 48px !important; font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Connection ---
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

# Header
st.markdown('<div class="header-wrapper"><h1>FinanceFlow</h1><p style="opacity:0.8; font-weight:500;">Your Wealth, Simplified.</p></div>', unsafe_allow_html=True)

# --- HOME ---
if not form_type and not edit_idx:
    if not df.empty:
        t_inc, t_exp = df[df['Type'] == 'Income']['Amount'].sum(), df[df['Type'] == 'Expense']['Amount'].sum()
        curr_bal = opening_bal + t_inc - t_exp

        st.markdown(f"""
            <div class="main-card">
                <p style="color:#8e8e93; font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Net Worth</p>
                <h1 style="color:#1c1c1e; margin:0; font-size:36px;">LKR {curr_bal:,.2f}</h1>
                <div style="display:flex; gap:40px; margin-top:25px; padding-top:20px; border-top:1px solid #f8f9fa;">
                    <div><small style="color:#8e8e93; font-weight:600;">INCOME</small><br><b style="color:#34C759; font-size:20px;">+ {t_inc:,.0f}</b></div>
                    <div><small style="color:#8e8e93; font-weight:600;">EXPENSES</small><br><b style="color:#FF3B30; font-size:20px;">- {t_exp:,.0f}</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; margin-bottom:30px;">'
                '<a href="./?form=Income" target="_self" class="grid-link">💰 Income</a>'
                '<a href="./?form=Expense" target="_self" class="grid-link">💸 Expense</a>'
                '<a href="./?form=Transfer" target="_self" class="grid-link">🔄 Transfer</a>'
                '<a href="./?form=History" target="_self" class="grid-link">📜 History</a>'
                '</div>', unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<h3 style="font-size:18px; font-weight:700; margin-bottom:15px; color:#1c1c1e;">Recent Activity</h3>', unsafe_allow_html=True)
        for i, idx in enumerate(df.index[-8:][::-1]):
            row = df.loc[idx]
            is_inc = row['Type'] == 'Income'
            line_class = "line-income" if is_inc else "line-expense"
            amt_color = "#34C759" if is_inc else "#FF3B30"
            
            # Row structure
            st.markdown(f'<div class="activity-container {line_class}">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([0.6, 0.25, 0.07, 0.07])
            with c1: st.markdown(f"<b>{row['Category']}</b><br><small style='color:#8e8e93'>{row['Date']}</small>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div style='color:{amt_color}; font-weight:700; text-align:right; margin-top:8px;'>{'▲' if is_inc else '▼'} {row['Amount']:,.0f}</div>", unsafe_allow_html=True)
            with c3: 
                if st.button("📝", key=f"e_{idx}"): st.query_params.update(edit=idx); st.rerun()
            with c4:
                if st.button("🗑️", key=f"d_{idx}"): worksheet.delete_rows(int(idx)+2); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- SETTINGS / ADD CATEGORY ---
elif form_type == "ManageCats":
    st.markdown('<div class="main-card"><h3>⚙️ Settings</h3></div>', unsafe_allow_html=True)
    
    with st.expander("💰 Opening Balance", expanded=True):
        new_ob = st.number_input("Initial Funds (LKR)", value=opening_bal)
        if st.button("Save Balance"): cat_sheet.update_acell('B1', new_ob); st.rerun()

    st.markdown("#### 🏷️ Categories")
    new_cat = st.text_input("New Category Name")
    st.markdown('<div class="save-btn">', unsafe_allow_html=True)
    if st.button("➕ Add Category"):
        if new_cat: cat_sheet.append_row([new_cat]); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    for c in categories:
        col1, col2 = st.columns([0.85, 0.15])
        col1.markdown(f"<div style='padding:12px; background:#f8f9fa; border-radius:12px; margin-bottom:8px; font-weight:600;'>{c}</div>", unsafe_allow_html=True)
        if col2.button("❌", key=f"del_{c}"):
            cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
    if st.button("⬅️ Back"): st.query_params.clear(); st.rerun()

# --- FORMS ---
elif form_type in ["Income", "Expense", "Transfer"] or edit_idx:
    t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    st.markdown(f'<div class="main-card"><h3>📝 {t} Entry</h3></div>', unsafe_allow_html=True)
    f_date, f_cat = st.date_input("Date", date.today()), st.selectbox("Category", categories)
    f_amt, f_desc = st.number_input("Amount (LKR)", min_value=0.0), st.text_input("Note")
    st.write(" ")
    b1, b2 = st.columns([0.2, 0.8])
    with b1:
        if st.button("Save", use_container_width=True):
            r = [f"{f_date} {datetime.now().strftime('%H:%M:%S')}", f_cat, f_amt, f_desc, t, "Cash", "Bank", ""]
            (worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [r]) if edit_idx else worksheet.append_row(r))
            st.query_params.clear(); st.rerun()
    with b2:
        if st.button("Cancel"): st.query_params.clear(); st.rerun()

elif form_type == "History":
    st.markdown('<div class="main-card"><h3>📜 History</h3></div>', unsafe_allow_html=True)
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("⬅️ Back"): st.query_params.clear(); st.rerun()

# --- 🎯 FLOATING ACTION BUTTON (Fixed) ---
st.markdown('<a href="./?form=ManageCats" target="_self" class="floating-btn">⚙️</a>', unsafe_allow_html=True)
