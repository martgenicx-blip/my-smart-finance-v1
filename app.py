import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# --- Page Config ---
st.set_page_config(page_title="Income Expense Tracker", layout="wide")

# --- ULTIMATE CSS FIX (Manual HTML Grid) ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f3f6; }
    
    .header-bar {
        background-color: #0081C9; padding: 15px; color: white;
        text-align: center; font-size: 20px; font-weight: bold;
        margin: -60px -20px 20px -20px;
    }

    /* --- CUSTOM BUTTON GRID (HTML) --- */
    .custom-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .grid-item {
        background: white;
        border: 1px solid #ddd;
        border-radius: 12px;
        height: 100px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #333;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        cursor: pointer;
        text-decoration: none;
    }

    .grid-item:active { background: #f0f8ff; transform: scale(0.98); }
    .icon { font-size: 22px; margin-bottom: 5px; }

    /* Summary Card */
    .summary-card {
        background: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px;
        text-align: center;
    }
    .sum-grid { display: flex; justify-content: space-around; border-top: 1px solid #eee; padding-top: 10px; margin-top: 10px; }
    .bal-box { background: #e3f2fd; padding: 10px; border-radius: 8px; margin-top: 10px; text-align: right; font-weight: bold; color: green; }

    /* Floating Button */
    .fab-wrapper { position: fixed; bottom: 30px; right: 25px; z-index: 99999; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }
    .fab-main { width: 60px; height: 60px; background: #0081C9; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-size: 35px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .fab-list { display: none; flex-direction: column; gap: 10px; align-items: flex-end; }
    .fab-wrapper:hover .fab-list { display: flex; }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header-bar">Income Expense ⌄</div>', unsafe_allow_html=True)

# --- 1. THE ACTION BUTTONS (Hard-coded Grid) ---
# මචං මෙතන බටන් එබුවම Form එක එන්න මම Query Params පාවිච්චි කළා
st.markdown("""
    <div class="custom-grid">
        <a href="/?form=income" target="_self" class="grid-item"><span class="icon">⊕</span> Add Income</a>
        <a href="/?form=expense" target="_self" class="grid-item"><span class="icon">⊖</span> Add Expense</a>
        <a href="/?form=transfer" target="_self" class="grid-item"><span class="icon">⇄</span> Transfer</a>
        <a href="/?form=history" target="_self" class="grid-item"><span class="icon">☰</span> Transactions</a>
    </div>
""", unsafe_allow_html=True)

# Query params වලින් Form එක පාලනය කිරීම
query_params = st.query_params
show_form = query_params.get("form")

# --- 2. DATA ENTRY FORM ---
if show_form in ["income", "expense", "transfer"]:
    st.write(f"### New {show_form.capitalize()}")
    with st.form("entry_form", clear_on_submit=True):
        d = st.date_input("Date", date.today())
        amt = st.number_input("Amount (LKR)", value=0.0)
        note = st.text_input("Note")
        if st.form_submit_button("Save Record ✅"):
            st.success("Saved!") # මෙතන ඔයාගේ GSheet කෝඩ් එක දාන්න පුළුවන්
            st.query_params.clear()
            st.rerun()

# --- 3. SUMMARY CARD (image_0.png style) ---
st.markdown(f"""
    <div class="summary-card">
        <div style="font-size:12px; color:gray;">21-Feb-2026 -> 20-Mar-2026</div>
        <div class="sum-grid">
            <div><span style="color:green; font-size:11px;">Income</span><br><b style="color:green;">0</b></div>
            <div><span style="color:red; font-size:11px;">Expense</span><br><b style="color:red;">0</b></div>
            <div><span style="color:gray; font-size:11px;">Balance</span><br><b>0</b></div>
        </div>
        <div style="text-align:right; font-size:12px; color:gray; margin-top:10px;">Previous Balance <span style="color:green; font-weight:bold;">38,814.85</span></div>
        <div class="bal-box">Balance <span>38,814.85</span></div>
    </div>
""", unsafe_allow_html=True)

# --- 4. FLOATING ACTION MENU ---
st.markdown("""
    <div class="fab-wrapper">
        <div class="fab-list">
            <div style="display:flex; align-items:center; gap:8px;"><span style="background:white;padding:2px 8px;border-radius:4px;font-size:12px;">Add Income</span><div style="width:40px;height:40px;background:#28a745;border-radius:50%;display:flex;justify-content:center;align-items:center;color:white;">➕</div></div>
            <div style="display:flex; align-items:center; gap:8px;"><span style="background:white;padding:2px 8px;border-radius:4px;font-size:12px;">Add Expense</span><div style="width:40px;height:40px;background:#dc3545;border-radius:50%;display:flex;justify-content:center;align-items:center;color:white;">➖</div></div>
        </div>
        <div class="fab-main">+</div>
    </div>
""", unsafe_allow_html=True)
