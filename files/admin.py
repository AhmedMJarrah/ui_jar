"""
admin.py — Admin panel
"""
import streamlit as st
from sheets import (
    get_all_users_progress, load_users,
    create_user, delete_user, update_password,
    load_user_data, rebuild_groups_from_sheet,
)
import pandas as pd
import io


def admin_panel():
    sp = st.session_state.spreadsheet

    st.markdown("""
    <div class="hero">
      <div style="font-size:2.5rem;margin-bottom:0.3rem">🛡️</div>
      <h1>لوحة الإدارة</h1>
      <p>إدارة المستخدمين ومتابعة تقدم المراجعة</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 لوحة التقدم", "👥 إدارة المستخدمين", "📋 سجل التغييرات"])

    # ── Tab 1: Progress Dashboard ──────────────────────────────────────────────
    with tab1:
        st.markdown("### تقدم المراجعة لكل مستخدم")
        if st.button("🔄 تحديث", key="refresh_progress"):
            st.rerun()

        with st.spinner("جارٍ تحميل البيانات..."):
            progress = get_all_users_progress(sp)

        if not progress:
            st.info("لا يوجد مستخدمون بعد أو لم يرفعوا ملفات.")
        else:
            # Summary stats
            total_users    = len(progress)
            done_users     = sum(1 for p in progress if p["pct"] == 100)
            total_records  = sum(p["total"]    for p in progress)
            total_reviewed = sum(p["reviewed"] for p in progress)
            overall_pct    = int(total_reviewed / total_records * 100) if total_records else 0

            c1, c2, c3, c4 = st.columns(4)
            for col, (num, lbl, color) in zip(
                [c1, c2, c3, c4],
                [(total_users,   "إجمالي المراجعين",  "var(--stat-num-laws)"),
                 (done_users,    "أكملوا المراجعة",   "var(--stat-num-ok)"),
                 (total_records, "إجمالي السجلات",    "var(--stat-num-rows)"),
                 (f"{overall_pct}%", "نسبة الإنجاز الكلية", "var(--stat-num-pct)")]
            ):
                with col:
                    st.markdown(f"""<div class="stat-card">
                        <div class="stat-num" style="color:{color}">{num}</div>
                        <div class="stat-lbl">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)

            for p in progress:
                pct      = p["pct"]
                bar_color = "#16a34a" if pct == 100 else "#2563eb"
                last      = p["last_active"][:16].replace("T", " ") if p["last_active"] else "لم يبدأ بعد"
                st.markdown(f"""
                <div class="progress-wrap" style="margin-bottom:0.8rem">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-weight:700;font-size:0.95rem">👤 {p["username"]}</span>
                    <span style="font-size:0.8rem;color:var(--text3)">آخر نشاط: {last}</span>
                  </div>
                  <div style="display:flex;gap:1.5rem;margin:4px 0 6px 0;font-size:0.82rem;color:var(--text2)">
                    <span>{p["reviewed"]}/{p["total"]} سجل</span>
                    <span style="color:var(--orange)">✏️ {p["modified"]} معدّل</span>
                    <span style="color:{bar_color};font-weight:700">{pct}%</span>
                  </div>
                  <div class="progress-bar-outer">
                    <div class="progress-bar-inner" style="width:{pct}%;background:{bar_color}"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                # Download user's file
                try:
                    records = load_user_data(sp, p["username"])
                    if records:
                        df = pd.DataFrame(records)
                        buf = io.BytesIO()
                        df.to_excel(buf, index=False)
                        buf.seek(0)
                        st.download_button(
                            f"⬇️ تنزيل ملف {p['username']}",
                            data=buf,
                            file_name=f"{p['username']}_مراجعة.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_{p['username']}",
                        )
                except Exception:
                    pass
                st.markdown("---")

    # ── Tab 2: User Management ─────────────────────────────────────────────────
    with tab2:
        col_create, col_list = st.columns([1, 1])

        with col_create:
            st.markdown("#### ➕ إنشاء مستخدم جديد")
            new_user  = st.text_input("اسم المستخدم", key="new_username", placeholder="مثال: ahmed")
            new_pass  = st.text_input("كلمة المرور",  key="new_password", type="password")
            new_role  = st.selectbox("الصلاحية", ["auditor", "admin"], key="new_role")
            if st.button("✅ إنشاء المستخدم", use_container_width=True, type="primary"):
                if new_user and new_pass:
                    with st.spinner("جارٍ الإنشاء..."):
                        ok, msg = create_user(sp, new_user.strip(), new_pass, new_role)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("الرجاء تعبئة جميع الحقول")

        with col_list:
            st.markdown("#### 👥 المستخدمون الحاليون")
            with st.spinner("جارٍ التحميل..."):
                users = load_users(sp)

            for uname, info in users.items():
                role_badge = "🛡️ Admin" if info["role"] == "admin" else "👤 مراجع"
                with st.expander(f"{role_badge} — {uname}"):
                    st.markdown(f"**الصلاحية:** {info['role']}")
                    st.markdown(f"**تاريخ الإنشاء:** {info.get('created_at','')[:10]}")

                    # Change password
                    np = st.text_input("كلمة مرور جديدة", type="password",
                                       key=f"np_{uname}", placeholder="اتركه فارغاً للإبقاء")
                    if st.button("💾 تحديث كلمة المرور", key=f"upd_{uname}"):
                        if np:
                            update_password(sp, uname, np)
                            st.success("تم التحديث")

                    # Delete (can't delete yourself)
                    if uname != st.session_state.username:
                        if st.button(f"🗑️ حذف {uname}", key=f"del_{uname}",
                                     type="secondary"):
                            delete_user(sp, uname)
                            st.success(f"تم حذف {uname}")
                            st.rerun()
                    else:
                        st.caption("لا يمكنك حذف حسابك الخاص")

    # ── Tab 3: Audit Log ───────────────────────────────────────────────────────
    with tab3:
        st.markdown("#### 📋 سجل التغييرات")
        try:
            ws  = sp.worksheet("audit_log")
            df  = pd.DataFrame(ws.get_all_records())
            if df.empty:
                st.info("لا توجد تغييرات مسجّلة بعد.")
            else:
                df = df.sort_values("timestamp", ascending=False)
                df.columns = ["التوقيت", "المستخدم", "القانون", "الحقل", "القيمة القديمة", "القيمة الجديدة"]
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception:
            st.info("لا توجد تغييرات مسجّلة بعد.")
