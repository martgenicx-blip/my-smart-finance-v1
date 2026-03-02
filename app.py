# --- Google Sheets Connection (Settings වෙනස් නොකර අලුත් Categories ටික ඇතුළත් කළා) ---
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = {k: st.secrets["connections"]["gsheets"][k] for k in st.secrets["connections"]["gsheets"]}
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open_by_key("1g77Wb3-mZij0tKyKFmz46YXHD8VN-gazQ0dUwhTUpD8")
    worksheet = sh.worksheet("Sheet1")
    
    try:
        cat_sheet = sh.worksheet("Categories")
    except:
        cat_sheet = sh.add_worksheet(title="Categories", rows="100", cols="2")
        cat_sheet.append_row(["CategoryName"])

    # දැනට තියෙන Categories ටික ගන්නවා
    existing_cats = [row['CategoryName'] for row in cat_sheet.get_all_records()]
    
    # ඔයා ඉල්ලපු අලුත් Categories ලැයිස්තුව
    default_cats = ["Salary", "Food", "Fuel", "Baby Care", "Toys", "Snacks", "Grocery", "SLT Bill", "Water Bill", "CEB Bill"]
    
    # අලුත් ඒවා නැත්නම් විතරක් ඇතුළත් කරනවා (Duplicate නොවෙන්න)
    for cat in default_cats:
        if cat not in existing_cats:
            cat_sheet.append_row([cat])
    
    # දැන් ඔක්කොම Categories ටික App එකට ලෝඩ් කරනවා
    categories = [row['CategoryName'] for row in cat_sheet.get_all_records()]

    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)

except Exception as e:
    st.error(f"Connection Error: {e}"); st.stop()
