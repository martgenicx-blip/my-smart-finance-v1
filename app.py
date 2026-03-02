import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Smart Finance Tracker", layout="wide")

# --- 2. CSS Styles (Zero Waste Space UI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f4f7f9; }
    
    .header-bar {
        background: linear-gradient(135deg, #0081C9 0%, #0056b3 100%);
        padding: 15px; color: white; text-align: center; font-size: 20px; font-weight: 700;
        margin: -60px -20px 20px -20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    /* 🔥 සම්පූර්ණ පේළියම එකම සුදු පාට Background එකක් කරන Style එක */
    .full-trans-row {
        background: white;
        border-radius: 12px;
        padding: 8px 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 6px;
        border-left: 5px solid #ccc;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .trans-income { border-left-color: #28a745; }
    .trans-expense { border-left-color: #dc3545; }

    /* Button Style inside Row */
    div.stButton > button {
        padding: 2px 8px !important;
        border-radius: 6px !important;
        height: 30px !important;
        width: 35px !important;
        border: none !important;
        background-color: #f8f9fa !important;
        font-size: 14px !important;
        transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #e9ecef !important; }

    /* Layout tweaks to remove extra padding */
    .block-container { padding-top: 2rem !important; }
    [data-testid="column"] { display: flex; align-items: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Google Sheets Connection ---
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
    st.error("Sheet Connection Error!"); st.stop()

# --- 4. Routing ---
query = st.query_params
form_type = query.get("form")
edit_idx = query.get("edit")

# --- 5. Header ---
st.markdown('<div class="header-bar">Finance Tracker</div>', unsafe_allow_html=True)

# --- 6. Summary & Activity (Inline Implementation) ---
if not form_type and not edit_idx:
    if not df.empty:
        t_inc = df[df['Type'] == 'Income']['Amount'].sum()
        t_exp = df[df['Type'] == 'Expense']['Amount'].sum()
        final_bal = 38814.85 + (t_inc - t_exp)

        # Summary box
        st.markdown(f"""
            <div style="background:white; border-radius:15px; padding:15px; margin-bottom:20px; box-shadow:0 2px 10px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; text-align:center;">
                    <div style="flex:1;"><small style="color:gray;">INCOME</small><br><b style="color:#28a745;">{t_inc:,.0f}</b></div>
                    <div style="flex:1; border-left:1px solid #eee; border-right:1px solid #eee;"><small style="color:gray;">EXPENSE</small><br><b style="color:#dc3545;">{t_exp:,.0f}</b></div>
                    <div style="flex:1;"><small style="color:gray;">BALANCE</small><br><b style="color:#0081C9;">{final_bal:,.0f}</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Activity Header
    st.write("<b>Recent Activity</b>", unsafe_allow_html=True)
    
    for idx in df.index[-12:][::-1]:
        row = df.loc[idx]
        is_inc = row['Type'] == 'Income'
        
        # 🎯 මම මෙතන Columns පාවිච්චි කරලා මුළු පේළියම එකම මට්ටමට හැදුවා
        # [Info (Date/Cat)] [Amount] [Edit] [Delete]
        c_main, c_amt, c_edit, c_del = st.columns([0.5, 0.3, 0.1, 0.1])
        
        with c_main:
            st.markdown(f"""
                <div class="full-trans-row {'trans-income' if is_inc else 'trans-expense'}" style="margin-bottom:0; box-shadow:none; border-right:none;">
                    <div><b style="font-size:14px;">{row['Category']}</b><br><small style="color:#888;">{row['Date']}</small></div>
                </div>""", unsafe_allow_html=True)
        
        with c_amt:
            st.markdown(f"""
                <div style="height:100%; display:flex; align-items:center; justify-content:flex-end; font-weight:700; color:{'#28a745' if is_inc else '#dc3545'}; font-size:15px;">
                    {'+' if is_inc else '-'}{row['Amount']:,.0f}
                </div>""", unsafe_allow_html=True)
        
        with c_edit:
            if st.button("✏️", key=f"e_{idx}"):
                st.query_params.update(edit=idx); st.rerun()
                
        with c_del:
            if st.button("🗑️", key=f"d_{idx}"):
                worksheet.delete_rows(int(idx)+2); st.rerun()
        
        st.markdown('<div style="margin-bottom:8px; border-bottom:1px solid #f0f0f0;"></div>', unsafe_allow_html=True)

# --- 7. Forms ---
elif form_type or edit_idx:
    # (Form logic remains the same to maintain stability)
    st.markdown(f"### 📝 Entry Form")
    with st.form("main_form"):
        # Simple form fields
        f_cat = st.selectbox("Category", categories)
        f_amt = st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Save Record"):
            ts = f"{date.today()} {datetime.now().strftime('%H:%M:%S')}"
            r = [ts, f_cat, f_amt, "", "Expense", "Cash", "Bank", ""]
            worksheet.append_row(r); st.query_params.clear(); st.rerun()

# --- 8. Floating Action Buttons (FAB) ---
st.markdown("""
    <div style="position:fixed; bottom:20px; right:20px; z-index:100;">
        <a href="./" target="_self" style="background:#0081C9; color:white; width:50px; height:50px; border-radius:50%; display:flex; align-items:center; justify-content:center; text-decoration:none; font-size:24px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">🏠</a>
    </div>
""", unsafe_allow_html=True)
