"""
auth.py — Login page and session helpers
"""
import streamlit as st
from sheets import get_spreadsheet, verify_password


def login_page():
    st.markdown("""
    <div style="max-width:420px;margin:4rem auto 0 auto;text-align:center">
      <div style="font-size:3.5rem;margin-bottom:0.5rem">⚖️</div>
      <h2 style="font-family:'Amiri',serif;font-size:2rem;margin:0 0 0.3rem 0">
        منظومة مراجعة التشريعات
      </h2>
      <p style="color:var(--text2);margin:0 0 2rem 0">الرجاء تسجيل الدخول للمتابعة</p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم", key="login_user")
        password = st.text_input("🔒 كلمة المرور", type="password", placeholder="أدخل كلمة المرور", key="login_pass")

        if st.button("تسجيل الدخول", use_container_width=True, type="primary"):
            if not username or not password:
                st.error("الرجاء إدخال اسم المستخدم وكلمة المرور")
                return False
            with st.spinner("جارٍ التحقق..."):
                try:
                    sp = get_spreadsheet()
                    ok, user_info = verify_password(sp, username.strip(), password)
                    if ok:
                        st.session_state.logged_in    = True
                        st.session_state.username     = username.strip()
                        st.session_state.role         = user_info["role"]
                        st.session_state.assigned_half = str(user_info.get("assigned_half", "")).strip()
                        st.session_state.spreadsheet  = sp
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                except Exception as e:
                    st.error(f"خطأ في الاتصال: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    return False


def require_login():
    if not st.session_state.get("logged_in"):
        login_page()
        st.stop()


def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()
