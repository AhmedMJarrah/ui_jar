import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="منظومة تصنيف التشريعات",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&family=Amiri:wght@400;700&display=swap');

:root {
    --bg:#f4f6fb;--bg2:#ffffff;--bg3:#edf0f7;--card:#ffffff;
    --border:#d5daea;--border2:#b8c4d8;
    --accent:#2563eb;--accent2:#6d28d9;--accentlt:#eff4ff;--purple-lt:#f5f0ff;
    --green:#16a34a;--green-lt:#f0fdf4;--green-border:#bbf7d0;
    --orange:#c2550a;--orange-lt:#fff7ed;--orange-border:#fed7aa;
    --text:#1e293b;--text2:#475569;--text3:#94a3b8;
    --law-name:#1e3a8a;--law-bg:linear-gradient(135deg,#eff4ff,#f5f0ff);
    --law-border:#c7d7fb;--val-bg:#edf0f7;
    --shadow:0 2px 14px rgba(30,41,59,0.07);--shadow-md:0 4px 22px rgba(30,41,59,0.11);
    --radius:14px;--progress-bg:#e2e8f0;--input-bg:#ffffff;
    --stat-num-laws:#2563eb;--stat-num-rows:#475569;--stat-num-pct:#6d28d9;
    --stat-num-ok:#16a34a;--stat-num-edit:#c2550a;
}
@media (prefers-color-scheme:dark){:root{
    --bg:#0f1318;--bg2:#161c24;--bg3:#1c2330;--card:#1a2030;
    --border:#2a3448;--border2:#3a4760;--accent:#60a5fa;--accent2:#a78bfa;
    --accentlt:#1e2d4a;--purple-lt:#1e1a38;--green:#34d399;--green-lt:#0d2218;
    --green-border:#065f46;--orange:#fb923c;--orange-lt:#1f1208;--orange-border:#92400e;
    --text:#e2e8f0;--text2:#94a3b8;--text3:#64748b;
    --law-name:#93c5fd;--law-bg:linear-gradient(135deg,#1e2d4a,#1e1a38);
    --law-border:#2e4070;--val-bg:#1c2330;
    --shadow:0 2px 14px rgba(0,0,0,0.35);--shadow-md:0 4px 22px rgba(0,0,0,0.45);
    --progress-bg:#1c2330;--input-bg:#161c24;
    --stat-num-laws:#60a5fa;--stat-num-rows:#94a3b8;--stat-num-pct:#a78bfa;
    --stat-num-ok:#34d399;--stat-num-edit:#fb923c;
}}
[data-theme="dark"]{
    --bg:#0f1318;--bg2:#161c24;--bg3:#1c2330;--card:#1a2030;
    --border:#2a3448;--border2:#3a4760;--accent:#60a5fa;--accent2:#a78bfa;
    --accentlt:#1e2d4a;--purple-lt:#1e1a38;--green:#34d399;--green-lt:#0d2218;
    --green-border:#065f46;--orange:#fb923c;--orange-lt:#1f1208;--orange-border:#92400e;
    --text:#e2e8f0;--text2:#94a3b8;--text3:#64748b;
    --law-name:#93c5fd;--law-bg:linear-gradient(135deg,#1e2d4a,#1e1a38);
    --law-border:#2e4070;--val-bg:#1c2330;
    --shadow:0 2px 14px rgba(0,0,0,0.35);--shadow-md:0 4px 22px rgba(0,0,0,0.45);
    --progress-bg:#1c2330;--input-bg:#161c24;
    --stat-num-laws:#60a5fa;--stat-num-rows:#94a3b8;--stat-num-pct:#a78bfa;
    --stat-num-ok:#34d399;--stat-num-edit:#fb923c;
}

html,body,[class*="css"]{font-family:'Tajawal',sans-serif !important;direction:rtl;background-color:var(--bg) !important;color:var(--text) !important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1.5rem 2rem 3rem 2rem !important;max-width:1100px !important;}

.hero{background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 55%,#4f46e5 100%);border-radius:20px;padding:2rem 3rem;margin-bottom:1.5rem;text-align:center;position:relative;overflow:hidden;box-shadow:var(--shadow-md);}
.hero h1{font-family:'Amiri',serif;font-size:2.2rem;font-weight:700;color:#fff;margin:0 0 0.3rem 0;}
.hero p{color:rgba(255,255,255,0.78);font-size:0.95rem;margin:0;}

.law-card{background:var(--law-bg);border:1px solid var(--law-border);border-right:5px solid var(--accent);border-radius:var(--radius);padding:1.5rem 2rem;margin-bottom:1.5rem;box-shadow:var(--shadow);}
.law-number{font-size:0.78rem;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;}
.law-title{font-family:'Amiri',serif;font-size:1.5rem;font-weight:700;color:var(--law-name);line-height:1.7;}
.law-meta{font-size:0.82rem;color:var(--text3);margin-top:6px;}

.stat-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:1rem 1.2rem;text-align:center;box-shadow:var(--shadow);}
.stat-num{font-size:1.9rem;font-weight:800;line-height:1.1;}
.stat-lbl{font-size:0.78rem;color:var(--text2);margin-top:3px;}

.progress-wrap{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:0.8rem 1.2rem;margin-bottom:1rem;box-shadow:var(--shadow);}
.progress-bar-outer{background:var(--progress-bg);border-radius:99px;height:8px;overflow:hidden;margin-top:6px;}
.progress-bar-inner{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width 0.6s ease;}

.scope-card{background:var(--card);border:2px solid var(--border);border-radius:var(--radius);padding:1.2rem 1.5rem;margin-bottom:0.8rem;cursor:pointer;transition:all 0.2s;box-shadow:var(--shadow);}
.scope-card:hover{border-color:var(--accent);transform:translateY(-2px);}
.scope-card.selected-jamea{border-color:#2563eb;background:var(--accentlt);}
.scope-card.selected-moayyan{border-color:#7c3aed;background:var(--purple-lt);}
.scope-icon{font-size:1.8rem;margin-bottom:0.3rem;}
.scope-title{font-size:1.05rem;font-weight:700;color:var(--text);}
.scope-desc{font-size:0.82rem;color:var(--text2);margin-top:2px;}

.entity-section{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:1.2rem 1.5rem;margin-top:0.8rem;}

.badge{display:inline-block;padding:3px 13px;border-radius:20px;font-size:0.78rem;font-weight:700;}
.badge-new{background:var(--bg3);color:var(--text3);border:1px solid var(--border2);}
.badge-ok{background:var(--green-lt);color:var(--green);border:1px solid var(--green-border);}
.badge-jamea{background:var(--accentlt);color:var(--accent);border:1px solid #c7d7fb;}
.badge-moayyan{background:var(--purple-lt);color:#7c3aed;border:1px solid #d4b8fb;}

.done-banner{background:linear-gradient(135deg,var(--green-lt),var(--accentlt));border:1px solid var(--green-border);border-radius:var(--radius);padding:2rem;text-align:center;margin:1rem 0;}
.done-banner h2{color:var(--green);font-family:'Amiri',serif;font-size:2rem;margin:0 0 0.4rem 0;}

.login-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:2rem;box-shadow:var(--shadow-md);}

.stButton>button{font-family:'Tajawal',sans-serif !important;font-weight:700 !important;border-radius:10px !important;padding:0.55rem 1.4rem !important;font-size:0.95rem !important;transition:all 0.2s !important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{font-family:'Tajawal',sans-serif !important;background:var(--input-bg) !important;border:1.5px solid var(--border) !important;color:var(--text) !important;border-radius:8px !important;direction:rtl !important;font-size:0.97rem !important;}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:var(--accent) !important;box-shadow:0 0 0 3px rgba(96,165,250,0.15) !important;}
.stSelectbox>div>div{background:var(--input-bg) !important;border:1.5px solid var(--border) !important;color:var(--text) !important;border-radius:8px !important;direction:rtl !important;}
.stTextInput label,.stTextArea label,.stSelectbox label,.stRadio label{color:var(--text2) !important;font-family:'Tajawal',sans-serif !important;font-size:0.87rem !important;font-weight:600 !important;}
hr{border-color:var(--border) !important;margin:1.2rem 0 !important;}
.stAlert{border-radius:var(--radius) !important;font-family:'Tajawal',sans-serif !important;}
.stRadio>div{gap:0.5rem !important;}
.stRadio>div>label{background:var(--card);border:1.5px solid var(--border);border-radius:10px;padding:0.7rem 1.2rem !important;transition:all 0.2s;font-size:1rem !important;}
.stRadio>div>label:hover{border-color:var(--accent);}
</style>
""", unsafe_allow_html=True)

# ─── Imports ───────────────────────────────────────────────────────────────────
from auth  import require_login, logout, greeting_page
from admin import admin_panel
from sheets import (
    get_spreadsheet, load_user_rows_v2, save_audited_row_v2,
    load_entities, add_custom_entity, invalidate_master_v2,
)

# ─── Session Defaults ──────────────────────────────────────────────────────────
for k, v in [("logged_in",False),("username",""),("role",""),
             ("assigned_half",""),("groups",None),
             ("cur_law",0),("cur_row",0),
             ("show_greeting",False),
             ("last_sync",None),("sync_ok",True),
             ("streak",0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Auth ──────────────────────────────────────────────────────────────────────
require_login()

# ─── Top Bar ───────────────────────────────────────────────────────────────────
top_left, top_right = st.columns([8, 1])
with top_left:
    role_txt = "🛡️ مدير" if st.session_state.role=="admin" else f"👤 {st.session_state.username}"
    sync_html = ""
    if st.session_state.get("last_sync"):
        cls = "✅" if st.session_state.sync_ok else "⚠️"
        sync_html = f' &nbsp;·&nbsp; <span style="font-size:0.78rem;color:var(--text3)">{cls} {st.session_state.last_sync}</span>'
    st.markdown(f'<span style="font-size:0.9rem;color:var(--text2)">{role_txt}{sync_html}</span>',
                unsafe_allow_html=True)
with top_right:
    if st.button("🚪 خروج", use_container_width=True):
        logout()

# ─── Admin ─────────────────────────────────────────────────────────────────────
if st.session_state.role == "admin":
    admin_panel()
    st.stop()

# ─── Load Data ─────────────────────────────────────────────────────────────────
def build_groups(records):
    seen, groups = {}, []
    for r in records:
        n = r["leg_name"]
        if n not in seen:
            seen[n] = len(groups)
            groups.append({"leg_name": n, "rows": []})
        groups[seen[n]]["rows"].append({
            "row_id":        r["row_id"],
            "leg_name":      r["leg_name"],
            "year":          r.get("year",""),
            "status":        r.get("status",""),
            "scope":         r.get("scope",""),
            "entity_audited":r.get("entity_audited",""),
            "type_audited":  r.get("type_audited",""),
            "custom_entity": r.get("custom_entity",""),
            "custom_type":   r.get("custom_type",""),
            "audit_status":  r.get("audit_status","لم يُراجع"),
            "audit_notes":   r.get("audit_notes",""),
        })
    return groups


if st.session_state.groups is None:
    with st.spinner("جارٍ تحميل بياناتك..."):
        records = load_user_rows_v2(st.session_state.assigned_half)
    if not records:
        invalidate_master_v2()
        records = load_user_rows_v2(st.session_state.assigned_half)
    if not records:
        st.warning("⏳ لم يتم رفع الملف من قِبَل المدير بعد.")
        if st.button("🔄 إعادة المحاولة"):
            st.rerun()
        st.stop()

    st.session_state.groups = build_groups(records)

    # Resume from first unreviewed
    resumed = False
    for li, g in enumerate(st.session_state.groups):
        for ri, r in enumerate(g["rows"]):
            if r["audit_status"] == "لم يُراجع":
                st.session_state.cur_law = li
                st.session_state.cur_row = ri
                resumed = True
                break
        if resumed: break
    if not resumed:
        st.session_state.cur_law = len(st.session_state.groups) - 1
        st.session_state.cur_row = 0

# ─── Stats ─────────────────────────────────────────────────────────────────────
groups     = st.session_state.groups
total_laws = len(groups)
reviewed   = sum(1 for g in groups for r in g["rows"] if r["audit_status"] != "لم يُراجع")
remaining  = total_laws - reviewed
pct        = int(reviewed / total_laws * 100) if total_laws else 0

# ─── Greeting Screen ───────────────────────────────────────────────────────────
if st.session_state.show_greeting:
    greeting_page(
        username  = st.session_state.username,
        total     = total_laws,
        reviewed  = reviewed,
        remaining = remaining,
    )
    st.stop()

# ─── Main Audit UI ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>⚖️ منظومة تصنيف التشريعات</h1>
  <p>صنّف كل قانون — هل ينطبق على جميع الجهات أم جهة معينة؟</p>
</div>
""", unsafe_allow_html=True)

# ── Progress Bar ──
st.markdown(f"""
<div class="progress-wrap">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <span style="font-weight:700;font-size:0.88rem">📊 {reviewed} / {total_laws} قانون مصنَّف</span>
    <span style="font-size:0.82rem;color:var(--text3)">{pct}% مكتمل</span>
  </div>
  <div class="progress-bar-outer">
    <div class="progress-bar-inner" style="width:{pct}%"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# Done banner
if reviewed == total_laws and total_laws > 0:
    st.markdown("""<div class="done-banner">
      <h2>🎉 أنجزت جميع القوانين!</h2>
      <p>عمل رائع! يمكنك تنزيل ملفك أدناه</p>
    </div>""", unsafe_allow_html=True)

# ─── Current Law ───────────────────────────────────────────────────────────────
cur_law = st.session_state.cur_law
cur_row = st.session_state.cur_row

if cur_law >= len(groups):
    cur_law = len(groups) - 1
    st.session_state.cur_law = cur_law

group = groups[cur_law]
rows  = group["rows"]
if cur_row >= len(rows):
    cur_row = 0
    st.session_state.cur_row = 0

row = rows[cur_row]

# Badge
bmap  = {"لم يُراجع":"badge-new","جميع الجهات":"badge-jamea","جهة معينة":"badge-moayyan"}
badge = bmap.get(row["audit_status"], "badge-new")
badge_txt = row["audit_status"] if row["audit_status"] != "لم يُراجع" else "لم يُصنَّف بعد"

# ─── Law Selector ──────────────────────────────────────────────────────────────
def law_label(i, g):
    st_map = {"لم يُراجع":"○","جميع الجهات":"🌐","جهة معينة":"🏢"}
    # Use first row's status as representative
    s = g["rows"][0]["audit_status"] if g["rows"] else "لم يُراجع"
    icon  = st_map.get(s, "○")
    short = g["leg_name"][:60] + ("..." if len(g["leg_name"])>60 else "")
    return f"{icon}  {short}"

law_options = [law_label(i,g) for i,g in enumerate(groups)]
selected = st.selectbox("اختر القانون", options=law_options,
                        index=st.session_state.cur_law,
                        label_visibility="collapsed")
new_idx = law_options.index(selected)
if new_idx != cur_law:
    st.session_state.cur_law = new_idx
    st.session_state.cur_row = 0
    st.rerun()

# Refresh
cur_law = st.session_state.cur_law
group   = groups[cur_law]
rows    = group["rows"]
row     = rows[0]

# ─── Law Card ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="law-card">
  <div class="law-number">القانون {cur_law + 1} من {total_laws}</div>
  <div class="law-title">{group["leg_name"]}</div>
  <div class="law-meta">
    سنة {row.get("year","")} &nbsp;·&nbsp; {row.get("status","")}
    &nbsp;&nbsp;
    <span class="badge {badge}">{badge_txt}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Scope Selection ───────────────────────────────────────────────────────────

# Load entities
entities_records = load_entities()
entity_names = [e["الاسم"] for e in entities_records] + ["أخرى"]
entity_types = sorted(set(e["النوع"] for e in entities_records)) + ["أخرى"]

st.markdown("#### هل ينطبق هذا القانون على:")

scope = st.radio(
    "النطاق",
    options=["جميع الجهات", "جهة معينة"],
    index=0 if row["scope"] != "جهة معينة" else 1,
    horizontal=True,
    label_visibility="collapsed",
    key=f"scope_{cur_law}",
)

# ─── If جميع الجهات → save immediately ────────────────────────────────────────
def save_and_next(scope_val, entity="", etype="",
                  custom_ent="", custom_typ="", notes=""):
    sp = st.session_state.spreadsheet
    try:
        save_audited_row_v2(
            sp,
            row_id        = row["row_id"],
            scope         = scope_val,
            entity_audited= entity,
            type_audited  = etype,
            custom_entity = custom_ent,
            custom_type   = custom_typ,
            audit_status  = scope_val,
            audit_notes   = notes,
        )
        # If custom entity entered, add to entities list
        if custom_ent.strip():
            add_custom_entity(sp, custom_ent.strip(), custom_typ.strip())

        # Update local state
        groups[cur_law]["rows"][0].update({
            "scope":         scope_val,
            "entity_audited":entity,
            "type_audited":  etype,
            "custom_entity": custom_ent,
            "custom_type":   custom_typ,
            "audit_status":  scope_val,
        })
        st.session_state.groups  = groups
        st.session_state.sync_ok = True
        st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
        st.session_state.streak  += 1

        # Move to next law
        if st.session_state.cur_law < total_laws - 1:
            st.session_state.cur_law += 1
            st.session_state.cur_row  = 0
        st.rerun()

    except Exception as e:
        st.session_state.sync_ok = False
        st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
        st.error(f"خطأ في الحفظ: {e}")


if scope == "جميع الجهات":
    st.markdown("""
    <div style="background:var(--accentlt);border:1px solid #c7d7fb;border-radius:10px;
                padding:1rem 1.5rem;margin:0.8rem 0;text-align:center">
      <div style="font-size:1.5rem">🌐</div>
      <div style="font-weight:700;color:var(--accent);margin-top:4px">ينطبق على جميع الجهات</div>
      <div style="font-size:0.82rem;color:var(--text2);margin-top:2px">سيتم الحفظ والانتقال للقانون التالي فوراً</div>
    </div>
    """, unsafe_allow_html=True)

    notes = st.text_area("💬 ملاحظات (اختياري)", value=row["audit_notes"],
                          key=f"notes_jamea_{cur_law}", placeholder="أضف ملاحظة...", height=70)

    col_prev, col_save = st.columns([2, 8])
    with col_prev:
        if st.button("◀ السابق", use_container_width=True):
            if st.session_state.cur_law > 0:
                st.session_state.cur_law -= 1
                st.rerun()
    with col_save:
        if st.button("✅ اعتماد — جميع الجهات", use_container_width=True, type="primary"):
            save_and_next("جميع الجهات", notes=notes)

# ─── If جهة معينة ─────────────────────────────────────────────────────────────
else:
    st.markdown('<div class="entity-section">', unsafe_allow_html=True)
    st.markdown("##### 🏢 تفاصيل الجهة")

    c_entity, c_type = st.columns(2)

    with c_entity:
        current_entity = row["entity_audited"] if row["entity_audited"] in entity_names else entity_names[0]
        selected_entity = st.selectbox(
            "اسم الجهة",
            options=entity_names,
            index=entity_names.index(current_entity) if current_entity in entity_names else 0,
            key=f"entity_{cur_law}",
        )
        custom_entity = ""
        if selected_entity == "أخرى":
            custom_entity = st.text_input(
                "أدخل اسم الجهة يدوياً",
                value=row.get("custom_entity",""),
                key=f"custom_ent_{cur_law}",
                placeholder="اسم الجهة...",
            )

    with c_type:
        current_type = row["type_audited"] if row["type_audited"] in entity_types else entity_types[0]
        selected_type = st.selectbox(
            "نوع الجهة",
            options=entity_types,
            index=entity_types.index(current_type) if current_type in entity_types else 0,
            key=f"type_{cur_law}",
        )
        custom_type = ""
        if selected_type == "أخرى":
            custom_type = st.text_input(
                "أدخل نوع الجهة يدوياً",
                value=row.get("custom_type",""),
                key=f"custom_typ_{cur_law}",
                placeholder="نوع الجهة...",
            )

    st.markdown('</div>', unsafe_allow_html=True)

    notes = st.text_area("💬 ملاحظات (اختياري)", value=row["audit_notes"],
                          key=f"notes_moayyan_{cur_law}", placeholder="أضف ملاحظة...", height=70)

    col_prev, col_save = st.columns([2, 8])
    with col_prev:
        if st.button("◀ السابق", use_container_width=True):
            if st.session_state.cur_law > 0:
                st.session_state.cur_law -= 1
                st.rerun()
    with col_save:
        # Validate
        final_entity = custom_entity if selected_entity == "أخرى" else selected_entity
        final_type   = custom_type   if selected_type   == "أخرى" else selected_type

        if st.button("✅ اعتماد — جهة معينة", use_container_width=True, type="primary"):
            if not final_entity.strip():
                st.error("الرجاء اختيار أو إدخال اسم الجهة")
            elif not final_type.strip():
                st.error("الرجاء اختيار أو إدخال نوع الجهة")
            else:
                save_and_next(
                    "جهة معينة",
                    entity     = final_entity if selected_entity != "أخرى" else "",
                    etype      = final_type   if selected_type   != "أخرى" else "",
                    custom_ent = custom_entity,
                    custom_typ = custom_type,
                    notes      = notes,
                )

# ─── Streak ────────────────────────────────────────────────────────────────────
if st.session_state.streak > 0 and st.session_state.streak % 10 == 0:
    st.success(f"🔥 رائع! أنجزت {st.session_state.streak} قانوناً متتالياً!")

# ─── Download ──────────────────────────────────────────────────────────────────
st.markdown("---")
rows_flat = [r for g in groups for r in g["rows"]]
df_dl = pd.DataFrame([{
    "leg_name":      r["leg_name"],
    "scope":         r["scope"],
    "entity_audited":r["entity_audited"],
    "type_audited":  r["type_audited"],
    "custom_entity": r["custom_entity"],
    "custom_type":   r["custom_type"],
    "audit_status":  r["audit_status"],
    "audit_notes":   r["audit_notes"],
} for r in rows_flat])
buf = io.BytesIO()
df_dl.to_excel(buf, index=False)
buf.seek(0)
st.download_button(
    label="⬇️ تنزيل ملفي",
    data=buf,
    file_name=f"تصنيف_{st.session_state.username}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
