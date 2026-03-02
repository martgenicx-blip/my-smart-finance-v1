import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Pro", layout="wide")

# --- 2. 🎨 ULTRA MODERN UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8f9fa; }

    .header-container {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
        padding: 45px 20px; color: white; border-radius: 0 0 35px 35px;
        text-align: center; margin: -65px -20px 30px -20px;
        box-shadow: 0 12px 30px rgba(0,122,255,0.25);
    }

    .glass-card {
        background: white; padding: 25px; border-radius: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04); margin-bottom: 20px;
    }

    /* Alternating Row Colors for Activity */
    .activity-item {
        padding: 15px; border-radius: 18px; margin-bottom: 10px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .row-even { background-color: #ffffff; border: 1px solid #f1f3f5; }
    .row-odd { background-color: #f8f9ff; border: 1px solid #eef2ff; }

    /* Modern Action Grid */
    .action-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 30px; }
    .nav-btn {
        background: white; border-radius: 22px; padding: 22px; text-align: center;
        text-decoration: none !important; color: #1c1c1e !important; font-weight: 700;
        transition: 0.3s; border: 1px solid #f1f3f5; font-size: 15px;
    }
    .nav-btn:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.06); border-color: #007AFF; }

    /* FAB Menu (Floating Button) */
    .fab-container { position: fixed; bottom: 30px; right: 25px; z-index: 1000; }
    .fab-btn {
        width: 60px; height: 60px; background: #007AFF; border-radius: 20px;
        display: flex; justify-content: center; align-items: center; color: white;
        font-size: 30px; box-shadow: 0 8px 25px rgba(0,122,255,0.4); cursor: pointer;
        transition: 0.3s;
    }
    .fab-btn:hover { transform: scale(1.1); background: #0056b3; }

    /* Remove Streamlit Default Button Styles */
    div.stButton > button {
        border: none !important; background: #f1f3f5 !important;
        border-radius: 12px !important; width: 38px !important; height: 38px !important;
        color: #444 !important; transition: 0.2s; padding: 0 !important;
    }
    div.stButton > button:hover { background: #e2e6ea !important; color: #007AFF !important; }

    /* Category Add Button Style */
    .add-cat-btn {
        background: #007AFF !important; color: white !important;
        width: 100% !important; height: 45px !important; font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Google Sheets Connection ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = st.secrets["connections"]["gsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet, cat_sheet = sh.worksheet("Sheet1"), sh.worksheet("Categories")
    
    try: opening_bal = float(cat_sheet.acell('B1').value.replace(',', ''))
    except: opening_bal = 0.0
        
    categories = sorted(list(set([row['CategoryName'] for row in cat_sheet.get_all_records() if row['CategoryName']])))
    df = pd.DataFrame(worksheet.get_all_records())
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"Sheet Connection Error: {e}"); st.stop()

# Navigation logic
query = st.query_params
form_type, edit_idx = query.get("form"), query.get("edit")

# Header
st.markdown('<div class="header-container"><h1>FinanceFlow Pro</h1><p style="opacity:0.8">Smart Money Tracker</p></div>', unsafe_allow_html=True)

# --- 5. HOME PAGE ---
if not form_type and not edit_idx:
    if not df.empty:
        t_inc = df[df['Type'] == 'Income']['Amount'].sum()
        t_exp = df[df['Type'] == 'Expense']['Amount'].sum()
        current_bal = opening_bal + t_inc - t_exp

        st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:12px; color:#8e8e93; font-weight:700; text-transform:uppercase;">Total Balance</div>
                <div style="font-size:32px; font-weight:700; color:#007AFF; margin:5px 0;">LKR {current_bal:,.2f}</div>
                <div style="display:flex; justify-content:space-between; margin-top:15px; padding-top:15px; border-top:1px solid #f1f3f5;">
                    <div><small style="color:#8e8e93">Income</small><br><b style="color:#34C759; font-size:18px;">+ {t_inc:,.0f}</b></div>
                    <div style="text-align:right;"><small style="color:#8e8e93">Expense</small><br><b style="color:#FF3B30; font-size:18px;">- {t_exp:,.0f}</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="action-grid">'
                '<a href="./?form=Income" target="_self" class="nav-btn">💰 Income</a>'
                '<a href="./?form=Expense" target="_self" class="nav-btn">💸 Expense</a>'
                '<a href="./?form=Transfer" target="_self" class="nav-btn">🔄 Transfer</a>'
                '<a href="./?form=History" target="_self" class="nav-btn">📜 History</a>'
                '</div>', unsafe_allow_html=True)

    # Recent Activity with Alternating Colors
    if not df.empty:
        st.markdown('<h3 style="font-size:18px; margin-bottom:15px; font-weight:700;">Recent Transactions</h3>', unsafe_allow_html=True)
        recent_df = df.index[-10:][::-1]
        for i, idx in enumerate(recent_df):
            row = df.loc[idx]
            is_inc = row['Type'] == 'Income'
            row_class = "row-even" if i % 2 == 0 else "row-odd"
            amt_color = "#34C759" if is_inc else "#FF3B30"
            
            # Row Layout
            st.markdown(f'<div class="activity-item {row_class}">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([0.6, 0.25, 0.07, 0.07])
            with c1: st.markdown(f"<b>{row['Category']}</b><br><small style='color:#8e8e93'>{row['Date']}</small>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div style='color:{amt_color}; font-weight:700; text-align:right; margin-top:8px;'>{'▲' if is_inc else '▼'} {row['Amount']:,.0f}</div>", unsafe_allow_html=True)
            with c3:
                if st.button("📝", key=f"e_{idx}"): st.query_params.update(edit=idx); st.rerun()
            with c4:
                if st.button("🗑️", key=f"d_{idx}"): worksheet.delete_rows(int(idx)+2); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 6. SETTINGS & CATEGORIES (With Add Category Button) ---
elif form_type == "ManageCats":
    st.markdown('<div class="glass-card"><h3>⚙️ Settings & Categories</h3></div>', unsafe_allow_html=True)
    
    # Opening Balance Update
    with st.expander("💰 Opening Balance", expanded=False):
        new_ob = st.number_input("Set Initial Balance", value=opening_bal)
        if st.button("Update Balance", key="up_bal"):
            cat_sheet.update_acell('B1', new_ob); st.success("Balance Updated!"); st.rerun()

    # Category Management
    st.markdown("#### 🏷️ Categories")
    new_cat_name = st.text_input("Enter New Category Name")
    if st.button("➕ Add Category", key="add_cat_btn"):
        if new_cat_name:
            cat_sheet.append_row([new_cat_name]); st.success("Added!"); st.rerun()
    
    st.write("---")
    for c in categories:
        cc1, cc2 = st.columns([0.85, 0.15])
        cc1.markdown(f"<div style='padding:10px; background:#f8f9fa; border-radius:10px; margin-bottom:5px;'>{c}</div>", unsafe_allow_html=True)
        if cc2.button("❌", key=f"del_{c}"):
            cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
            
    if st.button("⬅️ Back to Home"): st.query_params.clear(); st.rerun()

# --- 7. FORMS & HISTORY ---
elif form_type == "History":
    st.markdown('<div class="glass-card"><h3>📜 Full Transaction History</h3></div>', unsafe_allow_html=True)
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("⬅️ Back"): st.query_params.clear(); st.rerun()

elif form_type in ["Income", "Expense", "Transfer"] or edit_idx:
    t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    st.markdown(f'<div class="glass-card"><h3>📝 {t} Entry</h3></div>', unsafe_allow_html=True)
    f_date = st.date_input("Date", date.today())
    f_cat = st.selectbox("Category", categories)
    f_amt = st.number_input("Amount (LKR)", min_value=0.0)
    f_desc = st.text_input("Description")
    
    st.write(" ")
    b1, b2 = st.columns([0.2, 0.8])
    with b1:
        if st.button("Save", use_container_width=True):
            ts = f"{f_date} {datetime.now().strftime('%H:%M:%S')}"; r_data = [ts, f_cat, f_amt, f_desc, t, "Cash", "Bank", ""]
            if edit_idx: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [r_data])
            else: worksheet.append_row(r_data)
            st.query_params.clear(); st.rerun()
    with b2:
        if st.button("Cancel"): st.query_params.clear(); st.rerun()

# --- 8. FLOATING ACTION BUTTON (FAB) ---
st.markdown(f"""
    <div class="fab-container">
        <a href="./?form=ManageCats" target="_self" style="text-decoration:none;">
            <div class="fab-btn">⚙️</div>
        </a>
    </div>
""", unsafe_allow_html=True)
