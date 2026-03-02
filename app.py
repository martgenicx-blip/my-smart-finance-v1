import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Smart Finance Tracker", layout="wide")

# --- 2. CSS Styles (UI Quality & Alignment) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f1f3f5; } /* Slight gray for background to pop the white cards */
    
    .header-bar {
        background: linear-gradient(135deg, #0081C9 0%, #0056b3 100%);
        padding: 20px; color: white; text-align: center; font-size: 22px; font-weight: 700;
        margin: -60px -20px 25px -20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* Action Grid */
    .custom-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 25px; }
    .grid-item {
        background: white; border: 1px solid #eee; border-radius: 15px; height: 85px; 
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 600; color: #444 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        text-decoration: none !important;
    }

    /* 🔥 Pure White Row Styling */
    .trans-row-box {
        background: white !important;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Button Styles to fit 10% width */
    div.stButton > button {
        padding: 0 !important;
        border-radius: 8px !important;
        height: 35px !important;
        width: 100% !important;
        background: #f8f9fa !important;
        border: 1px solid #eee !important;
        font-size: 16px !important;
    }
    div.stButton > button:hover { background: #e9ecef !important; border-color: #0081C9 !important; }

    /* FAB */
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { width: 60px; height: 60px; background: #0081C9; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 30px; box-shadow: 0 4px 15px rgba(0,129,201,0.4); }
    .fab-list { display: none; flex-direction: column; gap: 10px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    .fab-item { display: flex; align-items: center; gap: 10px; text-decoration: none !important; }
    .fab-label { background: white; padding: 5px 12px; border-radius: 8px; font-size: 12px; font-weight: 600; color: #333; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .fab-icon { width: 45px; height: 45px; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Sheet Connection ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = {k: st.secrets["connections"]["gsheets"][k] for k in st.secrets["connections"]["gsheets"]}
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet = sh.worksheet("Sheet1")
    cat_sheet = sh.worksheet("Categories")
    categories = sorted(list(set([row['CategoryName'] for row in cat_sheet.get_all_records() if row['CategoryName']])))
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except:
    st.error("Connection Lost!"); st.stop()

# --- 4. Header ---
st.markdown('<div class="header-bar">Finance Tracker Pro</div>', unsafe_allow_html=True)

query = st.query_params
form_type = query.get("form")
edit_idx = query.get("edit")

# --- 5. Home Page Content ---
if not form_type and not edit_idx:
    # Summary
    if not df.empty:
        t_inc, t_exp = df[df['Type'] == 'Income']['Amount'].sum(), df[df['Type'] == 'Expense']['Amount'].sum()
        bal = 38814.85 + (t_inc - t_exp)
        st.markdown(f'<div style="background:white; border-radius:15px; padding:15px; text-align:center; box-shadow:0 4px 10px rgba(0,0,0,0.03); margin-bottom:20px;"><small style="color:gray;">TOTAL BALANCE</small><br><b style="font-size:24px; color:#0081C9;">LKR {bal:,.2f}</b></div>', unsafe_allow_html=True)

    # Action Buttons
    st.markdown("""
        <div class="custom-grid">
            <a href="./?form=Income" target="_self" class="grid-item"><span>💰</span> Income</a>
            <a href="./?form=Expense" target="_self" class="grid-item"><span>💸</span> Expense</a>
            <a href="./?form=Transfer" target="_self" class="grid-item"><span>🔄</span> Transfer</a>
            <a href="./?form=History" target="_self" class="grid-item"><span>📜</span> History</a>
        </div>
    """, unsafe_allow_html=True)

    st.write("<b>Recent Activity</b>", unsafe_allow_html=True)
    
    # 🔥 Recent Activity (🎯 60%, 20%, 10%, 10% Layout)
    if not df.empty:
        for idx in df.index[-10:][::-1]:
            row = df.loc[idx]
            is_inc = row['Type'] == 'Income'
            color = "#28a745" if is_inc else "#dc3545"
            
            # Using a custom container to group into a white row
            with st.container():
                # 🎯 මෙන්න මෙතන Column ටික බෙදුවා: 60, 20, 10, 10
                c1, c2, c3, c4 = st.columns([0.6, 0.2, 0.1, 0.1])
                
                # Wrapping everything in a White Background Row
                st.markdown("""
                    <style>
                    [data-testid="column"] { background: white; border-radius: 0; padding: 5px 0; }
                    [data-testid="stVerticalBlock"] > div:has(div.stButton) { background: white; }
                    </style>
                """, unsafe_allow_html=True)

                with c1:
                    st.markdown(f'<div style="padding-left:10px; border-left:5px solid {color};"><b>{row["Category"]}</b><br><small style="color:gray;">{row["Date"]}</small></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div style="height:100%; display:flex; align-items:center; font-weight:700; color:{color};">{" + " if is_inc else " - "}{row["Amount"]:,.0f}</div>', unsafe_allow_html=True)
                with c3:
                    st.write(" ") # Padding for vertical alignment
                    if st.button("✏️", key=f"e_{idx}"): st.query_params.update(edit=idx); st.rerun()
                with c4:
                    st.write(" ") # Padding for vertical alignment
                    if st.button("🗑️", key=f"d_{idx}"): worksheet.delete_rows(int(idx)+2); st.rerun()
                
                # Separation line for the row
                st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

# --- 6. Forms (History / Manage / Entry) ---
elif form_type == "History":
    st.subheader("📜 History")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("⬅️ Back Home"): st.query_params.clear(); st.rerun()

elif form_type == "ManageCats":
    st.subheader("⚙️ Categories")
    new_c = st.text_input("New Category Name")
    if st.button("➕ Add Category"):
        if new_c: cat_sheet.append_row([new_c]); st.rerun()
    st.write("---")
    for c in categories:
        cx, cy = st.columns([0.8, 0.2]); cx.write(f"• {c}")
        if cy.button("➖", key=f"del_{c}"):
            cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
    if st.button("⬅️ Back Home"): st.query_params.clear(); st.rerun()

elif form_type in ["Income", "Expense", "Transfer"] or edit_idx:
    curr_t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    with st.form("f"):
        f_date = st.date_input("Date", date.today())
        f_cat = st.selectbox("Category", categories)
        f_amt = st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Save"):
            ts = f"{f_date} {datetime.now().strftime('%H:%M:%S')}"
            r = [ts, f_cat, f_amt, "", curr_t, "Cash", "Bank", ""]
            if edit_idx: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [r])
            else: worksheet.append_row(r)
            st.query_params.clear(); st.rerun()
    if st.button("Cancel"): st.query_params.clear(); st.rerun()

# --- 7. FAB Menu ---
st.markdown("""<div class="fab-wrapper"><div class="fab-list">
    <a href="./?form=ManageCats" target="_self" class="fab-item"><span class="fab-label">Settings</span><div class="fab-icon" style="background:#6c757d;">⚙️</div></a>
    <a href="./?form=Income" target="_self" class="fab-item"><span class="fab-label">Income</span><div class="fab-icon" style="background:#28a745;">➕</div></a>
    <a href="./?form=Expense" target="_self" class="fab-item"><span class="fab-label">Expense</span><div class="fab-icon" style="background:#dc3545;">➖</div></a>
</div><div class="fab-main">+</div></div>""", unsafe_allow_html=True)
