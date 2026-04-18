"""
admin.py — Admin panel
"""
import streamlit as st
import pandas as pd
import io
from sheets import (
    get_spreadsheet, upload_master_file, get_master_df,
    get_all_users_progress, load_users,
    create_user, delete_user, update_password,
    invalidate_master,
)


def admin_panel():
    sp = st.session_state.spreadsheet

    st.markdown("""
    <div class="hero">
      <div style="font-size:2.5rem;margin-bottom:0.3rem">🛡️</div>
      <h1>لوحة الإدارة</h1>
      <p>رفع الملف · إدارة المستخدمين · متابعة التقدم</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📂 رفع الملف",
        "📊 لوحة التقدم",
        "👥 إدارة المستخدمين",
        "📋 سجل التغييرات",
    ])

    # ── Tab 1: File Upload ─────────────────────────────────────────────────────
    with tab1:
        st.markdown("### 📂 رفع ملف التشريعات الرئيسي")
        st.info("بعد الرفع، يُقسَّم الملف تلقائياً 50/50 بين المستخدمَين حسب القوانين الفريدة.")

        uploaded = st.file_uploader(
            "اختر ملف CSV أو Excel",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed",
        )

        if uploaded:
            try:
                from pathlib import Path
                ext = Path(uploaded.name).suffix.lower()
                df  = pd.read_csv(uploaded, encoding="utf-8-sig") if ext == ".csv" else pd.read_excel(uploaded)
                missing = {"leg_name", "entity_final", "type"} - set(df.columns)
                if missing:
                    st.error(f"❌ الأعمدة التالية غير موجودة: {', '.join(missing)}")
                else:
                    st.markdown(f"**معاينة الملف:** {len(df)} سجل · {df['leg_name'].nunique()} قانون فريد")
                    st.dataframe(df.head(5), use_container_width=True, hide_index=True)

                    if st.button("✅ رفع وحفظ الملف", type="primary", use_container_width=True):
                        with st.spinner("جارٍ الرفع والتقسيم... قد يستغرق دقيقة"):
                            n = upload_master_file(sp, df)
                        st.success(f"✅ تم رفع {n} سجل وتقسيمه بين المستخدمَين!")
                        st.balloons()
            except Exception as e:
                st.error(f"خطأ: {e}")

        # Download current master
        st.markdown("---")
        st.markdown("### ⬇️ تنزيل الملف الكامل المعدّل")
        if st.button("تحميل الملف", use_container_width=True):
            with st.spinner("جارٍ التحميل..."):
                df_master = get_master_df(sp)
            if df_master.empty:
                st.warning("لا يوجد ملف مرفوع بعد.")
            else:
                buf = io.BytesIO()
                df_master.to_excel(buf, index=False)
                buf.seek(0)
                st.download_button(
                    "⬇️ تنزيل Excel",
                    data=buf,
                    file_name="master_audit_complete.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary",
                )

    # ── Tab 2: Progress ────────────────────────────────────────────────────────
    with tab2:
        st.markdown("### 📊 تقدم المراجعة")
        if st.button("🔄 تحديث", key="refresh"):
            st.cache_data.clear()
            st.rerun()

        with st.spinner("جارٍ التحميل..."):
            progress = get_all_users_progress()

        if not progress:
            st.info("لا يوجد مراجعون بعد.")
        else:
            total_records  = sum(p["total"]    for p in progress)
            total_reviewed = sum(p["reviewed"] for p in progress)
            overall_pct    = int(total_reviewed / total_records * 100) if total_records else 0

            c1, c2, c3, c4 = st.columns(4)
            for col, (num, lbl, color) in zip([c1,c2,c3,c4], [
                (len(progress),   "إجمالي المراجعين",   "var(--stat-num-laws)"),
                (total_records,   "إجمالي السجلات",     "var(--stat-num-rows)"),
                (total_reviewed,  "سجلات مراجَعة",      "var(--stat-num-ok)"),
                (f"{overall_pct}%","نسبة الإنجاز الكلية","var(--stat-num-pct)"),
            ]):
                with col:
                    st.markdown(f"""<div class="stat-card">
                        <div class="stat-num" style="color:{color}">{num}</div>
                        <div class="stat-lbl">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

            for p in progress:
                pct   = p["pct"]
                color = "#16a34a" if pct == 100 else "#2563eb"
                last  = p["last_active"][:16].replace("T", " ") if p["last_active"] else "لم يبدأ"
                st.markdown(f"""
                <div class="progress-wrap" style="margin-bottom:0.8rem">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-weight:700">👤 {p["username"]}
                      <span style="font-size:0.78rem;color:var(--text3);margin-right:8px">
                        النصف {p["assigned_half"]}
                      </span>
                    </span>
                    <span style="font-size:0.8rem;color:var(--text3)">آخر نشاط: {last}</span>
                  </div>
                  <div style="font-size:0.82rem;color:var(--text2);margin:4px 0 6px 0">
                    {p["reviewed"]}/{p["total"]} سجل &nbsp;·&nbsp;
                    <span style="color:var(--orange)">✏️ {p["modified"]} معدّل</span> &nbsp;·&nbsp;
                    <span style="color:{color};font-weight:700">{pct}%</span>
                  </div>
                  <div class="progress-bar-outer">
                    <div class="progress-bar-inner" style="width:{pct}%;background:{color}"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 3: Users ───────────────────────────────────────────────────────────
    with tab3:
        col_new, col_list = st.columns([1, 1])

        with col_new:
            st.markdown("#### ➕ إنشاء مستخدم")
            # Check how many auditors exist
            users    = load_users()
            auditors = [u for u in users.values() if u["role"] == "auditor"]
            halves   = [u.get("assigned_half", "") for u in auditors]

            new_user = st.text_input("اسم المستخدم", key="nu", placeholder="مثال: user1")
            new_pass = st.text_input("كلمة المرور",  key="np", type="password")
            new_role = st.selectbox("الصلاحية", ["auditor", "admin"], key="nr")

            if new_role == "auditor":
                available = []
                if "1" not in halves: available.append("النصف الأول (قوانين 1-1165)")
                if "2" not in halves: available.append("النصف الثاني (قوانين 1166-2331)")
                if available:
                    st.info(f"سيُخصَّص تلقائياً: {available[0]}")
                else:
                    st.warning("⚠️ كلا المستخدمَين محجوزان. احذف أحدهما أولاً.")

            if st.button("✅ إنشاء", use_container_width=True, type="primary"):
                if new_user and new_pass:
                    with st.spinner("جارٍ الإنشاء..."):
                        ok, msg = create_user(sp, new_user.strip(), new_pass, new_role)
                    st.success(msg) if ok else st.error(msg)
                    if ok:
                        from sheets import invalidate_users
                        invalidate_users()
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.warning("الرجاء تعبئة جميع الحقول")

        with col_list:
            st.markdown("#### 👥 المستخدمون")
            from sheets import invalidate_users
            invalidate_users()
            users = load_users()
            for uname, info in users.items():
                icon = "🛡️" if info["role"] == "admin" else "👤"
                half = f" · النصف {info.get('assigned_half','')}" if info["role"] == "auditor" else ""
                with st.expander(f"{icon} {uname}{half}"):
                    np2 = st.text_input("كلمة مرور جديدة", type="password",
                                        key=f"np2_{uname}", placeholder="اتركه فارغاً")
                    if st.button("💾 تحديث كلمة المرور", key=f"upd_{uname}"):
                        if np2:
                            update_password(sp, uname, np2)
                            st.success("تم")
                    if uname != st.session_state.username:
                        if st.button(f"🗑️ حذف {uname}", key=f"del_{uname}"):
                            delete_user(sp, uname)
                            st.success(f"تم حذف {uname}")
                            st.rerun()

    # ── Tab 4: Audit Log ───────────────────────────────────────────────────────
    with tab4:
        st.markdown("#### 📋 سجل التغييرات")
        try:
            sp2 = get_spreadsheet()
            ws  = sp2.worksheet("audit_log")
            df  = pd.DataFrame(safe_call(ws.get_all_records))
            if df.empty:
                st.info("لا توجد تغييرات بعد.")
            else:
                df = df.sort_values("timestamp", ascending=False)
                df.columns = ["التوقيت","المستخدم","القانون","الحقل","القيمة القديمة","القيمة الجديدة"]
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception:
            st.info("لا توجد تغييرات بعد.")


def safe_call(fn, retries=3, wait=5):
    import time, gspread
    for attempt in range(retries):
        try:
            return fn()
        except gspread.exceptions.APIError as e:
            if "429" in str(e) and attempt < retries - 1:
                time.sleep(wait * (attempt + 1))
            else:
                raise
