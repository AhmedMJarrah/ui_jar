import streamlit as st
import pandas as pd
import io
from pathlib import Path
from datetime import datetime

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="مراجع التشريعات",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&family=Amiri:wght@400;700&display=swap');

/* ══ LIGHT ══ */
:root {
    --bg:           #f4f6fb;
    --bg2:          #ffffff;
    --bg3:          #edf0f7;
    --card:         #ffffff;
    --border:       #d5daea;
    --border2:      #b8c4d8;
    --accent:       #2563eb;
    --accent2:      #6d28d9;
    --accentlt:     #eff4ff;
    --purple-lt:    #f5f0ff;
    --green:        #16a34a;
    --green-lt:     #f0fdf4;
    --green-border: #bbf7d0;
    --orange:       #c2550a;
    --orange-lt:    #fff7ed;
    --orange-border:#fed7aa;
    --red:          #dc2626;
    --text:         #1e293b;
    --text2:        #475569;
    --text3:        #94a3b8;
    --law-name:     #1e3a8a;
    --law-bg:       linear-gradient(135deg,#eff4ff,#f5f0ff);
    --law-border:   #c7d7fb;
    --val-bg:       #edf0f7;
    --shadow:       0 2px 14px rgba(30,41,59,0.07);
    --shadow-md:    0 4px 22px rgba(30,41,59,0.11);
    --radius:       14px;
    --progress-bg:  #e2e8f0;
    --input-bg:     #ffffff;
    --stat-num-laws:#2563eb;
    --stat-num-rows:#475569;
    --stat-num-pct: #6d28d9;
    --stat-num-ok:  #16a34a;
    --stat-num-edit:#c2550a;
}

/* ══ DARK ══ */
@media (prefers-color-scheme: dark) { :root {
    --bg:#0f1318; --bg2:#161c24; --bg3:#1c2330; --card:#1a2030;
    --border:#2a3448; --border2:#3a4760;
    --accent:#60a5fa; --accent2:#a78bfa; --accentlt:#1e2d4a; --purple-lt:#1e1a38;
    --green:#34d399; --green-lt:#0d2218; --green-border:#065f46;
    --orange:#fb923c; --orange-lt:#1f1208; --orange-border:#92400e;
    --red:#f87171; --text:#e2e8f0; --text2:#94a3b8; --text3:#64748b;
    --law-name:#93c5fd; --law-bg:linear-gradient(135deg,#1e2d4a,#1e1a38);
    --law-border:#2e4070; --val-bg:#1c2330;
    --shadow:0 2px 14px rgba(0,0,0,0.35); --shadow-md:0 4px 22px rgba(0,0,0,0.45);
    --progress-bg:#1c2330; --input-bg:#161c24;
    --stat-num-laws:#60a5fa; --stat-num-rows:#94a3b8; --stat-num-pct:#a78bfa;
    --stat-num-ok:#34d399; --stat-num-edit:#fb923c;
}}
[data-theme="dark"] {
    --bg:#0f1318; --bg2:#161c24; --bg3:#1c2330; --card:#1a2030;
    --border:#2a3448; --border2:#3a4760;
    --accent:#60a5fa; --accent2:#a78bfa; --accentlt:#1e2d4a; --purple-lt:#1e1a38;
    --green:#34d399; --green-lt:#0d2218; --green-border:#065f46;
    --orange:#fb923c; --orange-lt:#1f1208; --orange-border:#92400e;
    --red:#f87171; --text:#e2e8f0; --text2:#94a3b8; --text3:#64748b;
    --law-name:#93c5fd; --law-bg:linear-gradient(135deg,#1e2d4a,#1e1a38);
    --law-border:#2e4070; --val-bg:#1c2330;
    --shadow:0 2px 14px rgba(0,0,0,0.35); --shadow-md:0 4px 22px rgba(0,0,0,0.45);
    --progress-bg:#1c2330; --input-bg:#161c24;
    --stat-num-laws:#60a5fa; --stat-num-rows:#94a3b8; --stat-num-pct:#a78bfa;
    --stat-num-ok:#34d399; --stat-num-edit:#fb923c;
}

html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif !important;
    direction: rtl;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem 2rem !important; max-width: 1300px !important; }

.hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 55%, #4f46e5 100%);
    border-radius: 20px; padding: 2.2rem 3rem; margin-bottom: 1.8rem;
    text-align: center; position: relative; overflow: hidden;
    box-shadow: var(--shadow-md);
}
.hero::before {
    content:''; position:absolute; inset:0;
    background: radial-gradient(ellipse at 20% 50%,rgba(255,255,255,0.10) 0%,transparent 55%),
                radial-gradient(ellipse at 80% 50%,rgba(255,255,255,0.07) 0%,transparent 55%);
    pointer-events:none;
}
.hero h1 { font-family:'Amiri',serif; font-size:2.4rem; font-weight:700; color:#fff; margin:0 0 0.3rem 0; text-shadow:0 2px 12px rgba(0,0,0,0.25); }
.hero p  { color:rgba(255,255,255,0.78); font-size:1rem; margin:0; }

.stat-card { background:var(--card); border:1px solid var(--border); border-radius:var(--radius); padding:1rem 1.2rem; text-align:center; box-shadow:var(--shadow); transition:border-color 0.2s; }
.stat-card:hover { border-color:var(--accent); }
.stat-num { font-size:1.9rem; font-weight:800; line-height:1.1; }
.stat-lbl { font-size:0.78rem; color:var(--text2); margin-top:3px; }

.progress-wrap { background:var(--card); border:1px solid var(--border); border-radius:var(--radius); padding:1rem 1.5rem; margin-bottom:1.2rem; box-shadow:var(--shadow); }
.prog-label { font-weight:700; font-size:0.9rem; color:var(--text); }
.prog-meta  { font-size:0.82rem; color:var(--text2); }
.progress-bar-outer { background:var(--progress-bg); border-radius:99px; height:8px; overflow:hidden; margin-top:8px; }
.progress-bar-inner { height:100%; border-radius:99px; background:linear-gradient(90deg,var(--accent),var(--accent2)); transition:width 0.6s ease; }

.law-card { background:var(--law-bg); border:1px solid var(--law-border); border-right:4px solid var(--accent); border-radius:var(--radius); padding:1.2rem 1.5rem; margin-bottom:1rem; box-shadow:var(--shadow); }
.law-name { font-family:'Amiri',serif; font-size:1.25rem; font-weight:700; color:var(--law-name); line-height:1.7; }
.law-meta { font-size:0.82rem; color:var(--text2); margin-top:5px; }

.val-box { background:var(--val-bg); border:1px solid var(--border); border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:0.7rem; }
.val-box-lbl { font-size:0.68rem; font-weight:700; color:var(--text3); margin-bottom:4px; text-transform:uppercase; letter-spacing:0.7px; }
.val-box-val { font-size:1.05rem; font-weight:700; color:var(--text); }

.badge { display:inline-block; padding:3px 13px; border-radius:20px; font-size:0.78rem; font-weight:700; }
.badge-new    { background:var(--bg3);       color:var(--text3);   border:1px solid var(--border2); }
.badge-ok     { background:var(--green-lt);  color:var(--green);   border:1px solid var(--green-border); }
.badge-edited { background:var(--orange-lt); color:var(--orange);  border:1px solid var(--orange-border); }

.done-banner { background:linear-gradient(135deg,var(--green-lt),var(--accentlt)); border:1px solid var(--green-border); border-radius:var(--radius); padding:1.8rem; text-align:center; margin:0.8rem 0; }
.done-banner h2 { color:var(--green); font-family:'Amiri',serif; font-size:2rem; margin:0 0 0.4rem 0; }
.done-banner p  { color:var(--text2); margin:0; }

.upload-hint { background:var(--card); border:2px dashed var(--border2); border-radius:var(--radius); padding:2.5rem; text-align:center; color:var(--text2); margin-top:1rem; }
.section-lbl { font-size:0.75rem; font-weight:700; color:var(--text3); text-transform:uppercase; letter-spacing:0.8px; margin-bottom:5px; }
.row-meta { font-size:0.82rem; color:var(--text3); margin:0.4rem 0 0.8rem 0; }
.login-card { background:var(--card); border:1px solid var(--border); border-radius:var(--radius); padding:2rem; box-shadow:var(--shadow-md); }

.sync-badge { display:inline-flex; align-items:center; gap:6px; font-size:0.78rem; padding:3px 10px; border-radius:20px; }
.sync-ok    { background:var(--green-lt);  color:var(--green);  border:1px solid var(--green-border); }
.sync-fail  { background:var(--orange-lt); color:var(--orange); border:1px solid var(--orange-border); }

.stButton > button { font-family:'Tajawal',sans-serif !important; font-weight:700 !important; border-radius:10px !important; padding:0.55rem 1.4rem !important; font-size:0.95rem !important; transition:all 0.2s !important; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    font-family:'Tajawal',sans-serif !important; background:var(--input-bg) !important;
    border:1.5px solid var(--border) !important; color:var(--text) !important;
    border-radius:8px !important; direction:rtl !important; font-size:0.97rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color:var(--accent) !important; box-shadow:0 0 0 3px rgba(96,165,250,0.15) !important;
}
.stSelectbox > div > div { background:var(--input-bg) !important; border:1.5px solid var(--border) !important; color:var(--text) !important; border-radius:8px !important; direction:rtl !important; }
.stTextInput label,.stTextArea label,.stSelectbox label { color:var(--text2) !important; font-family:'Tajawal',sans-serif !important; font-size:0.87rem !important; font-weight:600 !important; }
hr { border-color:var(--border) !important; margin:1.2rem 0 !important; }
.stAlert { border-radius:var(--radius) !important; font-family:'Tajawal',sans-serif !important; }
</style>
""", unsafe_allow_html=True)


# ─── Imports (after CSS so login page looks good) ──────────────────────────────
from auth  import require_login, logout
from admin import admin_panel
from sheets import (
    save_single_row, save_user_data,
    load_user_data, rebuild_groups_from_sheet,
    log_change,
)

# ─── Session State Defaults ────────────────────────────────────────────────────
for k, v in [("logged_in", False), ("username", ""), ("role", ""),
             ("groups", None), ("original_df", None),
             ("cur_law", 0), ("cur_row", 0),
             ("file_ext", ".csv"), ("file_name", "audit_output"),
             ("last_sync", None), ("sync_ok", True)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Auth Gate ─────────────────────────────────────────────────────────────────
require_login()

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown(f"الصلاحية: {'🛡️ Admin' if st.session_state.role == 'admin' else '👤 مراجع'}")
    st.markdown("---")
    if st.session_state.get("last_sync"):
        sync_time = st.session_state.last_sync
        badge_cls = "sync-ok" if st.session_state.sync_ok else "sync-fail"
        badge_txt = f"✅ تمت المزامنة {sync_time}" if st.session_state.sync_ok else "⚠️ فشلت المزامنة"
        st.markdown(f'<span class="sync-badge {badge_cls}">{badge_txt}</span>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        logout()

# ─── Admin Panel ───────────────────────────────────────────────────────────────
if st.session_state.role == "admin":
    admin_panel()
    st.stop()

# ─── AUDITOR VIEW ──────────────────────────────────────────────────────────────

# ── Hero ──
st.markdown("""
<div class="hero">
  <div style="font-size:2.8rem;margin-bottom:0.4rem">⚖️</div>
  <h1>منظومة مراجعة التشريعات</h1>
  <p>مراجعة وتدقيق الجهات والأنواع المرتبطة بالقوانين والأنظمة</p>
</div>
""", unsafe_allow_html=True)


# ─── Helpers ───────────────────────────────────────────────────────────────────
def load_file(uploaded_file):
    ext = Path(uploaded_file.name).suffix.lower()
    df  = pd.read_csv(uploaded_file, encoding="utf-8-sig") if ext == ".csv" else pd.read_excel(uploaded_file)
    return df, ext


def init_groups(df) -> list:
    records = []
    for idx, row in df.iterrows():
        records.append({
            "orig_idx":       idx,
            "leg_name":       str(row.get("leg_name", "")),
            "entity_final":   str(row.get("entity_final", "")),
            "type":           str(row.get("type", "")),
            "entity_audited": str(row.get("entity_final", "")),
            "type_audited":   str(row.get("type", "")),
            "audit_status":   "لم يُراجع",
            "audit_notes":    "",
        })
    seen, groups = {}, []
    for r in records:
        n = r["leg_name"]
        if n not in seen:
            seen[n] = len(groups)
            groups.append({"leg_name": n, "rows": []})
        groups[seen[n]]["rows"].append(r)
    return groups


def export_df(original_df, groups, ext):
    df_out = original_df.copy()
    df_out["entity_audited"] = df_out["entity_final"].astype(str)
    df_out["type_audited"]   = df_out["type"].astype(str)
    df_out["audit_status"]   = "لم يُراجع"
    df_out["audit_notes"]    = ""
    for g in groups:
        for r in g["rows"]:
            i = r["orig_idx"]
            df_out.at[i, "entity_audited"] = r["entity_audited"]
            df_out.at[i, "type_audited"]   = r["type_audited"]
            df_out.at[i, "audit_status"]   = r["audit_status"]
            df_out.at[i, "audit_notes"]    = r["audit_notes"]
    buf = io.BytesIO()
    if ext == ".csv":
        df_out.to_csv(buf, index=False, encoding="utf-8-sig")
        mime = "text/csv"
    else:
        df_out.to_excel(buf, index=False)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    buf.seek(0)
    return buf, mime


def sync_row(row_data: dict, row_id: int, leg_name: str,
             old_entity: str, old_type: str):
    """Save a single row to Google Sheets and log any changes."""
    sp = st.session_state.spreadsheet
    try:
        save_single_row(sp, st.session_state.username, row_id, row_data)
        log_change(sp, st.session_state.username, leg_name,
                   "entity_final", old_entity, row_data["entity_audited"])
        log_change(sp, st.session_state.username, leg_name,
                   "type", old_type, row_data["type_audited"])
        st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
        st.session_state.sync_ok   = True
    except Exception as e:
        st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
        st.session_state.sync_ok   = False


# ─── Try to resume from Google Sheets ─────────────────────────────────────────
if st.session_state.groups is None:
    sp = st.session_state.spreadsheet
    with st.spinner("جارٍ البحث عن بياناتك المحفوظة..."):
        saved = load_user_data(sp, st.session_state.username)
    if saved:
        st.session_state.groups = rebuild_groups_from_sheet(saved)
        st.info("✅ تم استئناف جلستك السابقة من السحابة.")


# ─── Upload Screen ─────────────────────────────────────────────────────────────
if st.session_state.groups is None:
    st.markdown("### 📂 رفع الملف")
    uploaded = st.file_uploader("ملف", type=["csv","xlsx","xls"], label_visibility="collapsed")
    if uploaded:
        try:
            df, ext = load_file(uploaded)
            missing = {"leg_name","entity_final","type"} - set(df.columns)
            if missing:
                st.error(f"❌ الأعمدة التالية غير موجودة: {', '.join(missing)}")
            else:
                st.session_state.original_df = df
                st.session_state.file_ext    = ext
                st.session_state.file_name   = Path(uploaded.name).stem
                groups = init_groups(df)
                st.session_state.groups = groups
                st.session_state.cur_law = 0
                st.session_state.cur_row = 0
                # Initial save to Sheets
                with st.spinner("جارٍ حفظ الملف في السحابة..."):
                    try:
                        sp = st.session_state.spreadsheet
                        save_user_data(sp, st.session_state.username, groups)
                        st.session_state.sync_ok   = True
                        st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
                    except Exception:
                        st.session_state.sync_ok = False
                st.rerun()
        except Exception as e:
            st.error(f"خطأ في قراءة الملف: {e}")
    st.markdown("""
    <div class="upload-hint">
        <div style="font-size:2.5rem;margin-bottom:0.5rem">📄</div>
        <div style="font-size:1rem">اسحب الملف هنا أو انقر للاختيار</div>
        <div style="font-size:0.82rem;color:var(--text3);margin-top:6px">CSV · XLSX · XLS</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── Main Audit View ───────────────────────────────────────────────────────────
groups     = st.session_state.groups
cur_law    = st.session_state.cur_law
cur_row    = st.session_state.cur_row
total_laws = len(groups)
total_rows = sum(len(g["rows"]) for g in groups)
reviewed   = sum(1 for g in groups for r in g["rows"] if r["audit_status"] != "لم يُراجع")
modified   = sum(1 for g in groups for r in g["rows"] if r["audit_status"] == "معدّل")
approved   = sum(1 for g in groups for r in g["rows"] if r["audit_status"] == "معتمد")
laws_done  = sum(1 for g in groups if all(r["audit_status"] != "لم يُراجع" for r in g["rows"]))
pct        = int(reviewed / total_rows * 100) if total_rows else 0

# ── Stats ──
for col, (num, lbl, color) in zip(st.columns(5), [
    (total_laws, "إجمالي القوانين",  "var(--stat-num-laws)"),
    (total_rows, "إجمالي السجلات",   "var(--stat-num-rows)"),
    (f"{pct}%",  "نسبة الإنجاز",     "var(--stat-num-pct)"),
    (approved,   "سجلات معتمدة",     "var(--stat-num-ok)"),
    (modified,   "سجلات معدّلة",     "var(--stat-num-edit)"),
]):
    with col:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-num" style="color:{color}">{num}</div>
            <div class="stat-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:0.9rem'></div>", unsafe_allow_html=True)

# ── Progress ──
st.markdown(f"""
<div class="progress-wrap">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <span class="prog-label">📊 تقدم المراجعة</span>
    <span class="prog-meta">{laws_done}/{total_laws} قانون · {reviewed}/{total_rows} سجل</span>
  </div>
  <div class="progress-bar-outer">
    <div class="progress-bar-inner" style="width:{pct}%"></div>
  </div>
</div>
""", unsafe_allow_html=True)

if reviewed == total_rows and total_rows > 0:
    st.markdown("""<div class="done-banner">
      <h2>🎉 تمت مراجعة جميع السجلات!</h2>
      <p>يمكنك الآن تنزيل الملف المعدّل أدناه</p>
    </div>""", unsafe_allow_html=True)

st.markdown("---")


# ─── Action Helpers ────────────────────────────────────────────────────────────
def save_current(status):
    r = groups[cur_law]["rows"][cur_row]
    entity_val = st.session_state.get(f"entity_{cur_law}_{cur_row}", r["entity_audited"])
    type_val   = st.session_state.get(f"type_{cur_law}_{cur_row}",   r["type_audited"])
    ct         = st.session_state.get(f"custom_type_{cur_law}_{cur_row}", "").strip()
    notes_val  = st.session_state.get(f"notes_{cur_law}_{cur_row}",  r["audit_notes"])
    if ct:
        type_val = ct
    if status == "auto":
        changed = entity_val != r["entity_final"] or type_val != r["type"]
        status  = "معدّل" if changed else "معتمد"

    old_entity = r["entity_audited"]
    old_type   = r["type_audited"]

    groups[cur_law]["rows"][cur_row].update({
        "entity_audited": entity_val,
        "type_audited":   type_val,
        "audit_status":   status,
        "audit_notes":    notes_val,
    })
    st.session_state.groups = groups

    # Sync to Google Sheets
    row_id = r["orig_idx"]
    sync_row(
        row_data=groups[cur_law]["rows"][cur_row],
        row_id=row_id,
        leg_name=r["leg_name"],
        old_entity=old_entity,
        old_type=old_type,
    )


def go_next():
    rows_n = len(groups[st.session_state.cur_law]["rows"])
    if st.session_state.cur_row < rows_n - 1:
        st.session_state.cur_row += 1
    elif st.session_state.cur_law < total_laws - 1:
        st.session_state.cur_law += 1
        st.session_state.cur_row  = 0

def go_prev():
    if st.session_state.cur_row > 0:
        st.session_state.cur_row -= 1
    elif st.session_state.cur_law > 0:
        st.session_state.cur_law -= 1
        st.session_state.cur_row = len(groups[st.session_state.cur_law]["rows"]) - 1


# ─── Law Selector ──────────────────────────────────────────────────────────────
def law_label(i, g):
    done     = all(r["audit_status"] != "لم يُراجع" for r in g["rows"])
    has_edit = any(r["audit_status"] == "معدّل"      for r in g["rows"])
    icon = "✅" if (done and not has_edit) else ("✏️" if has_edit else "○")
    short = g["leg_name"][:65] + ("..." if len(g["leg_name"]) > 65 else "")
    return f"{icon}  {short}"

law_options = [law_label(i, g) for i, g in enumerate(groups)]

st.markdown('<div class="section-lbl">اختر القانون أو النظام</div>', unsafe_allow_html=True)
selected = st.selectbox("القانون", options=law_options, index=cur_law,
                        label_visibility="collapsed", key="law_selector")
new_idx = law_options.index(selected)
if new_idx != cur_law:
    save_current("auto")
    st.session_state.cur_law = new_idx
    st.session_state.cur_row = 0
    st.rerun()

cur_law = st.session_state.cur_law
cur_row = st.session_state.cur_row
group   = groups[cur_law]
rows    = group["rows"]
if cur_row >= len(rows):
    cur_row = 0
    st.session_state.cur_row = 0

# ── Law Header ──
lsc  = {"لم يُراجع": 0, "معتمد": 0, "معدّل": 0}
for r in rows: lsc[r["audit_status"]] += 1
lpct = int((lsc["معتمد"] + lsc["معدّل"]) / len(rows) * 100) if rows else 0

st.markdown(f"""
<div class="law-card">
  <div class="law-name">📜 {group["leg_name"]}</div>
  <div class="law-meta">
    {len(rows)} سجل &nbsp;·&nbsp;
    <span style="color:var(--green);font-weight:700">{lsc["معتمد"]} معتمد</span> &nbsp;·&nbsp;
    <span style="color:var(--orange);font-weight:700">{lsc["معدّل"]} معدّل</span> &nbsp;·&nbsp;
    <span style="color:var(--text3)">{lsc["لم يُراجع"]} لم يُراجع</span>
    &nbsp;·&nbsp; {lpct}% مكتمل
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f'<div class="row-meta">السجل {cur_row + 1} من {len(rows)}</div>',
            unsafe_allow_html=True)

# ─── Current Row ───────────────────────────────────────────────────────────────
row     = rows[cur_row]
bmap    = {"لم يُراجع": "badge-new", "معتمد": "badge-ok", "معدّل": "badge-edited"}
badge_c = bmap.get(row["audit_status"], "badge-new")

st.markdown(f'<span class="badge {badge_c}">{row["audit_status"]}</span>', unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:0.5rem'></div>", unsafe_allow_html=True)

c_entity, c_type = st.columns(2)

with c_entity:
    st.markdown(f"""<div class="val-box">
      <div class="val-box-lbl">الجهة المنطبق عليها القانون أو النظام</div>
      <div class="val-box-val">{row["entity_final"]}</div>
    </div>""", unsafe_allow_html=True)
    st.text_input("✏️ تعديل الجهة", value=row["entity_audited"],
                  key=f"entity_{cur_law}_{cur_row}", placeholder="اكتب اسم الجهة...")

with c_type:
    st.markdown(f"""<div class="val-box">
      <div class="val-box-lbl">نوع هذه الجهة</div>
      <div class="val-box-val">{row["type"]}</div>
    </div>""", unsafe_allow_html=True)
    all_types    = sorted(set(r["type_audited"] for g in groups for r in g["rows"] if r["type_audited"]))
    type_options = list(dict.fromkeys([row["type_audited"]] + all_types))
    st.selectbox("✏️ تعديل نوع الجهة", options=type_options,
                 index=type_options.index(row["type_audited"]) if row["type_audited"] in type_options else 0,
                 key=f"type_{cur_law}_{cur_row}")
    st.text_input("أو أدخل نوعاً جديداً", value="",
                  key=f"custom_type_{cur_law}_{cur_row}", placeholder="نوع مختلف...")

st.text_area("💬 ملاحظات (اختياري)", value=row["audit_notes"],
             key=f"notes_{cur_law}_{cur_row}",
             placeholder="أضف ملاحظة على هذا السجل...", height=75)

st.markdown("<div style='margin-top:0.3rem'></div>", unsafe_allow_html=True)

# ── Buttons ──
col_prev, col_approve, col_save, col_next = st.columns([2, 3, 3, 2])
with col_prev:
    if st.button("◀ السابق", use_container_width=True):
        save_current("auto"); go_prev(); st.rerun()
with col_approve:
    if st.button("✅ اعتماد والتالي", use_container_width=True, type="primary"):
        save_current("معتمد"); go_next(); st.rerun()
with col_save:
    if st.button("💾 حفظ التعديل والتالي", use_container_width=True):
        save_current("معدّل"); go_next(); st.rerun()
with col_next:
    if st.button("التالي ▶", use_container_width=True):
        save_current("auto"); go_next(); st.rerun()

# ─── Download ──────────────────────────────────────────────────────────────────
st.markdown("---")
dl1, dl2 = st.columns([3, 1])
with dl1:
    if st.session_state.original_df is not None:
        buf, mime = export_df(st.session_state.original_df, groups, st.session_state.file_ext)
        st.download_button(
            label="⬇️ تنزيل الملف المعدّل",
            data=buf,
            file_name=f"{st.session_state.file_name}_مراجعة{st.session_state.file_ext}",
            mime=mime,
            use_container_width=True,
            type="primary",
        )
    else:
        # Rebuild downloadable file from groups only
        rows_flat = [r for g in groups for r in g["rows"]]
        df_dl = pd.DataFrame([{
            "leg_name":       r["leg_name"],
            "entity_final":   r["entity_final"],
            "type":           r["type"],
            "entity_audited": r["entity_audited"],
            "type_audited":   r["type_audited"],
            "audit_status":   r["audit_status"],
            "audit_notes":    r["audit_notes"],
        } for r in rows_flat])
        buf = io.BytesIO()
        df_dl.to_excel(buf, index=False)
        buf.seek(0)
        st.download_button(
            label="⬇️ تنزيل الملف المعدّل",
            data=buf,
            file_name=f"مراجعة_{st.session_state.username}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )
with dl2:
    if st.button("🔄 رفع ملف جديد", use_container_width=True):
        for k in ["groups","original_df","cur_law","cur_row","file_ext","file_name"]:
            st.session_state.pop(k, None)
        st.rerun()
