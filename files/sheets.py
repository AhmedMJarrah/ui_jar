"""
sheets.py — Google Sheets backend (v2)
Two master sheets:
  - master_data     : old work (untouched)
  - master_data_v2  : new classification work
"""
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import bcrypt
import time
import pandas as pd

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_ID   = "1svY3lp6RUTp4K-bigbx2JDAeh8RNLACsuXCYqxP4QgQ"
SHEET_USERS      = "users"
SHEET_MASTER     = "master_data"
SHEET_MASTER_V2  = "master_data_v2"
SHEET_AUDIT_LOG  = "audit_log"
SHEET_ENTITIES   = "entities"

MASTER_V2_HEADERS = [
    "row_id", "year", "magazine_number", "leg_name", "leg_number", "status",
    "scope", "entity_audited", "type_audited",
    "custom_entity", "custom_type",
    "audit_status", "audit_notes", "assigned_to", "last_updated",
]

USERS_HEADERS = [
    "username", "password_hash", "role",
    "created_at", "last_active", "assigned_half"
]


# ─── CONNECTION ────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def get_client():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=SCOPES
    )
    return gspread.authorize(creds)


@st.cache_resource(show_spinner=False)
def get_spreadsheet():
    return get_client().open_by_key(SPREADSHEET_ID)


def ensure_sheet(spreadsheet, name: str, headers: list):
    try:
        return spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=3000, cols=len(headers))
        ws.append_row(headers)
        return ws


def safe_call(fn, retries=4, wait=6):
    for attempt in range(retries):
        try:
            return fn()
        except gspread.exceptions.APIError as e:
            if "429" in str(e) and attempt < retries - 1:
                time.sleep(wait * (attempt + 1))
            else:
                raise


# ─── USERS ─────────────────────────────────────────────────────────────────────

def get_users_sheet(spreadsheet):
    return ensure_sheet(spreadsheet, SHEET_USERS, USERS_HEADERS)


@st.cache_data(ttl=30, show_spinner=False)
def load_users_cached(_sid: str) -> dict:
    sp      = get_spreadsheet()
    ws      = get_users_sheet(sp)
    records = safe_call(ws.get_all_records)
    return {r["username"]: r for r in records}


def load_users(spreadsheet=None) -> dict:
    return load_users_cached(SPREADSHEET_ID)


def invalidate_users():
    load_users_cached.clear()


def create_user(spreadsheet, username: str, password: str,
                role: str = "auditor", assigned_half: str = ""):
    users = load_users()
    if username in users:
        return False, "اسم المستخدم موجود مسبقاً"
    if role == "auditor" and not assigned_half:
        taken = [str(u.get("assigned_half","")).strip() for u in users.values() if u["role"]=="auditor"]
        for h in ["1","2","3","4","5","6","7","8"]:
            if h not in taken:
                assigned_half = h
                break
        if not assigned_half:
            return False, "لا توجد نصف متاح"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    ws = get_users_sheet(spreadsheet)
    safe_call(lambda: ws.append_row([
        username, hashed, role,
        datetime.now().isoformat(), "", assigned_half
    ]))
    invalidate_users()
    return True, f"تم إنشاء المستخدم — النصف: {assigned_half}"


def delete_user(spreadsheet, username: str):
    ws      = get_users_sheet(spreadsheet)
    records = safe_call(ws.get_all_values)
    for i, row in enumerate(records):
        if row and row[0] == username:
            safe_call(lambda idx=i: ws.delete_rows(idx + 1))
            invalidate_users()
            return True
    return False


def verify_password(spreadsheet, username: str, password: str):
    users = load_users()
    if username not in users:
        return False, None
    u = users[username]
    if bcrypt.checkpw(password.encode(), u["password_hash"].encode()):
        try:
            ws   = get_users_sheet(spreadsheet)
            cell = safe_call(lambda: ws.find(username))
            safe_call(lambda: ws.update_cell(cell.row, 5, datetime.now().isoformat()))
            invalidate_users()
        except Exception:
            pass
        return True, u
    return False, None


def update_password(spreadsheet, username: str, new_password: str):
    ws     = get_users_sheet(spreadsheet)
    cell   = safe_call(lambda: ws.find(username))
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    safe_call(lambda: ws.update_cell(cell.row, 2, hashed))
    invalidate_users()


# ─── ENTITIES ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_entities_cached(_sid: str) -> list:
    sp = get_spreadsheet()
    try:
        ws      = sp.worksheet(SHEET_ENTITIES)
        records = safe_call(ws.get_all_records)
        return records  # [{"الاسم": ..., "النوع": ...}]
    except Exception:
        return []


def load_entities() -> list:
    return load_entities_cached(SPREADSHEET_ID)


def save_entities_sheet(spreadsheet, df_entities: pd.DataFrame):
    """Save entities list to Google Sheets."""
    ws = ensure_sheet(spreadsheet, SHEET_ENTITIES, ["الاسم", "النوع"])
    safe_call(ws.clear)
    rows = [["الاسم", "النوع"]] + df_entities.values.tolist()
    safe_call(lambda: ws.update(rows))
    load_entities_cached.clear()


def add_custom_entity(spreadsheet, name: str, etype: str):
    """Add a new entity to the entities sheet."""
    if not name.strip():
        return
    ws = ensure_sheet(spreadsheet, SHEET_ENTITIES, ["الاسم", "النوع"])
    safe_call(lambda: ws.append_row([name.strip(), etype.strip()]))
    load_entities_cached.clear()


# ─── MASTER V2 ─────────────────────────────────────────────────────────────────

def upload_master_v2(spreadsheet, df: pd.DataFrame, df_entities: pd.DataFrame):
    """
    Upload new classification file as master_data_v2.
    Split 977 unique laws equally between 5 users.
    Also saves entities to entities sheet.
    """
    def clean(val):
        import math
        if val is None: return ""
        if isinstance(val, float) and math.isnan(val): return ""
        return str(val)

    # Save entities first
    save_entities_sheet(spreadsheet, df_entities)

    ws = ensure_sheet(spreadsheet, SHEET_MASTER_V2, MASTER_V2_HEADERS)
    safe_call(ws.clear)

    unique_laws = df["leg_name"].dropna().unique().tolist()
    total       = len(unique_laws)
    each        = total // 5
    splits      = [0, each, each*2, each*3, each*4, total]

    rows = [MASTER_V2_HEADERS]
    row_id = 0
    for half_idx, (start, end) in enumerate(zip(splits, splits[1:])):
        half = str(half_idx + 1)
        for law in unique_laws[start:end]:
            law_rows = df[df["leg_name"] == law]
            for _, r in law_rows.iterrows():
                rows.append([
                    row_id,
                    clean(r.get("year", "")),
                    clean(r.get("magazine_number", "")),
                    clean(r.get("leg_name", "")),
                    clean(r.get("leg_number", "")),
                    clean(r.get("status", "")),
                    "",   # scope
                    "",   # entity_audited
                    "",   # type_audited
                    "",   # custom_entity
                    "",   # custom_type
                    "لم يُراجع",
                    "",
                    half,
                    "",
                ])
                row_id += 1

    # Write in chunks
    chunk = 200
    for i in range(0, len(rows), chunk):
        safe_call(lambda s=i: ws.append_rows(rows[s:s+chunk]))

    invalidate_master_v2()
    return row_id


@st.cache_data(ttl=60, show_spinner=False)
def load_master_v2_cached(_sid: str):
    sp  = get_spreadsheet()
    ws  = ensure_sheet(sp, SHEET_MASTER_V2, MASTER_V2_HEADERS)
    return safe_call(ws.get_all_records)


def load_master_v2():
    return load_master_v2_cached(SPREADSHEET_ID)


def invalidate_master_v2():
    load_master_v2_cached.clear()


def load_user_rows_v2(assigned_half: str) -> list:
    records = load_master_v2()
    half    = str(assigned_half).strip()
    return [r for r in records if str(r.get("assigned_to","")).strip() == half]


def save_audited_row_v2(spreadsheet, row_id: int,
                         scope: str, entity_audited: str, type_audited: str,
                         custom_entity: str, custom_type: str,
                         audit_status: str, audit_notes: str):
    ws      = ensure_sheet(spreadsheet, SHEET_MASTER_V2, MASTER_V2_HEADERS)
    records = safe_call(ws.get_all_values)
    for i, rec in enumerate(records):
        if i == 0: continue
        if str(rec[0]) == str(row_id):
            row_num = i + 1
            safe_call(lambda r=row_num: ws.update(
                f"G{r}:O{r}",
                [[scope, entity_audited, type_audited,
                  custom_entity, custom_type,
                  audit_status, audit_notes, rec[13],
                  datetime.now().isoformat()]]
            ))
            invalidate_master_v2()
            return


# ─── ADMIN PROGRESS V2 ─────────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def get_progress_v2_cached(_sid: str) -> list:
    users   = load_users()
    records = load_master_v2()
    result  = []
    for username, info in users.items():
        if info["role"] == "admin":
            continue
        half     = str(info.get("assigned_half","")).strip()
        my_rows  = [r for r in records if str(r.get("assigned_to","")).strip() == half]
        total    = len(my_rows)
        reviewed = sum(1 for r in my_rows if r.get("audit_status") != "لم يُراجع")
        jamea    = sum(1 for r in my_rows if r.get("scope") == "جميع الجهات")
        moayyan  = sum(1 for r in my_rows if r.get("scope") == "جهة معينة")
        pct      = int(reviewed / total * 100) if total else 0
        result.append({
            "username":     username,
            "half":         half,
            "total":        total,
            "reviewed":     reviewed,
            "jamea":        jamea,
            "moayyan":      moayyan,
            "pct":          pct,
            "last_active":  info.get("last_active", ""),
        })
    return result


def get_progress_v2():
    return get_progress_v2_cached(SPREADSHEET_ID)


def get_master_v2_df() -> pd.DataFrame:
    return pd.DataFrame(load_master_v2())


# ─── OLD MASTER (read-only) ─────────────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def load_master_cached(_sid: str):
    sp = get_spreadsheet()
    try:
        ws = sp.worksheet(SHEET_MASTER)
        return safe_call(ws.get_all_records)
    except Exception:
        return []


def load_master():
    return load_master_cached(SPREADSHEET_ID)


def invalidate_master():
    load_master_cached.clear()


def load_user_rows(username: str, assigned_half: str) -> list:
    records = load_master()
    half    = str(assigned_half).strip()
    return [r for r in records if str(r.get("assigned_to","")).strip() == half]


def save_audited_row(spreadsheet, row_id: int, username: str,
                     entity_audited: str, type_audited: str,
                     audit_status: str, audit_notes: str):
    ws      = ensure_sheet(spreadsheet, SHEET_MASTER, [])
    records = safe_call(ws.get_all_values)
    for i, rec in enumerate(records):
        if i == 0: continue
        if str(rec[0]) == str(row_id):
            row_num = i + 1
            safe_call(lambda r=row_num: ws.update(
                f"I{r}:N{r}",
                [[entity_audited, type_audited, audit_status,
                  audit_notes, str(rec[12]), datetime.now().isoformat()]]
            ))
            invalidate_master()
            return


def get_all_users_progress(spreadsheet=None) -> list:
    users   = load_users()
    records = load_master()
    result  = []
    for username, info in users.items():
        if info["role"] == "admin": continue
        half     = str(info.get("assigned_half","")).strip()
        my_rows  = [r for r in records if str(r.get("assigned_to","")).strip() == half]
        total    = len(my_rows)
        reviewed = sum(1 for r in my_rows if r.get("audit_status") != "لم يُراجع")
        modified = sum(1 for r in my_rows if r.get("audit_status") == "معدّل")
        pct      = int(reviewed / total * 100) if total else 0
        result.append({
            "username": username, "assigned_half": half,
            "total": total, "reviewed": reviewed,
            "modified": modified, "pct": pct,
            "last_active": info.get("last_active",""),
        })
    return result


def log_change(spreadsheet, username, leg_name, field, old_val, new_val):
    if old_val == new_val: return
    try:
        ws = ensure_sheet(spreadsheet, SHEET_AUDIT_LOG,
                          ["timestamp","username","leg_name","field","old_value","new_value"])
        safe_call(lambda: ws.append_row([
            datetime.now().isoformat(), username, leg_name, field, old_val, new_val
        ]))
    except Exception:
        pass
