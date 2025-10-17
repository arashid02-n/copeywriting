# db.py
# SQLite database helper for users, credits, prompts and purchases.
# Keeps same structure as YAML version but stores data in persistent database.

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib
import secrets

DB_PATH = Path(__file__).parent / "users.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

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

    # --- Create prompts table ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        prompt_text TEXT,
        credit_used REAL,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # --- Create purchases table ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        credits REAL,
        txn_id TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

# --- Password hashing (same SHA-256 + salt scheme as old YAML) ---
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

# --- Credit management ---
def get_credits(user_id: int) -> float:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT credits_balance FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return float(row["credits_balance"]) if row else 0.0

def deduct_credits(user_id: int, amount: float) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT credits_balance FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False
    balance = float(row["credits_balance"])
    if balance < amount:
        conn.close()
        return False
    new_balance = balance - amount
    cur.execute("UPDATE users SET credits_balance = ? WHERE id = ?", (new_balance, user_id))
    conn.commit()
    conn.close()
    return True

def add_credits(user_id: int, credits: float, txn_id: Optional[str] = None, amount_money: float = 0.0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO purchases (user_id, amount, credits, txn_id, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, amount_money, credits, txn_id, datetime.utcnow().isoformat()))
    cur.execute("UPDATE users SET credits_balance = credits_balance + ? WHERE id = ?", (credits, user_id))
    conn.commit()
    conn.close()

def add_prompt_record(user_id: int, prompt_text: str, credit_used: float = 1.0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO prompts (user_id, prompt_text, credit_used, created_at) VALUES (?, ?, ?, ?)",
                (user_id, prompt_text, credit_used, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
