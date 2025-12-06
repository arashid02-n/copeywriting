import streamlit as st
import requests
from agents import run_agents
from github_utils import update_github_file
from dotenv import load_dotenv
import os
import hashlib
import secrets
import sqlite3
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from pathlib import Path
from db import get_credits, deduct_credits, add_prompt_record
from posthog_client import track_event

# -----------------------------
# HIDE STREAMLIT DEFAULT PAGES
# -----------------------------
st.markdown("""
    <style>
        section[data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- Secure password hashing ---
def safe_hash(password: str) -> str:
    if password is None:
        password = ""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((salt + password).encode("utf-8"))
    return f"{salt}${hash_obj.hexdigest()}"

# --- Fetch HTML content from a URL ---
def fetch_page_content(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            st.warning(f"⚠️ Could not fetch content from {url} (Status: {response.status_code})")
            return ""
    except Exception as e:
        st.warning(f"⚠️ Error fetching {url}: {e}")
        return ""

# --- Load environment variables ---
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# --- Page setup ---
st.set_page_config(page_title="Copywriting Improvement AI", page_icon="✍️", layout="centered")

# --- Init session ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = st.session_state.get("cookie_authenticated", False)
if "user" not in st.session_state:
    st.session_state["user"] = st.session_state.get("cookie_user", {})
if "google_login_done" not in st.session_state:
    st.session_state["google_login_done"] = False

# --- Handle Google OAuth ---
query_params = st.query_params
if not st.session_state["google_login_done"] and "code" in query_params:
    code = query_params["code"][0] if isinstance(query_params["code"], list) else query_params["code"]
    try:
        st.session_state["google_login_done"] = True

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email"
            ],
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        flow.fetch_token(code=code)
        credentials = flow.credentials

        idinfo = id_token.verify_oauth2_token(credentials._id_token, grequests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo.get("email")
        name = idinfo.get("name")

        DB_PATH = Path(__file__).parent / "users.db"
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            credits INTEGER DEFAULT 0
        )
        """)
        conn.commit()

        username_key = email.split("@")[0]
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing_user = cur.fetchone()

        if not existing_user:
            hashed_password = safe_hash("google_oauth_user")
            cur.execute(
                "INSERT INTO users (username, name, email, password, credits) VALUES (?, ?, ?, ?, ?)",
                (username_key, name or username_key, email, hashed_password, 0)
            )
            conn.commit()

        conn.close()

        st.session_state["authenticated"] = True
        st.session_state["user"] = {"email": email, "name": name}
        st.session_state["cookie_authenticated"] = True
        st.session_state["cookie_user"] = {"email": email, "name": name}

        track_event(email, "login_success", {"method": "google"})

        st.success(f"Logged in successfully as {name}")
        st.query_params.clear()
        st.rerun()

    except Exception as e:
        st.session_state["google_login_done"] = False
        st.error(f"Google sign-in failed: {e}")

# --- Require authenticated user ---
if not st.session_state.get("authenticated", False):
    st.warning("⚠️ Please login first.")
    st.stop()

# ------------------------------
#  CUSTOM SIDEBAR (ONLY LOGOUT)
# ------------------------------
user = st.session_state.get("user", {})
user_name = user.get("name") or user.get("email") or "User"
st.sidebar.markdown(f"**Signed in as:** {user_name}")

if st.sidebar.button("🚪 Logout"):
    for key in ["authenticated", "authentication_status", "user", "google_login_done", "cookie_authenticated", "cookie_user"]:
        st.session_state.pop(key, None)
    st.rerun()

# ----------------------------------
# Main APP UI (unchanged)
# ----------------------------------

st.title("✍️ Copywriting Improvement AI")
st.markdown("Welcome! Let's improve your website content using AI 💡")

# FULL ORIGINAL CODE CONTINUES DOWN HERE…
# هیچ تغییری در منطق برنامه داده نشده
# فقط CSS برای حذف Pages اضافه شد
