"""
sheets.py — All Google Sheets read/write operations
"""
import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import bcrypt

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_ID = "1svY3lp6RUTp4K-bigbx2JDAeh8RNLACsuXCYqxP4QgQ"

# Sheet name constants
SHEET_USERS     = "users"
SHEET_AUDIT_LOG = "audit_log"


@st.cache_resource(show_spinner=False)
def get_client():
    """Authenticate and return gspread client. Cached so we don't re-auth every rerun."""
    creds_dict = dict(st.secrets["google_credentials"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet():
    client = get_client()
    return client.open_by_key(SPREADSHEET_ID)


def ensure_sheet(spreadsheet, name: str, headers: list):
    """Get sheet by name, create it with headers if it doesn't exist."""
    try:
        ws = spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=1000, cols=len(headers))
        ws.append_row(headers)
    return ws


# ─── USER MANAGEMENT ───────────────────────────────────────────────────────────

def get_users_sheet(spreadsheet):
    return ensure_sheet(spreadsheet, SHEET_USERS,
                        ["username", "password_hash", "role", "created_at", "last_active"])


def load_users(spreadsheet) -> dict:
    """Returns dict: {username: {password_hash, role, ...}}"""
    ws = get_users_sheet(spreadsheet)
    records = ws.get_all_records()
    return {r["username"]: r for r in records}


def create_user(spreadsheet, username: str, password: str, role: str = "auditor"):
    ws   = get_users_sheet(spreadsheet)
    users = load_users(spreadsheet)
    if username in users:
        return False, "اسم المستخدم موجود مسبقاً"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    ws.append_row([username, hashed, role, datetime.now().isoformat(), ""])
    return True, "تم إنشاء المستخدم بنجاح"


def delete_user(spreadsheet, username: str):
    ws      = get_users_sheet(spreadsheet)
    records = ws.get_all_values()          # [[row], [row], ...]
    for i, row in enumerate(records):
        if row and row[0] == username:
            ws.delete_rows(i + 1)          # gspread is 1-indexed
            # Also delete their data sheet if exists
            try:
                spreadsheet.del_worksheet(spreadsheet.worksheet(f"user_{username}"))
            except Exception:
                pass
            return True
    return False


def verify_password(spreadsheet, username: str, password: str):
    users = load_users(spreadsheet)
    if username not in users:
        return False, None
    u = users[username]
    if bcrypt.checkpw(password.encode(), u["password_hash"].encode()):
        # Update last_active
        try:
            ws = get_users_sheet(spreadsheet)
            cell = ws.find(username)
            ws.update_cell(cell.row, 5, datetime.now().isoformat())
        except Exception:
            pass
        return True, u
    return False, None


def update_password(spreadsheet, username: str, new_password: str):
    ws     = get_users_sheet(spreadsheet)
    cell   = ws.find(username)
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    ws.update_cell(cell.row, 2, hashed)


# ─── USER DATA SHEET ───────────────────────────────────────────────────────────

DATA_HEADERS = [
    "row_id", "leg_name", "entity_final", "type",
    "entity_audited", "type_audited", "audit_status", "audit_notes",
    "last_updated",
]


def get_user_sheet(spreadsheet, username: str):
    return ensure_sheet(spreadsheet, f"user_{username}", DATA_HEADERS)


def save_user_data(spreadsheet, username: str, groups: list):
    """Write all audit rows for this user to their sheet."""
    ws = get_user_sheet(spreadsheet, username)
    rows = [DATA_HEADERS]
    row_id = 0
    for g in groups:
        for r in g["rows"]:
            rows.append([
                row_id,
                r["leg_name"],
                r["entity_final"],
                r["type"],
                r["entity_audited"],
                r["type_audited"],
                r["audit_status"],
                r["audit_notes"],
                datetime.now().isoformat(),
            ])
            row_id += 1
    ws.clear()
    ws.update(rows)


def save_single_row(spreadsheet, username: str, row_id: int, row_data: dict):
    """Update a single row in the user's sheet (faster than full rewrite)."""
    ws      = get_user_sheet(spreadsheet, username)
    records = ws.get_all_values()
    # Find the row with matching row_id (col 1, index 0)
    for i, rec in enumerate(records):
        if rec and str(rec[0]) == str(row_id):
            ws.update(f"A{i+1}:I{i+1}", [[
                row_id,
                row_data["leg_name"],
                row_data["entity_final"],
                row_data["type"],
                row_data["entity_audited"],
                row_data["type_audited"],
                row_data["audit_status"],
                row_data["audit_notes"],
                datetime.now().isoformat(),
            ]])
            return


def load_user_data(spreadsheet, username: str):
    """Load saved audit data for a user. Returns list of dicts or None."""
    try:
        ws      = get_user_sheet(spreadsheet, username)
        records = ws.get_all_records()
        if not records:
            return None
        return records
    except Exception:
        return None


def rebuild_groups_from_sheet(records: list) -> list:
    """Convert flat sheet records back into grouped structure."""
    seen, groups = {}, []
    for i, r in enumerate(records):
        name = r["leg_name"]
        if name not in seen:
            seen[name] = len(groups)
            groups.append({"leg_name": name, "rows": []})
        groups[seen[name]]["rows"].append({
            "orig_idx":       i,
            "leg_name":       r["leg_name"],
            "entity_final":   r["entity_final"],
            "type":           r["type"],
            "entity_audited": r["entity_audited"],
            "type_audited":   r["type_audited"],
            "audit_status":   r["audit_status"],
            "audit_notes":    r["audit_notes"],
        })
    return groups


# ─── AUDIT LOG ─────────────────────────────────────────────────────────────────

def log_change(spreadsheet, username: str, leg_name: str,
               field: str, old_val: str, new_val: str):
    if old_val == new_val:
        return
    ws = ensure_sheet(spreadsheet, SHEET_AUDIT_LOG,
                      ["timestamp", "username", "leg_name", "field", "old_value", "new_value"])
    ws.append_row([
        datetime.now().isoformat(),
        username, leg_name, field, old_val, new_val,
    ])


# ─── ADMIN DASHBOARD DATA ──────────────────────────────────────────────────────

def get_all_users_progress(spreadsheet) -> list:
    """For admin dashboard — returns progress info for each user."""
    users = load_users(spreadsheet)
    result = []
    for username, info in users.items():
        if info["role"] == "admin":
            continue
        try:
            ws      = spreadsheet.worksheet(f"user_{username}")
            records = ws.get_all_records()
            total    = len(records)
            reviewed = sum(1 for r in records if r.get("audit_status") != "لم يُراجع")
            modified = sum(1 for r in records if r.get("audit_status") == "معدّل")
            pct      = int(reviewed / total * 100) if total else 0
        except Exception:
            total = reviewed = modified = pct = 0
        result.append({
            "username":    username,
            "total":       total,
            "reviewed":    reviewed,
            "modified":    modified,
            "pct":         pct,
            "last_active": info.get("last_active", ""),
        })
    return result
