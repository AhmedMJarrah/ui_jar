"""
setup_lob.py — Run once to create lob user with half 5
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

st.title("⚙️ إنشاء مستخدم lob")

if st.button("إنشاء مستخدم lob", type="primary"):
    try:
        creds  = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=SCOPES)
        client = gspread.authorize(creds)
        sp     = client.open_by_key(SPREADSHEET_ID)
        ws     = sp.worksheet("users")

        records = ws.get_all_records()
        if any(r["username"] == "lob" for r in records):
            st.warning("المستخدم lob موجود مسبقاً!")
        else:
            hashed = bcrypt.hashpw("lob12345".encode(), bcrypt.gensalt()).decode()
            ws.append_row(["lob", hashed, "auditor",
                           datetime.now().isoformat(), "", "5"])
            st.success("✅ تم إنشاء المستخدم lob بنجاح!")
            st.info("اسم المستخدم: lob | كلمة المرور: lob12345 | النصف: 5")
            st.warning("⚠️ احذف هذا الملف من GitHub بعد التشغيل!")
    except Exception as e:
        st.error(f"خطأ: {e}")
