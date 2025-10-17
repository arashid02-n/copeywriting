# db.py
# Database helper for SQLite: users, prompts, purchases
# Uses passlib CryptContext to verify legacy bcrypt hashes and to create new pbkdf2_sha256 hashes.

import sqlite3
from pathlib import Path
from datetime import datetime
from passlib.context import CryptContext
from typing import Optional, Dict, Any

# Use pbkdf2_sha256 for new hashes, but accept bcrypt if present in YAML migrated users.
pwd_ctx = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

DB_PATH = Path(__file__).parent / "users.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # users: stores hashed password, credits_balance, created_at, last_login
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
    # prompts: each user prompt and credit used
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
    # purchases: credit purchases
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

# ---------- user helpers ----------
def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        return pwd_ctx.verify(password, stored_hash)
    except Exception:
        return False

def create_user(username: str, name: str, email: str, password: str, credits: float = 100.0) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    pwd_hash = hash_password(password)
    try:
        cur.execute("""
        INSERT INTO users (username, name, email, password_hash, credits_balance, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (username, name, email, pwd_hash, credits, now))
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError as e:
        conn.close()
        raise e
    conn.close()
    return {"id": user_id, "username": username, "email": email, "credits": credits}

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

# ---------- credits & prompts ----------
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

# ---------- migration helper ----------
def import_user_raw(username: str, name: str, email: str, password_hash: str, credits: float = 100.0):
    """
    Insert a user using an existing hash (e.g. bcrypt hash from YAML).
    We store the hash as-is; verify_password() uses passlib's context to verify whichever scheme is present.
    """
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    try:
        cur.execute("""
        INSERT INTO users (username, name, email, password_hash, credits_balance, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (username, name, email, password_hash, credits, now))
        conn.commit()
    except sqlite3.IntegrityError as e:
        # skip duplicates
        pass
    conn.close()
