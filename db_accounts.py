# db_accounts.py
# SQLite database helper for separate accounts database.
# Handles users, credits, and last login.

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib
import secrets

# --- Path to the new accounts database ---
DB_PATH = Path(__file__).parent / "accounts.db"

# --- Helper to get connection ---
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# --- Initialize database ---
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # --- Create users table ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        name TEXT,
        email TEXT UNIQUE,
        password_hash TEXT,
        credits_balance REAL DEFAULT 100,
        created_at TEXT,
        last_login TEXT
    )
    """)

    conn.commit()
    conn.close()

# --- Password hashing ---
def safe_hash(password: str) -> str:
    if password is None:
        password = ""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((salt + password).encode("utf-8"))
    return f"{salt}${hash_obj.hexdigest()}"

def verify_hash(password: str, stored_hash: str) -> bool:
    try:
        salt, hash_val = stored_hash.split("$")
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest() == hash_val
    except Exception:
        return False

# --- User management ---
def create_user(username: str, name: str, email: str, password: str) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    pwd_hash = safe_hash(password)
    cur.execute("""
        INSERT INTO users (username, name, email, password_hash, credits_balance, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, name, email, pwd_hash, 100.0, now))
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return {"id": user_id, "username": username, "email": email, "credits": 100.0}

def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row

def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return row

def set_last_login(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.utcnow().isoformat(), user_id))
    conn.commit()
    conn.close()
