"""
auth.py — Login + Greeting
"""
import streamlit as st
from sheets import get_spreadsheet, verify_password


def login_page():
    st.markdown("""
    <div style="max-width:440px;margin:5rem auto 0 auto;text-align:center">
      <div style="font-size:4rem;margin-bottom:0.5rem">⚖️</div>
      <h2 style="font-family:'Amiri',serif;font-size:2.2rem;margin:0 0 0.3rem 0;color:var(--text)">
        منظومة تصنيف التشريعات
      </h2>
      <p style="color:var(--text2);margin:0 0 2.5rem 0;font-size:1rem">
        تسجيل الدخول للمتابعة
      </p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم", key="login_user")
        password = st.text_input("🔒 كلمة المرور", type="password", placeholder="أدخل كلمة المرور", key="login_pass")
        if st.button("تسجيل الدخول →", use_container_width=True, type="primary"):
            if not username or not password:
                st.error("الرجاء إدخال اسم المستخدم وكلمة المرور")
                return False
            with st.spinner("جارٍ التحقق..."):
                try:
                    sp = get_spreadsheet()
                    ok, user_info = verify_password(sp, username.strip(), password)
                    if ok:
                        st.session_state.logged_in     = True
                        st.session_state.username      = username.strip()
                        st.session_state.role          = user_info["role"]
                        st.session_state.assigned_half = str(user_info.get("assigned_half","")).strip()
                        st.session_state.spreadsheet   = sp
                        st.session_state.show_greeting = True
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                except Exception as e:
                    st.error(f"خطأ في الاتصال: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    return False


def greeting_page(username: str, total: int, reviewed: int, remaining: int):
    """Show personalized greeting with start button."""
    pct = int(reviewed / total * 100) if total else 0

    # Pick motivational message based on progress
    if pct == 0:
        msg = "كل رحلة تبدأ بخطوة! أنت على وشك البداية 🌟"
        energy = "#2563eb"
    elif pct < 25:
        msg = "بداية رائعة! استمر وأنت في الطريق الصحيح 💪"
        energy = "#7c3aed"
    elif pct < 50:
        msg = "ممتاز! أنجزت ربع العمل، تقدم رائع 🔥"
        energy = "#ea580c"
    elif pct < 75:
        msg = "نصف الطريق خلفك! أنت نجم حقيقي ⭐"
        energy = "#16a34a"
    elif pct < 100:
        msg = "أوشكت على الانتهاء! لا تتوقف الآن 🚀"
        energy = "#16a34a"
    else:
        msg = "أنجزت جميع القوانين! عمل استثنائي 🎉"
        energy = "#16a34a"

    st.markdown(f"""
    <div style="max-width:600px;margin:4rem auto;text-align:center">
      <div style="font-size:4rem;margin-bottom:1rem">👋</div>
      <h1 style="font-family:'Amiri',serif;font-size:2.8rem;margin:0 0 0.5rem 0;color:var(--text)">
        أهلاً، {username}!
      </h1>
      <p style="font-size:1.1rem;color:{energy};font-weight:700;margin:0 0 2rem 0">
        {msg}
      </p>

      <div style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:1.5rem 2rem;margin-bottom:2rem;box-shadow:var(--shadow)">
        <div style="display:flex;justify-content:space-around;margin-bottom:1rem">
          <div>
            <div style="font-size:2rem;font-weight:800;color:var(--accent)">{total}</div>
            <div style="font-size:0.8rem;color:var(--text2)">إجمالي القوانين</div>
          </div>
          <div>
            <div style="font-size:2rem;font-weight:800;color:#16a34a">{reviewed}</div>
            <div style="font-size:0.8rem;color:var(--text2)">تم تصنيفها</div>
          </div>
          <div>
            <div style="font-size:2rem;font-weight:800;color:{energy}">{remaining}</div>
            <div style="font-size:0.8rem;color:var(--text2)">متبقية</div>
          </div>
        </div>
        <div style="background:var(--progress-bg);border-radius:99px;height:10px;overflow:hidden">
          <div style="height:100%;border-radius:99px;background:linear-gradient(90deg,var(--accent),{energy});width:{pct}%;transition:width 1s ease"></div>
        </div>
        <div style="font-size:0.82rem;color:var(--text3);margin-top:6px">{pct}% مكتمل</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        if pct == 100:
            st.success("🎉 أنجزت جميع القوانين المخصصة لك!")
        else:
            if st.button("🚀 ابدأ المراجعة", use_container_width=True, type="primary"):
                st.session_state.show_greeting = False
                st.rerun()


def require_login():
    if not st.session_state.get("logged_in"):
        login_page()
        st.stop()


def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()
