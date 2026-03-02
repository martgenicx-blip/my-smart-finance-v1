import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="FinanceFlow Pro", layout="wide")

# --- 2. 🎨 THE ULTIMATE MODERN UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8f9fc; }

    .header-wrapper {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
        padding: 45px 15px; color: white; border-radius: 0 0 40px 40px;
        text-align: center; margin: -65px -20px 30px -20px;
        box-shadow: 0 15px 35px rgba(0,122,255,0.2);
    }

    .net-balance-card {
        background: white; border-radius: 28px; padding: 30px;
        text-align: center; margin-bottom: 30px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.04);
        border: 1px solid rgba(255,255,255,0.7);
        position: relative; overflow: hidden;
    }
    .bal-label { color: #8E8E93; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }
    .bal-amount { color: #1c1c1e; font-size: 40px; font-weight: 800; letter-spacing: -1.5px; }

    .grid-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 35px; }
    .grid-btn {
        background: #ffffff; border-radius: 22px; padding: 25px 15px; text-align: center;
        text-decoration: none !important; color: #1c1c1e !important; font-weight: 700; font-size: 16px;
        border: 2px solid #f1f3f5; transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    .grid-btn:hover {
        transform: translateY(-8px); border-color: #007AFF;
        box-shadow: 0 15px 30px rgba(0,122,255,0.12);
        background: #fff;
    }

    /* CLICKABLE RECENT ACTIVITY CARD */
    .activity-link { text-decoration: none !important; color: inherit !important; display: block; margin-bottom: 12px; }
    
    .activity-container {
        background: white; border-radius: 20px;
        padding: 18px 25px; position: relative;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02); border: 1px solid #f8f9fa;
        transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .activity-container:hover { 
        transform: scale(1.02); border-color: #007AFF; 
        box-shadow: 0 10px 20px rgba(0,122,255,0.08);
        background-color: #f0f7ff;
    }

    .v-line { position: absolute; left: 0; top: 15px; bottom: 15px; width: 6px; border-radius: 0 10px 10px 0; }
    .bg-income { background-color: #34C759; }
    .bg-expense { background-color: #FF3B30; }

    /* FLOATING ACTION BUTTON WITH ANIMATION */
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 9999; }
    .fab-main { 
        width: 65px; height: 65px; background: linear-gradient(135deg, #007AFF 0%, #0056b3 100%);
        border-radius: 22px; display: flex; justify-content: center; align-items: center; 
        color: white; font-size: 35px; box-shadow: 0 12px 25px rgba(0,122,255,0.35);
        cursor: pointer; transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .fab-wrapper:hover .fab-main { transform: scale(1.1) rotate(90deg); }
    
    .fab-list { 
        display: none; flex-direction: column; gap: 12px; align-items: flex-end; margin-bottom: 15px;
        animation: fadeIn 0.3s ease forwards;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 12px; text-decoration: none !important; transition: 0.2s; }
    .fab-item:hover { transform: translateX(-5px); }
    .fab-label { background: #1c1c1e; padding: 8px 16px; border-radius: 12px; font-size: 13px; font-weight: 600; color: white; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
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
    st.error(f"Error connecting to Sheets: {e}"); st.stop()

q = st.query_params
form_type, edit_idx = q.get("form"), q.get("edit")

st.markdown('<div class="header-wrapper"><h1>FinanceFlow</h1></div>', unsafe_allow_html=True)

# --- 5. HOME PAGE ---
if not form_type and not edit_idx:
    if not df.empty:
        t_inc, t_exp = df[df['Type'] == 'Income']['Amount'].sum(), df[df['Type'] == 'Expense']['Amount'].sum()
        curr_bal = opening_bal + t_inc - t_exp
        st.markdown(f'<div class="net-balance-card"><div class="bal-label">Net Balance</div><div class="bal-amount">LKR {curr_bal:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="grid-container">
            <a href="./?form=Income" target="_self" class="grid-btn">💰<br>Income</a>
            <a href="./?form=Expense" target="_self" class="grid-btn">💸<br>Expense</a>
            <a href="./?form=Transfer" target="_self" class="grid-btn">🔄<br>Transfer</a>
            <a href="./?form=History" target="_self" class="grid-btn">📜<br>History</a>
        </div>
    """, unsafe_allow_html=True)

    if not df.empty:
        st.markdown('<h3 style="font-size:18px; font-weight:800; margin-bottom:20px;">Recent Transactions</h3>', unsafe_allow_html=True)
        recent_items = df.tail(10).iloc[::-1]
        
        for idx_row, row in recent_items.iterrows():
            is_inc = row['Type'] == 'Income'
            v_color, t_color, sym = ("bg-income", "#34C759", "+") if is_inc else ("bg-expense", "#FF3B30", "-")
            
            st.markdown(f"""
                <a href="./?edit={idx_row}" target="_self" class="activity-link">
                    <div class="activity-container">
                        <div class="v-line {v_color}"></div>
                        <div>
                            <div style="font-weight:700; font-size:16px;">{row['Category']}</div>
                            <div style="color:#8e8e93; font-size:12px;">{row['Date']}</div>
                        </div>
                        <div style="font-weight:800; font-size:18px; color:{t_color};">{sym} {row['Amount']:,.0f}</div>
                    </div>
                </a>
            """, unsafe_allow_html=True)

# --- 6. HISTORY PAGE ---
elif form_type == "History":
    st.markdown('<div class="net-balance-card"><h3>📜 Transaction History</h3></div>', unsafe_allow_html=True)
    if not df.empty:
        for idx_row, row in df.iloc[::-1].iterrows():
            is_inc = row['Type'] == 'Income'
            t_color = "#34C759" if is_inc else "#FF3B30"
            with st.container():
                c1, c2, c3 = st.columns([0.5, 0.3, 0.2])
                with c1: st.markdown(f"**{row['Category']}**<br><small>{row['Date']}</small>", unsafe_allow_html=True)
                with c2: st.markdown(f"<span style='color:{t_color}; font-weight:700;'>{row['Amount']:,.0f}</span>", unsafe_allow_html=True)
                with c3:
                    if st.button("🗑️", key=f"del_{idx_row}"):
                        worksheet.delete_rows(int(idx_row)+2); st.cache_data.clear(); st.rerun()
                st.divider()
    if st.button("Back Home 🏠", use_container_width=True): st.query_params.clear(); st.rerun()

# --- 7. FORMS (EDIT/ADD) ---
elif form_type or edit_idx:
    is_edit = edit_idx is not None
    row_data = df.loc[int(edit_idx)] if is_edit else None
    t = form_type if not is_edit else row_data['Type']
    
    st.markdown(f'<div class="net-balance-card"><h3>📝 {t}</h3></div>', unsafe_allow_html=True)
    
    # 🔥 FIXED DATE LOGIC FOR VALUE ERROR
    if is_edit:
        try:
            current_date = pd.to_datetime(row_data['Date']).date()
        except:
            current_date = date.today()
    else:
        current_date = date.today()

    f_date = st.date_input("Date", current_date)
    f_cat = st.selectbox("Category", categories, index=categories.index(row_data['Category']) if is_edit and row_data['Category'] in categories else 0)
    f_amt = st.number_input("Amount", min_value=0.0, value=float(row_data['Amount']) if is_edit else 0.0)
    f_note = st.text_input("Note", value=row_data['Note'] if is_edit else "")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save ✅", use_container_width=True):
            new_row = [str(f_date), f_cat, f_amt, f_note, t, "Cash", "Bank", ""]
            if is_edit: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [new_row])
            else: worksheet.append_row(new_row)
            st.cache_data.clear(); st.query_params.clear(); st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True): st.query_params.clear(); st.rerun()

# --- 8. FAB ---
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
