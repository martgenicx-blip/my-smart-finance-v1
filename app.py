import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Page Config ---
st.set_page_config(page_title="Finance Tracker", layout="wide")

# --- 2. 🎯 FINAL CLEAN UI CSS ---
st.markdown("""
    <style>
    /* මුළු Row එකම මැදට ගන්න */
    [data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    
    /* බටන් වල Borders සහ Padding සම්පූර්ණයෙන්ම අයින් කිරීම */
    div.stButton > button {
        border: none !important;
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 35px !important;
        height: 35px !important;
        font-size: 20px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: 0.2s;
    }
    
    /* බටන් එක උඩට යනකොට පොඩි අළු පාටක් එන්න */
    div.stButton > button:hover {
        background-color: #eeeeee !important;
        border-radius: 50% !important;
    }

    /* පේළි අතර ඉඩ පාලනය */
    hr { margin: 8px 0 !important; opacity: 0.15; }
    
    /* Amount එක දකුණට කරන්න */
    .amt-text { width: 100%; text-align: right; padding-right: 20px; }
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
    st.error("Connection Error!"); st.stop()

# --- 4. Navigation Logic ---
query = st.query_params
form_type = query.get("form")
edit_idx = query.get("edit")

# --- 5. MAIN HOME PAGE ---
if not form_type and not edit_idx:
    st.markdown("<h2 style='text-align: center; color: #333;'>Finance Tracker</h2>", unsafe_allow_html=True)
    
    # Quick Actions
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("💰 Income"): st.query_params.update(form="Income"); st.rerun()
    if c2.button("💸 Expense"): st.query_params.update(form="Expense"); st.rerun()
    if c3.button("⚙️ Cats"): st.query_params.update(form="ManageCats"); st.rerun()
    if c4.button("📜 History"): st.query_params.update(form="History"); st.rerun()

    st.write("---")
    
    # 🔥 Table Header
    h1, h2, h3 = st.columns([0.65, 0.20, 0.15])
    h1.write("**Transaction Details**")
    h2.markdown("<div style='text-align:right; font-weight:bold;'>Amount</div>", unsafe_allow_html=True)
    h3.markdown("<div style='padding-left:15px; font-weight:bold;'>Actions</div>", unsafe_allow_html=True)
    st.write("---")

    # 🔥 Data Rows (Clean Alignment)
    if not df.empty:
        for idx in df.index[-12:][::-1]:
            row = df.loc[idx]
            is_inc = row['Type'] == 'Income'
            color = "#28a745" if is_inc else "#dc3545"
            
            r1, r2, r3 = st.columns([0.65, 0.20, 0.15])
            
            with r1:
                st.markdown(f"<div><b>{row['Category']}</b><br><small style='color:gray;'>{row['Date']}</small></div>", unsafe_allow_html=True)
            
            with r2:
                st.markdown(f"<div class='amt-text' style='color:{color}; font-weight:700; font-size:18px;'>{row['Amount']:,.0f}</div>", unsafe_allow_html=True)
            
            with r3:
                # බටන් දෙක අතර ඉතා කුඩා පරතරයක් තැබීම (Padding අයින් කරලා තියෙන්නේ CSS වලින්)
                b1, b2 = st.columns([1, 1])
                with b1:
                    if st.button("📝", key=f"e_{idx}"):
                        st.query_params.update(edit=idx); st.rerun()
                with b2:
                    if st.button("🗑️", key=f"d_{idx}"):
                        worksheet.delete_rows(int(idx)+2); st.rerun()
            st.write("---")

# --- 6. OTHER SECTIONS (Remain Same) ---
elif form_type == "ManageCats":
    st.subheader("⚙️ Manage Categories")
    new_c = st.text_input("New Category")
    if st.button("Add"):
        if new_c: cat_sheet.append_row([new_c]); st.rerun()
    for c in categories:
        cx, cy = st.columns([0.8, 0.2])
        cx.write(f"• {c}")
        if cy.button("❌", key=f"del_{c}"):
            cell = cat_sheet.find(c); cat_sheet.delete_rows(cell.row); st.rerun()
    if st.button("Back"): st.query_params.clear(); st.rerun()

elif form_type in ["Income", "Expense"] or edit_idx:
    t = form_type if not edit_idx else df.loc[int(edit_idx)]['Type']
    with st.form("f"):
        f_cat = st.selectbox("Category", categories)
        f_amt = st.number_input("Amount", min_value=0.0)
        if st.form_submit_button("Save"):
            r = [str(date.today()), f_cat, f_amt, "", t, "Cash", "Bank", ""]
            if edit_idx: worksheet.update(f'A{int(edit_idx)+2}:H{int(edit_idx)+2}', [r])
            else: worksheet.append_row(r)
            st.query_params.clear(); st.rerun()
    if st.button("Cancel"): st.query_params.clear(); st.rerun()

elif form_type == "History":
    st.subheader("📜 History")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    if st.button("Back"): st.query_params.clear(); st.rerun()
