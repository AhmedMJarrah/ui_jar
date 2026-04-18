"""
sheets.py — Google Sheets backend
Master sheet approach: one source of truth, users update their assigned rows only.
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

SPREADSHEET_ID  = "1svY3lp6RUTp4K-bigbx2JDAeh8RNLACsuXCYqxP4QgQ"
SHEET_USERS     = "users"
SHEET_MASTER    = "master_data"
SHEET_AUDIT_LOG = "audit_log"

MASTER_HEADERS = [
    "row_id", "year", "magazine_number", "leg_name", "leg_number",
    "status", "entity_final", "type",
    "entity_audited", "type_audited", "audit_status", "audit_notes",
    "assigned_to", "last_updated",
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
    """Retry on 429 rate-limit errors."""
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
    return ensure_sheet(
        spreadsheet, SHEET_USERS,
        ["username", "password_hash", "role", "assigned_half",
         "created_at", "last_active"]
    )


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

    # Auto-assign half if auditor and not specified
    if role == "auditor" and not assigned_half:
        auditors = [u for u in users.values() if u["role"] == "auditor"]
        halves_taken = [u.get("assigned_half", "") for u in auditors]
        if "1" not in halves_taken:
            assigned_half = "1"
        elif "2" not in halves_taken:
            assigned_half = "2"
        else:
            return False, "الحد الأقصى للمراجعين هو مستخدمان فقط"

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    ws = get_users_sheet(spreadsheet)
    safe_call(lambda: ws.append_row([
        username, hashed, role, assigned_half,
        datetime.now().isoformat(), ""
    ]))
    invalidate_users()
    return True, f"تم إنشاء المستخدم — النصف المخصص: {assigned_half}"


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
            safe_call(lambda: ws.update_cell(cell.row, 6, datetime.now().isoformat()))
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


# ─── MASTER DATA ───────────────────────────────────────────────────────────────

def upload_master_file(spreadsheet, df: pd.DataFrame):
    """
    Admin uploads file → saved as master_data sheet.
    Laws split 50/50 between user slots 1 and 2.
    """
    # Fix NaN values — replace with empty string
    df = df.fillna("").astype(str)
    df = df.replace("nan", "").replace("NaN", "")

    ws = ensure_sheet(spreadsheet, SHEET_MASTER, MASTER_HEADERS)
    safe_call(ws.clear)

    def clean(val):
        """Convert nan/None to empty string."""
        import math
        if val is None:
            return ""
        if isinstance(val, float) and math.isnan(val):
            return ""
        return str(val)

    unique_laws = df["leg_name"].unique().tolist()
    mid         = len(unique_laws) // 2
    half1_laws  = set(unique_laws[:mid])

    rows = [MASTER_HEADERS]
    for idx, row in df.iterrows():
        half = "1" if row["leg_name"] in half1_laws else "2"
        rows.append([
            idx,
            clean(row.get("year", "")),
            clean(row.get("magazine_number", "")),
            clean(row.get("leg_name", "")),
            clean(row.get("leg_number", "")),
            clean(row.get("status", "")),
            clean(row.get("entity_final", "")),
            clean(row.get("type", "")),
            clean(row.get("entity_final", "")),
            clean(row.get("type", "")),
            "لم يُراجع",
            "",
            half,
            "",
        ])

    # Batch write in chunks to avoid payload limits
    chunk = 200
    for i in range(0, len(rows), chunk):
        safe_call(lambda s=i: ws.append_rows(rows[s:s + chunk]))

    invalidate_master()
    # Also clear entity/type caches
    get_unique_entities_cached.clear()
    get_unique_types_cached.clear()
    return len(rows) - 1  # rows uploaded


@st.cache_data(ttl=60, show_spinner=False)
def load_master_cached(_sid: str):
    sp  = get_spreadsheet()
    ws  = ensure_sheet(sp, SHEET_MASTER, MASTER_HEADERS)
    return safe_call(ws.get_all_records)


def load_master(spreadsheet=None):
    return load_master_cached(SPREADSHEET_ID)


def invalidate_master():
    load_master_cached.clear()


def load_user_rows(username: str, assigned_half: str) -> list:
    """Return only the rows assigned to this user."""
    records = load_master()
    return [r for r in records if str(r.get("assigned_to", "")) == str(assigned_half)]


def save_audited_row(spreadsheet, row_id: int, username: str,
                     entity_audited: str, type_audited: str,
                     audit_status: str, audit_notes: str):
    """Update one row in master_data sheet."""
    ws      = ensure_sheet(spreadsheet, SHEET_MASTER, MASTER_HEADERS)
    records = safe_call(ws.get_all_values)   # includes header

    for i, rec in enumerate(records):
        if i == 0:
            continue  # skip header
        if str(rec[0]) == str(row_id):
            # Columns: entity_audited=9, type_audited=10, audit_status=11,
            #          audit_notes=12, last_updated=14  (1-indexed)
            row_num = i + 1
            safe_call(lambda r=row_num: ws.update(
                f"I{r}:N{r}",
                [[entity_audited, type_audited, audit_status,
                  audit_notes, str(rec[12]), datetime.now().isoformat()]]
            ))
            invalidate_master()
            return


def get_master_df(spreadsheet) -> pd.DataFrame:
    """Return full master as DataFrame for admin download."""
    records = load_master()
    return pd.DataFrame(records)


# ─── UNIQUE ENTITIES & TYPES (for autocomplete) ────────────────────────────────

@st.cache_data(ttl=120, show_spinner=False)
def get_unique_entities_cached(_sid: str) -> list:
    records = load_master()
    entities = sorted(set(
        r["entity_final"] for r in records if r.get("entity_final")
    ))
    return entities


@st.cache_data(ttl=120, show_spinner=False)
def get_unique_types_cached(_sid: str) -> list:
    records = load_master()
    types = sorted(set(
        r["type"] for r in records if r.get("type")
    ))
    return types


def get_unique_entities() -> list:
    return get_unique_entities_cached(SPREADSHEET_ID)


def get_unique_types() -> list:
    return get_unique_types_cached(SPREADSHEET_ID)


# ─── AUDIT LOG ─────────────────────────────────────────────────────────────────

def log_change(spreadsheet, username: str, leg_name: str,
               field: str, old_val: str, new_val: str):
    if old_val == new_val:
        return
    try:
        ws = ensure_sheet(
            spreadsheet, SHEET_AUDIT_LOG,
            ["timestamp", "username", "leg_name", "field", "old_value", "new_value"]
        )
        safe_call(lambda: ws.append_row([
            datetime.now().isoformat(),
            username, leg_name, field, old_val, new_val,
        ]))
    except Exception:
        pass


# ─── ADMIN PROGRESS ────────────────────────────────────────────────────────────

@st.cache_data(ttl=30, show_spinner=False)
def get_all_users_progress_cached(_sid: str) -> list:
    users   = load_users()
    records = load_master()
    result  = []

    for username, info in users.items():
        if info["role"] == "admin":
            continue
        half     = str(info.get("assigned_half", ""))
        my_rows  = [r for r in records if str(r.get("assigned_to", "")) == half]
        total    = len(my_rows)
        reviewed = sum(1 for r in my_rows if r.get("audit_status") != "لم يُراجع")
        modified = sum(1 for r in my_rows if r.get("audit_status") == "معدّل")
        pct      = int(reviewed / total * 100) if total else 0
        result.append({
            "username":     username,
            "assigned_half": half,
            "total":        total,
            "reviewed":     reviewed,
            "modified":     modified,
            "pct":          pct,
            "last_active":  info.get("last_active", ""),
        })
    return result


def get_all_users_progress(spreadsheet=None) -> list:
    return get_all_users_progress_cached(SPREADSHEET_ID)
