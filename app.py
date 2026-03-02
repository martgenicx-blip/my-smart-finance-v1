import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Pro", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 🎨 MODERN Glassmorphism UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    :root {
        --main-bg: #f0f2f6;
        --card-bg: #ffffff;
        --primary: #007AFF;
        --secondary: #5856D6;
        --success: #34C759;
        --danger: #FF3B30;
    }

    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: var(--main-bg); }

    /* Header */
    .header-container {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 40px 20px; color: white; border-radius: 0 0 30px 30px;
        text-align: center; margin: -60px -20px 30px -20px;
        box-shadow: 0 10px 30px rgba(0,122,255,0.2);
    }

    /* Cards */
    .glass-card {
        background: var(--card-bg); padding: 25px; border-radius: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.3);
        margin-bottom: 20px;
    }

    /* Stats */
    .stat-label { font-size: 12px; color: #8E8E93; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-value { font-size: 24px; font-weight: 700; margin-top: 5px; }

    /* Modern Grid */
    .action-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }
    .nav-btn {
        background: white; border-radius: 20px; padding: 20px; text-align: center;
        text-decoration: none !important; color: #1C1C1E !important; font-weight: 600;
        transition: all 0.3s ease; border: 1px solid #E5E5EA; display: block;
    }
    .nav-btn:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08); border-color: var(--primary); }

    /* Recent Activity Row */
    .activity-row {
        background: white; border-radius: 18px; padding: 12px 15px; margin-bottom: 10px;
        display: flex; align-items: center; justify-content: space-between;
        border: 1px solid #F2F2F7; transition: 0.2s;
    }
    .activity-row:hover { background: #FAFAFC; }

    /* 🔥 Borderless Icon Buttons (Fixed False Issue) */
    div.stButton > button {
        border: none !important; background: #F2F2F7 !important;
        border-radius: 12px !important; width: 40px !important; height: 40px !important;
        padding: 0 !important; color: #48484A !important; transition: 0.2s;
    }
    div.stButton > button:hover { background: #E5E5EA !important; color: var(--primary) !important; }
    
    /* Floating Menu */
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 1000; }
    .fab-main { 
        width: 56px; height: 56px; background: var(--primary); border-radius: 18px;
        display: flex; justify-content: center; align-items: center; color: white;
        font-size: 28px; box-shadow: 0 8px 25px rgba(0,122,255,0.3); cursor: pointer;
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
    
    try:
        opening_bal = float(cat_sheet.acell('B1').value.replace(',', ''))
    except: opening_bal = 0.0
        
    categories = sorted(list(set([row['CategoryName'] for row in cat_sheet.get_all_records() if row['CategoryName']])))
    df = pd.DataFrame(worksheet.get_all_records())
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"⚠️ Connection Lost: {e}"); st.stop()

# --- 4. Navigation ---
query = st.query_params
form_type, edit_idx = query.get("form"), query.get("edit")

# Header Section
st.markdown('<div class="header-container"><h1>FinanceFlow</h1><p style="opacity:0.8">Smart Wealth Management</p></div>', unsafe_allow_html=True)

# --- 5. HOME PAGE ---
if not form_type and not edit_idx:
    if not df.empty:
        t_inc = df[df['Type'] == 'Income']['Amount'].sum()
        t_exp = df[df['Type'] == 'Expense']['Amount'].sum()
        current_bal = opening_bal + t_inc - t_exp

        # Modern Balance Card
        st.markdown(f"""
            <div class="glass-card">
                <div class="stat-label">Available Balance</div>
                <div class="stat-value" style="color:var(--primary); font-size:32px;">LKR {current_bal:,.2f}</div>
                <hr style="margin:20px 0; border:0; border-top:1px solid #eee;">
                <div style="display:flex; justify-content:space-between;">
                    <div><div class="stat-label">Monthly Income</div><div class="stat-value" style="color:var(--success); font-size:18px;">+ {t_inc:,.0f}</div></div>
                    <div style="text-align:right;"><div class="stat-label">Monthly Expense</div><div class="stat-value" style="color:var(--danger); font-size:18px;">- {t_exp:,.0f}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Action Grid
    st.markdown("""
        <div class="action-grid">
            <a href="./?form=Income" target="_self" class="nav-btn">💰 Income</a>
            <a href="./?form=Expense" target="_self" class="nav-btn">💸 Expense</a>
            <a href="./?form=Transfer" target="_self" class="nav-btn">🔄 Transfer</a>
            <a href="./?form=History" target="_self" class="nav-btn">📜 History</a>
        </div>
    """, unsafe_allow_html=True)

    # Recent Activity
    if not df.empty:
        st.markdown('<h3 style="font-size:18px; margin-bottom:15px;">Recent Activity</h3>', unsafe_allow_html=True)
        for idx in df.index[-8:][::-1]:
            row = df.loc[idx]
            is_inc = row['Type'] == 'Income'
            color = "#34C759" if is_inc else "#FF3B30"
            
            # Use columns for layout but custom CSS for styling
            with st.container():
                c1, c2, c3, c4 = st.columns([0.6, 0.25, 0.08, 0.08])
                with c1: st.markdown(f"<b>{row['Category']}</b><br><small style='color:#8E8E93'>{row['Date']}</small>", unsafe_allow_html=True)
                with c2: st.markdown(f"<p style='color:{color}; font-weight:700; margin-top:8px; text-align:right;'>{'▲' if is_inc else '▼'} {row['Amount']:,.0f}</p>", unsafe_allow_html=True)
                
                # Action buttons (False text fix: wrapped in if condition or simplified)
                with c3: 
                    if st.button("📝", key=f"ed_{idx}"): st.query_params.update(edit=idx); st.rerun()
                with c4:
                    if st.button("🗑️", key=f"dl_{idx}"): worksheet.delete_rows(int(idx)+2); st.rerun()
                st.markdown('<div style="margin-bottom:12px;"></div>', unsafe_allow_html=True)

# --- 6. HISTORY ---
elif form_type == "History":
    st.markdown('<div class="glass-card"><h3>📜 Transaction History</h3></div>', unsafe_allow_html=True)
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("Back to Home"): st.query_params.clear(); st.rerun()

# --- 7. SETTINGS & OPENING BALANCE ---
elif form_type == "ManageCats":
    st.markdown('<div class="glass-card"><h3>⚙️ App Settings</h3></div>', unsafe_allow_html=True)
    with st.expander("💰 Opening Balance Management", expanded=True):
        new_bal = st.number_input("Set Initial Balance", value=opening_bal)
        if st.button("Save New Balance"):
            cat_sheet.update_acell('B1', new_bal); st.success("Updated!"); st.rerun()
    
    with st.expander("🏷️ Categories"):
        new_cat = st.text_input("New Category")
        if st.button("Add Category"): cat_sheet.append_row([new_cat]); st.rerun()
        for c in categories:
            col1, col2 = st.columns([0.8, 0.2])
            col1.write(c)
            if col2.button("❌", key=c):
                cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
    if st.button("Back Home"): st.query_params.clear(); st.rerun()

# --- 8. ENTRY FORMS ---
elif form_type in ["Income", "Expense", "Transfer"] or edit_idx:
    t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    st.markdown(f'<div class="glass-card"><h3>📝 Add {t}</h3></div>', unsafe_allow_html=True)
    
    with st.container():
        f_date = st.date_input("Date", date.today())
        f_cat = st.selectbox("Category", categories)
        f_amt = st.number_input("Amount (LKR)", min_value=0.0)
        f_desc = st.text_input("Note / Description")
        
        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns([0.2, 0.8])
        with b1:
            if st.button("Save", use_container_width=True):
                ts = f"{f_date} {datetime.now().strftime('%H:%M:%S')}"; r_data = [ts, f_cat, f_amt, f_desc, t, "Cash", "Bank", ""]
                if edit_idx: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [r_data])
                else: worksheet.append_row(r_data)
                st.query_params.clear(); st.rerun()
        with b2:
            if st.button("Cancel", use_container_width=True): st.query_params.clear(); st.rerun()

# --- 9. FAB ---
st.markdown('<div class="fab-wrapper"><a href="./?form=ManageCats" target="_self" style="text-decoration:none"><div class="fab-main">⚙️</div></a></div>', unsafe_allow_html=True)
