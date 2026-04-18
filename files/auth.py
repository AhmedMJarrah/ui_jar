"""
auth.py — Login page and session helpers
"""
import streamlit as st
from sheets import get_spreadsheet, verify_password


def login_page():
    """Render login form. Returns True if logged in."""

    st.markdown("""
    <div style="max-width:420px;margin:3rem auto 0 auto;">
      <div style="text-align:center;margin-bottom:2rem">
        <div style="font-size:3rem">⚖️</div>
        <h2 style="font-family:'Amiri',serif;font-size:1.9rem;margin:0.3rem 0 0.2rem 0">
          منظومة مراجعة التشريعات
        </h2>
        <p style="color:var(--text2);font-size:0.95rem;margin:0">
          الرجاء تسجيل الدخول للمتابعة
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        with st.container():
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم",
                                     key="login_user")
            password = st.text_input("🔒 كلمة المرور", type="password",
                                     placeholder="أدخل كلمة المرور", key="login_pass")

            if st.button("تسجيل الدخول", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("الرجاء إدخال اسم المستخدم وكلمة المرور")
                    return False
                with st.spinner("جارٍ التحقق..."):
                    try:
                        sp   = get_spreadsheet()
                        ok, user_info = verify_password(sp, username.strip(), password)
                        if ok:
                            st.session_state.logged_in   = True
                            st.session_state.username    = username.strip()
                            st.session_state.role        = user_info["role"]
                            st.session_state.spreadsheet = sp
                            st.rerun()
                        else:
                            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                    except Exception as e:
                        st.error(f"خطأ في الاتصال: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
    return False


def require_login():
    """Call at top of every page. Redirects to login if not authenticated."""
    if not st.session_state.get("logged_in"):
        login_page()
        st.stop()


def logout():
    keys = ["logged_in", "username", "role", "spreadsheet",
            "groups", "original_df", "cur_law", "cur_row",
            "file_ext", "file_name"]
    for k in keys:
        st.session_state.pop(k, None)
    st.rerun()
