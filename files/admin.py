"""
admin.py — Admin Panel (v2)
"""
import streamlit as st
import pandas as pd
import io
from sheets import (
    get_spreadsheet, upload_master_v2, get_master_v2_df,
    get_progress_v2, load_users, create_user, delete_user,
    update_password, invalidate_users, load_entities,
    get_all_users_progress,
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
        "📂 رفع ملف جديد",
        "📊 لوحة التقدم",
        "👥 إدارة المستخدمين",
        "📋 سجل التغييرات",
    ])

    # ── Tab 1: Upload ──────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### 📂 رفع ملف التشريعات الجديد (v2)")
        st.info("يُقسَّم الملف تلقائياً بالتساوي بين 5 مستخدمين. يجب رفع ملف الجهات أيضاً.")

        col1, col2 = st.columns(2)
        with col1:
            laws_file = st.file_uploader("📜 ملف القوانين (Excel/CSV)", type=["xlsx","xls","csv"], key="laws_up")
        with col2:
            entities_file = st.file_uploader("🏢 ملف الجهات (CSV)", type=["csv","xlsx","xls"], key="ent_up")

        if laws_file and entities_file:
            try:
                from pathlib import Path
                # Load laws
                ext = Path(laws_file.name).suffix.lower()
                df_laws = pd.read_csv(laws_file, encoding="utf-8-sig") if ext==".csv" else pd.read_excel(laws_file)

                # Load entities
                ext2 = Path(entities_file.name).suffix.lower()
                df_ent = pd.read_csv(entities_file, encoding="utf-8-sig") if ext2==".csv" else pd.read_excel(entities_file)

                st.markdown(f"**القوانين:** {len(df_laws)} سجل · {df_laws['leg_name'].nunique()} قانون فريد")
                st.markdown(f"**الجهات:** {len(df_ent)} جهة")
                st.dataframe(df_laws.head(3), use_container_width=True, hide_index=True)

                if st.button("✅ رفع وتقسيم", type="primary", use_container_width=True):
                    with st.spinner("جارٍ الرفع..."):
                        n = upload_master_v2(sp, df_laws, df_ent)
                    st.success(f"✅ تم رفع {n} سجل!")
                    st.balloons()
            except Exception as e:
                st.error(f"خطأ: {e}")

        st.markdown("---")
        st.markdown("### ⬇️ تنزيل الملف الكامل (v2)")
        if st.button("تحميل", key="dl_v2"):
            with st.spinner("جارٍ التحميل..."):
                df = get_master_v2_df()
            if df.empty:
                st.warning("لا يوجد ملف مرفوع.")
            else:
                buf = io.BytesIO()
                df.to_excel(buf, index=False)
                buf.seek(0)
                st.download_button("⬇️ تنزيل Excel", data=buf,
                    file_name="master_v2_complete.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True, type="primary")

    # ── Tab 2: Progress ────────────────────────────────────────────────────────
    with tab2:
        st.markdown("### 📊 تقدم المراجعة — النظام الجديد")
        if st.button("🔄 تحديث", key="ref_v2"):
            st.cache_data.clear(); st.rerun()

        progress = get_progress_v2()
        if not progress:
            st.info("لا يوجد بيانات بعد.")
        else:
            total_r  = sum(p["total"]    for p in progress)
            total_rv = sum(p["reviewed"] for p in progress)
            opct     = int(total_rv / total_r * 100) if total_r else 0

            c1,c2,c3,c4 = st.columns(4)
            for col,(num,lbl,color) in zip([c1,c2,c3,c4],[
                (len(progress),"إجمالي المراجعين","var(--stat-num-laws)"),
                (total_r,     "إجمالي القوانين", "var(--stat-num-rows)"),
                (total_rv,    "تم تصنيفها",       "var(--stat-num-ok)"),
                (f"{opct}%",  "نسبة الإنجاز",     "var(--stat-num-pct)"),
            ]):
                with col:
                    st.markdown(f"""<div class="stat-card">
                        <div class="stat-num" style="color:{color}">{num}</div>
                        <div class="stat-lbl">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

            for p in progress:
                pct   = p["pct"]
                color = "#16a34a" if pct==100 else "#2563eb"
                last  = p["last_active"][:16].replace("T"," ") if p["last_active"] else "لم يبدأ"
                st.markdown(f"""
                <div class="progress-wrap" style="margin-bottom:0.8rem">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-weight:700">👤 {p["username"]}
                      <span style="font-size:0.78rem;color:var(--text3);margin-right:8px">النصف {p["half"]}</span>
                    </span>
                    <span style="font-size:0.8rem;color:var(--text3)">آخر نشاط: {last}</span>
                  </div>
                  <div style="font-size:0.82rem;color:var(--text2);margin:4px 0 6px 0;display:flex;gap:1rem">
                    <span>{p["reviewed"]}/{p["total"]} قانون</span>
                    <span style="color:#2563eb">🌐 جميع الجهات: {p["jamea"]}</span>
                    <span style="color:#7c3aed">🏢 جهة معينة: {p["moayyan"]}</span>
                    <span style="color:{color};font-weight:700">{pct}%</span>
                  </div>
                  <div class="progress-bar-outer">
                    <div class="progress-bar-inner" style="width:{pct}%;background:{color}"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 3: Users ───────────────────────────────────────────────────────────
    with tab3:
        col_new, col_list = st.columns([1,1])
        with col_new:
            st.markdown("#### ➕ إنشاء مستخدم")
            nu = st.text_input("اسم المستخدم", key="nu", placeholder="مثال: user1")
            np = st.text_input("كلمة المرور",  key="np", type="password")
            nr = st.selectbox("الصلاحية", ["auditor","admin"], key="nr")
            if st.button("✅ إنشاء", use_container_width=True, type="primary"):
                if nu and np:
                    with st.spinner("جارٍ الإنشاء..."):
                        ok, msg = create_user(sp, nu.strip(), np, nr)
                    st.success(msg) if ok else st.error(msg)
                    if ok:
                        invalidate_users()
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.warning("الرجاء تعبئة جميع الحقول")

        with col_list:
            st.markdown("#### 👥 المستخدمون")
            invalidate_users()
            users = load_users()
            for uname, info in users.items():
                icon = "🛡️" if info["role"]=="admin" else "👤"
                half = f" · النصف {info.get('assigned_half','')}" if info["role"]=="auditor" else ""
                with st.expander(f"{icon} {uname}{half}"):
                    np2 = st.text_input("كلمة مرور جديدة", type="password", key=f"np2_{uname}")
                    if st.button("💾 تحديث", key=f"upd_{uname}"):
                        if np2: update_password(sp, uname, np2); st.success("تم")
                    if uname != st.session_state.username:
                        if st.button(f"🗑️ حذف", key=f"del_{uname}"):
                            delete_user(sp, uname); st.success(f"تم حذف {uname}"); st.rerun()

    # ── Tab 4: Audit Log ───────────────────────────────────────────────────────
    with tab4:
        st.markdown("#### 📋 سجل التغييرات")
        try:
            ws  = sp.worksheet("audit_log")
            df  = pd.DataFrame(ws.get_all_records())
            if df.empty:
                st.info("لا توجد تغييرات بعد.")
            else:
                df = df.sort_values("timestamp", ascending=False)
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception:
            st.info("لا توجد تغييرات بعد.")
