import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Finance Tracker", layout="wide")

# --- 2. CSS (බටන් දෙක ලං කරන්න සහ UI එක පිරිසිදු කරන්න) ---
st.markdown("""
    <style>
    /* බටන් වල සයිස් එක පාලනය කිරීම */
    div.stButton > button {
        width: 100% !important;
        height: 32px !important;
        padding: 0 !important;
        font-size: 16px !important;
        border-radius: 6px !important;
    }
    /* පේළි අතර ඉඩ අඩු කිරීම */
    .stVerticalBlock { gap: 0.5rem !important; }
    hr { margin: 0.5rem 0 !important; }
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
except Exception as e:
    st.error(f"Error: {e}"); st.stop()

# --- 4. Navigation ---
query = st.query_params
form_type = query.get("form")
edit_idx = query.get("edit")

# --- 5. MAIN HOME PAGE ---
if not form_type and not edit_idx:
    st.title("💸 Finance Tracker")
    
    # Action Buttons (Uda tiana tika)
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("➕ Income"): st.query_params.update(form="Income"); st.rerun()
    if col2.button("➖ Expense"): st.query_params.update(form="Expense"); st.rerun()
    if col3.button("⚙️ Categories"): st.query_params.update(form="ManageCats"); st.rerun()
    if col4.button("📜 History"): st.query_params.update(form="History"); st.rerun()

    st.write("---")
    
    # 🔥 Table Header (Ratios: 65%, 20%, 15%)
    h1, h2, h3 = st.columns([0.65, 0.20, 0.15])
    h1.write("**Item / Category**")
    h2.write("**Amount**")
    h3.write("**Actions**")
    st.write("---")

    # 🔥 Data Rows
    if not df.empty:
        for idx in df.index[-10:][::-1]:
            row = df.loc[idx]
            color = "green" if row['Type'] == 'Income' else "red"
            
            # පේළිය බෙදීම
            r1, r2, r3 = st.columns([0.65, 0.20, 0.15])
            
            with r1:
                st.write(f"**{row['Category']}** \n*{row['Date']}*")
            
            with r2:
                st.markdown(f"<h4 style='color:{color}; margin:0;'>{row['Amount']:,.0f}</h4>", unsafe_allow_html=True)
            
            with r3:
                # බටන් දෙක තවත් ලං කිරීමට මෙතන තව Columns දෙකක් හැදුවා
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("✏️", key=f"ed_{idx}"):
                        st.query_params.update(edit=idx); st.rerun()
                with btn_col2:
                    if st.button("🗑️", key=f"dl_{idx}"):
                        worksheet.delete_rows(int(idx)+2); st.rerun()
            st.write("---")

# --- 6. MANAGE CATEGORIES ---
elif form_type == "ManageCats":
    st.subheader("⚙️ Manage Categories")
    new_c = st.text_input("New Category Name")
    if st.button("Add Category"):
        if new_c: cat_sheet.append_row([new_c]); st.rerun()
    
    for c in categories:
        c_col1, c_col2 = st.columns([0.8, 0.2])
        c_col1.write(c)
        if c_col2.button("❌", key=f"del_{c}"):
            cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
    if st.button("Back Home"): st.query_params.clear(); st.rerun()

# --- 7. HISTORY ---
elif form_type == "History":
    st.subheader("📜 Full History")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("Back Home"): st.query_params.clear(); st.rerun()

# --- 8. ADD/EDIT FORMS ---
elif form_type in ["Income", "Expense"] or edit_idx:
    t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    st.subheader(f"📝 {t} Entry")
    with st.form("entry_form"):
        f_cat = st.selectbox("Category", categories)
        f_amt = st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Save"):
            row = [str(date.today()), f_cat, f_amt, "", t, "Cash", "Bank", ""]
            if edit_idx: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [row])
            else: worksheet.append_row(row)
            st.query_params.clear(); st.rerun()
    if st.button("Cancel"): st.query_params.clear(); st.rerun()
