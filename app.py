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

# --- Secure password hashing (SHA-256 + salt) ---
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

# --- Initialize session & cookies ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = st.session_state.get("cookie_authenticated", False)
if "user" not in st.session_state:
    st.session_state["user"] = st.session_state.get("cookie_user", {})
if "google_login_done" not in st.session_state:
    st.session_state["google_login_done"] = False

# --- Handle Google OAuth redirect ---
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
            st.info(f"👤 New Google user added: {email}")

        conn.close()

        st.session_state["authenticated"] = True
        st.session_state["user"] = {"email": email, "name": name}
        st.session_state["cookie_authenticated"] = True
        st.session_state["cookie_user"] = {"email": email, "name": name}

        st.success(f"✅ Logged in successfully as {name}")
        st.query_params.clear()
        st.rerun()

    except Exception as e:
        st.session_state["google_login_done"] = False
        st.error(f"⚠️ Google sign-in failed: {e}")

# --- Require authentication ---
if not st.session_state.get("authenticated", False):
    st.warning("⚠️ Please login first.")
    st.stop()

# --- Sidebar (User info + Logout) ---
user = st.session_state.get("user", {})
user_name = user.get("name") or user.get("email") or "User"
st.sidebar.markdown(f"**Signed in as:** {user_name}")
if st.sidebar.button("🚪 Logout"):
    for key in ["authenticated", "user", "cookie_authenticated", "cookie_user", "google_login_done"]:
        st.session_state[key] = False if "auth" in key else {}
    st.rerun()

# --- Main Page ---
st.title("✍️ Copywriting Improvement AI")
st.markdown("Welcome! Let's improve your website content using AI 💡")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "funnel_steps" not in st.session_state:
    st.session_state.funnel_steps = []

# --- Form ---
st.markdown("### What is that you want to improve?")
content_options = ["Headline", "Subheadline", "CTA", "Other"]
content_choice = st.selectbox("Choose one:", content_options, key="content_choice")

if content_choice == "Other":
    content_target = st.text_input("Please specify what you want to improve:", placeholder="e.g. Logo, Footer, Sidebar")
else:
    content_target = content_choice

current_version = st.text_area(
    "What is the current version of it?",
    placeholder="Paste or describe the current content here..."
)
offer_definition = st.text_area(
    "Offer Definition (Describe what your business does and what problem it solves):",
    placeholder="Explain your business, product, or service..."
)

# --- New Section: Funnel links ---
st.markdown("### 🔗 Link of the pages")
st.caption("Link every step of your funnel and their conversion rate:")

with st.container():
    for i, step in enumerate(st.session_state.funnel_steps):
        st.text_input(f"Step {i+1} Name", step["name"], key=f"step_name_{i}")
        st.text_input(f"Step {i+1} Link", step["link"], key=f"step_link_{i}")
        st.number_input(f"Step {i+1} Conversion Rate (%)", step["rate"], min_value=0.0, max_value=100.0, key=f"step_rate_{i}")
        st.divider()

    if st.button("➕ Add Step"):
        st.session_state.funnel_steps.append({"name": "", "link": "", "rate": 0.0})
        st.rerun()

# --- Optional file upload ---
uploaded_file = st.file_uploader("Upload HTML/content file (optional)", type=["html", "htm", "txt"])

# --- Submit button ---
if st.button("Generate Improvement Suggestions"):
    st.info("Generating AI suggestions... ⏳")

    # Collect funnel data and fetch content
    funnel_data = []
    funnel_html = ""
    for i, step in enumerate(st.session_state.funnel_steps):
        name = st.session_state.get(f"step_name_{i}", "")
        link = st.session_state.get(f"step_link_{i}", "")
        rate = st.session_state.get(f"step_rate_{i}", 0.0)
        html_content = fetch_page_content(link) if link else ""
        funnel_data.append({"name": name, "link": link, "rate": rate})
        funnel_html += f"\n\n---\nSTEP: {name}\nURL: {link}\nConversion: {rate}%\nContent:\n{html_content[:1000]}..."  # truncate for prompt

    page_content = None
    if uploaded_file:
        try:
            page_content = uploaded_file.read().decode("utf-8")
        except Exception:
            page_content = uploaded_file.read().decode("latin-1")

    # Build prompt input
    desired_outcome = (
        f"Improve {content_target}. Current version: {current_version}\n"
        f"Offer: {offer_definition}\n"
        f"Funnel Data:\n{funnel_html}"
    )

    suggestions = run_agents(content_target, "", page_content, desired_outcome)
    st.subheader("💡 AI Suggestions")
    choice = st.radio("Select one:", suggestions)
    if st.button("Apply & Update Code"):
        update_github_file("index.html", choice)
        st.success("✅ Code updated on GitHub!")
        st.session_state.chat_history.append({
            "content_target": content_target,
            "offer_definition": offer_definition,
            "funnel_data": funnel_data,
            "current_version": current_version,
            "suggestions": suggestions,
            "chosen": choice,
        })

# --- Chat History ---
if st.session_state.chat_history:
    st.subheader("💬 Chat History")
    for i, chat in enumerate(st.session_state.chat_history[::-1], 1):
        st.markdown(f"**Interaction {i}:**")
        st.markdown(f"- **Content Target:** {chat['content_target']}")
        st.markdown(f"- **Offer Definition:** {chat['offer_definition']}")
        st.markdown(f"- **Funnel Data:** {chat['funnel_data']}")
        st.markdown(f"- **Current Version:** {chat['current_version']}")
        st.markdown(f"- **Suggestions:** {chat['suggestions']}")
        st.markdown(f"- **Chosen:** {chat['chosen']}")
        st.markdown("---")
