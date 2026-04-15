import streamlit as st
import pandas as pd
import io
from pathlib import Path

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="مراجع التشريعات",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS — Light Theme ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&family=Amiri:wght@400;700&display=swap');

:root {
    --bg:        #f4f6fb;
    --bg2:       #ffffff;
    --bg3:       #eef1f8;
    --card:      #ffffff;
    --border:    #d4daea;
    --border2:   #b8c2d8;
    --accent:    #2563eb;
    --accent2:   #7c3aed;
    --accentlt:  #eff4ff;
    --green:     #16a34a;
    --greenlt:   #f0fdf4;
    --orange:    #ea6c00;
    --orangelt:  #fff7ed;
    --gray:      #64748b;
    --text:      #1e293b;
    --text2:     #475569;
    --text3:     #94a3b8;
    --radius:    14px;
    --shadow:    0 2px 16px rgba(30,41,59,0.08);
    --shadowmd:  0 4px 24px rgba(30,41,59,0.12);
}

html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif !important;
    direction: rtl;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem 2rem !important; max-width: 1300px !important; }

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 55%, #4f46e5 100%);
    border-radius: 20px;
    padding: 2.2rem 3rem;
    margin-bottom: 1.8rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadowmd);
}
.hero::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 20% 50%, rgba(255,255,255,0.09) 0%, transparent 55%),
                radial-gradient(ellipse at 80% 50%, rgba(255,255,255,0.06) 0%, transparent 55%);
    pointer-events: none;
}
.hero h1 {
    font-family: 'Amiri', serif;
    font-size: 2.4rem; font-weight: 700;
    color: #fff; margin: 0 0 0.3rem 0;
    text-shadow: 0 2px 12px rgba(0,0,0,0.2);
}
.hero p { color: rgba(255,255,255,0.75); font-size: 1rem; margin: 0; }

/* ── Stats ── */
.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    text-align: center;
    box-shadow: var(--shadow);
}
.stat-num { font-size: 1.9rem; font-weight: 800; }
.stat-lbl { font-size: 0.78rem; color: var(--text2); margin-top: 2px; }

/* ── Progress ── */
.progress-wrap {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: var(--shadow);
}
.progress-bar-outer {
    background: var(--bg3);
    border-radius: 99px; height: 8px;
    overflow: hidden; margin-top: 8px;
}
.progress-bar-inner {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    transition: width 0.5s ease;
}

/* ── Law Header Card ── */
.law-card {
    background: linear-gradient(135deg, var(--accentlt), #f5f0ff);
    border: 1px solid #c7d7fb;
    border-right: 4px solid var(--accent);
    border-radius: var(--radius);
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.law-name {
    font-family: 'Amiri', serif;
    font-size: 1.25rem; font-weight: 700;
    color: #1e3a8a; line-height: 1.7;
}
.law-meta { font-size: 0.82rem; color: var(--text2); margin-top: 5px; }

/* ── Value Box ── */
.val-box {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
}
.val-box-lbl {
    font-size: 0.7rem; font-weight: 700;
    color: var(--text3); margin-bottom: 4px;
    text-transform: uppercase; letter-spacing: 0.6px;
}
.val-box-val { font-size: 1.05rem; font-weight: 700; color: var(--text); }

/* ── Badge ── */
.badge {
    display: inline-block;
    padding: 3px 12px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 700;
}
.badge-new    { background: #f1f5f9; color: #64748b; border: 1px solid #cbd5e1; }
.badge-ok     { background: var(--greenlt); color: var(--green); border: 1px solid #bbf7d0; }
.badge-edited { background: var(--orangelt); color: var(--orange); border: 1px solid #fed7aa; }

/* ── Dots ── */
.dot-row { display:flex; gap:7px; flex-wrap:wrap; align-items:center; margin:0.5rem 0 0.9rem 0; }
.dot {
    width:11px; height:11px; border-radius:50%;
    display:inline-block; cursor:default;
}
.dot-new    { background:#cbd5e1; }
.dot-ok     { background:#4ade80; }
.dot-edited { background:#fb923c; }
.dot-active { outline:2.5px solid var(--accent); outline-offset:2px; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'Tajawal', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    font-size: 0.95rem !important;
    transition: all 0.2s !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    font-family: 'Tajawal', sans-serif !important;
    background: #fff !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    direction: rtl !important;
    font-size: 0.97rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #fff !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    direction: rtl !important;
}

/* ── Labels ── */
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: var(--text2) !important;
    font-family: 'Tajawal', sans-serif !important;
    font-size: 0.87rem !important;
    font-weight: 600 !important;
}

hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

.done-banner {
    background: linear-gradient(135deg, var(--greenlt), #eff4ff);
    border: 1px solid #bbf7d0;
    border-radius: var(--radius);
    padding: 1.8rem; text-align: center; margin: 0.8rem 0;
}
.done-banner h2 { color: var(--green); font-family:'Amiri',serif; font-size:2rem; margin:0 0 0.4rem 0; }
.done-banner p  { color: var(--text2); margin: 0; }

.upload-hint {
    background: var(--card);
    border: 2px dashed var(--border2);
    border-radius: var(--radius);
    padding: 2.5rem; text-align: center;
    color: var(--text2); margin-top: 1rem;
}

.section-lbl {
    font-size: 0.78rem; font-weight: 700;
    color: var(--text3); text-transform: uppercase;
    letter-spacing: 0.8px; margin-bottom: 5px;
}

.stAlert { border-radius: var(--radius) !important; font-family:'Tajawal',sans-serif !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ───────────────────────────────────────────────────────────────────
def load_file(uploaded_file):
    ext = Path(uploaded_file.name).suffix.lower()
    df  = pd.read_csv(uploaded_file, encoding="utf-8-sig") if ext == ".csv" else pd.read_excel(uploaded_file)
    return df, ext


def init_audit_state(df):
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


# ─── Session State ─────────────────────────────────────────────────────────────
for k, v in [("groups",None),("cur_law",0),("cur_row",0),
             ("original_df",None),("file_ext",".csv"),("file_name","audit_output")]:
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div style="font-size:2.8rem;margin-bottom:0.4rem">⚖️</div>
  <h1>منظومة مراجعة التشريعات</h1>
  <p>مراجعة وتدقيق الجهات والأنواع المرتبطة بالقوانين والأنظمة</p>
</div>
""", unsafe_allow_html=True)


# ─── Upload Screen ─────────────────────────────────────────────────────────────
if st.session_state.groups is None:
    st.markdown("### 📂 رفع الملف")
    uploaded = st.file_uploader(
        "ملف",
        type=["csv","xlsx","xls"],
        label_visibility="collapsed",
    )
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
                st.session_state.groups      = init_audit_state(df)
                st.session_state.cur_law     = 0
                st.session_state.cur_row     = 0
                st.rerun()
        except Exception as e:
            st.error(f"خطأ في قراءة الملف: {e}")
    st.markdown("""
    <div class="upload-hint">
        <div style="font-size:2.5rem;margin-bottom:0.5rem">📄</div>
        <div style="font-size:1rem">اسحب الملف هنا أو انقر للاختيار</div>
        <div style="font-size:0.82rem;color:#94a3b8;margin-top:6px">CSV · XLSX · XLS</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── Main App ──────────────────────────────────────────────────────────────────
groups    = st.session_state.groups
cur_law   = st.session_state.cur_law
cur_row   = st.session_state.cur_row
total_laws = len(groups)
total_rows = sum(len(g["rows"]) for g in groups)
reviewed   = sum(1 for g in groups for r in g["rows"] if r["audit_status"] != "لم يُراجع")
modified   = sum(1 for g in groups for r in g["rows"] if r["audit_status"] == "معدّل")
approved   = sum(1 for g in groups for r in g["rows"] if r["audit_status"] == "معتمد")
laws_done  = sum(1 for g in groups if all(r["audit_status"] != "لم يُراجع" for r in g["rows"]))
pct        = int(reviewed / total_rows * 100) if total_rows else 0

# ── Stats Bar ──
for col, (num, lbl, color) in zip(
    st.columns(5),
    [(total_laws,"إجمالي القوانين","#2563eb"),
     (total_rows,"إجمالي السجلات","#475569"),
     (f"{pct}%","نسبة الإنجاز","#7c3aed"),
     (approved,  "سجلات معتمدة","#16a34a"),
     (modified,  "سجلات معدّلة","#ea6c00")]
):
    with col:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-num" style="color:{color}">{num}</div>
            <div class="stat-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:0.9rem'></div>", unsafe_allow_html=True)

# ── Progress Bar ──
st.markdown(f"""
<div class="progress-wrap">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <span style="font-weight:700;font-size:0.9rem;color:#1e293b">📊 تقدم المراجعة</span>
    <span style="color:#64748b;font-size:0.82rem">{laws_done}/{total_laws} قانون · {reviewed}/{total_rows} سجل</span>
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


# ─── Helpers ───────────────────────────────────────────────────────────────────
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
    groups[cur_law]["rows"][cur_row].update({
        "entity_audited": entity_val,
        "type_audited":   type_val,
        "audit_status":   status,
        "audit_notes":    notes_val,
    })
    st.session_state.groups = groups

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


# ─── Law Selector Dropdown ─────────────────────────────────────────────────────
def law_label(i, g):
    done     = all(r["audit_status"] != "لم يُراجع" for r in g["rows"])
    has_edit = any(r["audit_status"] == "معدّل"      for r in g["rows"])
    icon = "✅" if (done and not has_edit) else ("✏️" if has_edit else "○")
    short = g["leg_name"][:65] + ("..." if len(g["leg_name"]) > 65 else "")
    return f"{icon}  {short}"

law_options = [law_label(i, g) for i, g in enumerate(groups)]

st.markdown('<div class="section-lbl">اختر القانون أو النظام</div>', unsafe_allow_html=True)
selected = st.selectbox(
    "القانون",
    options=law_options,
    index=cur_law,
    label_visibility="collapsed",
    key="law_selector",
)
new_idx = law_options.index(selected)
if new_idx != cur_law:
    save_current("auto")
    st.session_state.cur_law = new_idx
    st.session_state.cur_row = 0
    st.rerun()

# refresh locals
cur_law = st.session_state.cur_law
cur_row = st.session_state.cur_row
group   = groups[cur_law]
rows    = group["rows"]
if cur_row >= len(rows):
    cur_row = 0
    st.session_state.cur_row = 0

# ── Law Stats Header ──
lsc = {"لم يُراجع":0,"معتمد":0,"معدّل":0}
for r in rows: lsc[r["audit_status"]] += 1
lpct = int((lsc["معتمد"]+lsc["معدّل"])/len(rows)*100) if rows else 0

st.markdown(f"""
<div class="law-card">
  <div class="law-name">📜 {group["leg_name"]}</div>
  <div class="law-meta">
    {len(rows)} سجل &nbsp;·&nbsp;
    <span style="color:#16a34a;font-weight:700">{lsc["معتمد"]} معتمد</span> &nbsp;·&nbsp;
    <span style="color:#ea6c00;font-weight:700">{lsc["معدّل"]} معدّل</span> &nbsp;·&nbsp;
    <span style="color:#94a3b8">{lsc["لم يُراجع"]} لم يُراجع</span>
    &nbsp;·&nbsp; {lpct}% مكتمل
  </div>
</div>
""", unsafe_allow_html=True)

# ── Dots ──
dot_map = {"لم يُراجع":"dot-new","معتمد":"dot-ok","معدّل":"dot-edited"}
dots = "".join(
    f'<span class="dot {dot_map.get(r["audit_status"],"dot-new")} {"dot-active" if j==cur_row else ""}" title="{r["entity_final"][:30]}"></span>'
    for j, r in enumerate(rows)
)
st.markdown(f"""<div class="dot-row">{dots}
  <span style="font-size:0.8rem;color:#94a3b8;margin-right:8px">السجل {cur_row+1} من {len(rows)}</span>
</div>""", unsafe_allow_html=True)

# ─── Current Row Audit ─────────────────────────────────────────────────────────
row = rows[cur_row]
bmap = {"لم يُراجع":"badge-new","معتمد":"badge-ok","معدّل":"badge-edited"}
st.markdown(f'<span class="badge {bmap.get(row["audit_status"],"badge-new")}">{row["audit_status"]}</span>',
            unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:0.5rem'></div>", unsafe_allow_html=True)

c_entity, c_type = st.columns(2)

with c_entity:
    st.markdown(f"""
    <div class="val-box">
      <div class="val-box-lbl">الجهة المنطبق عليها القانون أو النظام</div>
      <div class="val-box-val">{row["entity_final"]}</div>
    </div>""", unsafe_allow_html=True)
    st.text_input(
        "✏️ تعديل الجهة",
        value=row["entity_audited"],
        key=f"entity_{cur_law}_{cur_row}",
        placeholder="اكتب اسم الجهة...",
    )

with c_type:
    st.markdown(f"""
    <div class="val-box">
      <div class="val-box-lbl">نوع هذه الجهة</div>
      <div class="val-box-val">{row["type"]}</div>
    </div>""", unsafe_allow_html=True)
    all_types    = sorted(set(r["type_audited"] for g in groups for r in g["rows"] if r["type_audited"]))
    type_options = list(dict.fromkeys([row["type_audited"]] + all_types))
    st.selectbox(
        "✏️ تعديل نوع الجهة",
        options=type_options,
        index=type_options.index(row["type_audited"]) if row["type_audited"] in type_options else 0,
        key=f"type_{cur_law}_{cur_row}",
    )
    st.text_input(
        "أو أدخل نوعاً جديداً",
        value="",
        key=f"custom_type_{cur_law}_{cur_row}",
        placeholder="نوع مختلف...",
    )

st.text_area(
    "💬 ملاحظات (اختياري)",
    value=row["audit_notes"],
    key=f"notes_{cur_law}_{cur_row}",
    placeholder="أضف ملاحظة على هذا السجل...",
    height=75,
)

st.markdown("<div style='margin-top:0.2rem'></div>", unsafe_allow_html=True)

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
    buf, mime = export_df(st.session_state.original_df, groups, st.session_state.file_ext)
    st.download_button(
        label="⬇️ تنزيل الملف المعدّل",
        data=buf,
        file_name=f"{st.session_state.file_name}_مراجعة{st.session_state.file_ext}",
        mime=mime,
        use_container_width=True,
        type="primary",
    )
with dl2:
    if st.button("🔄 رفع ملف جديد", use_container_width=True):
        for k in ["groups","original_df","cur_law","cur_row","file_ext","file_name"]:
            st.session_state.pop(k, None)
        st.rerun()