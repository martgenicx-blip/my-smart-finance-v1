import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px

# --- Page Config (Mobile Optimization) ---
st.set_page_config(page_title="Finance Pro", page_icon="💰", layout="wide")

# --- CUSTOM CSS (Mobile එකටම විතරක් ගැලපෙන විදිහට) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #f5f7f9; }

    /* Top Action Buttons - Mobile Grid */
    @media (max-width: 640px) {
        .stButton > button {
            height: 60px !important;
            font-size: 14px !important;
            margin-bottom: 5px !important;
        }
    }
    
    div.stButton > button {
        width: 100% !important;
        border-radius: 12px !important;
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }

    /* Summary Card Styling */
    .summary-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 20px;
    }
    .summary-box {
        flex: 1;
        background: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .summary-box h4 { margin: 0; font-size: 12px; color: gray; }
    .summary-box p { margin: 5px 0 0 0; font-weight: bold; font-size: 15px; }

    /* Floating marks */
    .inc-mark { color: #28a745; font-weight: bold; }
    .exp-mark { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if "show_form" not in st.session_state:
    st.session_state.show_form = None

# --- Connection ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = {k: st.secrets["connections"]["gsheets"][k] for k in st.secrets["connections"]["gsheets"]}
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet = sh.worksheet("Sheet1")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    
    if not df.empty:
        df['Date_Only'] = pd.to_datetime(df['Date'], format='mixed').dt.date
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- UI Header ---
st.markdown("<h2 style='text-align: center;'>💸 My Finance Pro</h2>", unsafe_allow_html=True)

# --- 2x2 Grid for Buttons (Mobile එකේ ලස්සනට පේන්න) ---
col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Income"): st.session_state.show_form = "Income"
    if st.button("🔄 Transfer"): st.session_state.show_form = "Transfer"
with col2:
    if st.button("➖ Expense"): st.session_state.show_form = "Expense"
    if st.button("📊 Charts"): st.session_state.show_form = "Charts"

st.write("---")

# --- Summary Row (Mobile පේළියකට) ---
if not df.empty:
    ti = df[df['Type'] == 'Income']['Amount'].sum()
    te = df[df['Type'] == 'Expense']['Amount'].sum()
    bal = ti - te
    
    st.markdown(f"""
        <div class="summary-container">
            <div class="summary-box"><h4>Income</h4><p style="color:green;">{ti:,.0f}</p></div>
            <div class="summary-box"><h4>Expense</h4><p style="color:red;">{te:,.0f}</p></div>
            <div class="summary-box"><h4>Balance</h4><p>{bal:,.0f}</p></div>
        </div>
    """, unsafe_allow_html=True)

# --- Forms & Charts ---
if st.session_state.show_form in ["Income", "Expense", "Transfer"]:
    with st.form("entry_form", clear_on_submit=True):
        st.subheader(f"Add {st.session_state.show_form}")
        d = st.date_input("Date", date.today())
        amt = st.number_input("Amount (LKR)", value=None, placeholder="0.00", min_value=0.0)
        
        if st.session_state.show_form == "Transfer":
            f_acc = st.selectbox("From", ["Cash", "Bank", "Card"])
            t_acc = st.selectbox("To", ["Bank", "Cash", "Card"])
            cat = "Transfer"
        else:
            cat = st.selectbox("Category", ["Food", "Salary", "Bills", "Travel", "Other"])
            f_acc, t_acc = "", ""

        note = st.text_input("Note")
        if st.form_submit_button("Save ✅"):
            if amt:
                ts = f"{d} {datetime.now().strftime('%H:%M:%S')}"
                worksheet.append_row([ts, cat, amt, note, st.session_state.show_form, f_acc, t_acc])
                st.success("Saved!"); st.session_state.show_form = None; st.rerun()

if st.session_state.show_form == "Charts" and not df.empty:
    exp_df = df[df['Type'] == 'Expense']
    if not exp_df.empty:
        st.plotly_chart(px.pie(exp_df, values='Amount', names='Category', hole=0.5), use_container_width=True)

# --- History with Date Filter ---
st.markdown("### 📜 History")
if not df.empty:
    f1, f2 = st.columns(2)
    start_d = f1.date_input("Start", df['Date_Only'].min())
    end_d = f2.date_input("End", date.today())

    mask = (df['Date_Only'] >= start_d) & (df['Date_Only'] <= end_d)
    df['row_idx'] = range(2, len(df) + 2)
    filtered_df = df.loc[mask].iloc[::-1]

    for idx, row in filtered_df.iterrows():
        c_data, c_del = st.columns([0.85, 0.15])
        t_color = "#28a745" if row['Type'] == "Income" else "#dc3545" if row['Type'] == "Expense" else "#ff8c00"
        mark = "+" if row['Type'] == "Income" else "-" if row['Type'] == "Expense" else "🔄"
        
        with c_data:
            st.markdown(f"""
                <div style="background:white; padding:12px; border-radius:10px; border-left:6px solid {t_color}; margin-bottom:8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <span style="float:right; font-weight:bold; color:{t_color};">{mark} {row['Amount']:,.0f}</span>
                    <div style="font-size:11px; color:gray;">{row['Date']}</div>
                    <div style="font-weight:bold; font-size:14px;">{row['Category']}</div>
                    <div style="font-size:13px; color:#666;">{row['Description']}</div>
                </div>
            """, unsafe_allow_html=True)
        with c_del:
            if st.button("🗑️", key=f"del_{row['row_idx']}"):
                worksheet.delete_rows(int(row['row_idx']))
                st.rerun()
