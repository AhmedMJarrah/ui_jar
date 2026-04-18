"""
setup_admin.py
Run this ONCE to create the admin user in Google Sheets.
Usage: streamlit run setup_admin.py
"""
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import bcrypt
from datetime import datetime

SPREADSHEET_ID = "1svY3lp6RUTp4K-bigbx2JDAeh8RNLACsuXCYqxP4QgQ"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

st.title("⚙️ إعداد المدير - تشغيل مرة واحدة فقط")

if st.button("إنشاء حساب المدير", type="primary"):
    try:
        creds_dict = dict(st.secrets["google_credentials"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        sp = client.open_by_key(SPREADSHEET_ID)

        # Create users sheet
        try:
            ws = sp.worksheet("users")
        except gspread.WorksheetNotFound:
            ws = sp.add_worksheet(title="users", rows=1000, cols=10)
            ws.append_row(["username", "password_hash", "role", "created_at", "last_active"])

        # Check if admin exists
        records = ws.get_all_records()
        if any(r["username"] == "Jarrah01" for r in records):
            st.warning("حساب المدير موجود مسبقاً!")
        else:
            hashed = bcrypt.hashpw("rrrrr01".encode(), bcrypt.gensalt()).decode()
            ws.append_row(["Jarrah01", hashed, "admin", datetime.now().isoformat(), ""])
            st.success("✅ تم إنشاء حساب المدير بنجاح!")
            st.info("اسم المستخدم: Jarrah01 | كلمة المرور: rrrrr01")
            st.warning("⚠️ احذف هذا الملف من GitHub بعد التشغيل!")

    except Exception as e:
        st.error(f"خطأ: {e}")
