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

# ---------------------------------------------------
# 🔥 HIDE STREAMLIT DEFAULT SIDEBAR PAGES (login / signup / app)
# ---------------------------------------------------
st.markdown("""
    <style>
        section[data-testid="stSidebarNav"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

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

        track_event(email, "login_success", {"method": "google"})

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

# ---------------------------------------------------
# CUSTOMIZED SIDEBAR (ONLY USER + LOGOUT)
# ---------------------------------------------------

user = st.session_state.get("user", {})
user_name = user.get("name") or user.get("email") or "User"

st.sidebar.markdown(f"**Signed in as:** {user_name}")

if st.sidebar.button("🚪 Logout"):
    for key in ["authenticated", "authentication_status", "user", "google_login_done", "cookie_authenticated", "cookie_user"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ---------------------------------------------------
# MAIN APP (exactly as your original code)
# ---------------------------------------------------

st.title("✍️ Copywriting Improvement AI")
st.markdown("Welcome! Let's improve your website content using AI 💡")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "funnel_steps" not in st.session_state:
    st.session_state.funnel_steps = []

st.markdown("### 🧠 What is that you want to improve?")
st.caption("Choose the main element you want AI to focus on improving.")

content_options = ["Headline", "Subheadline", "CTA", "Other"]
content_choice = st.selectbox("Choose one:", content_options, key="content_choice")

if content_choice == "Other":
    content_target = st.text_input(
        "Please specify what you want to improve:",
        placeholder="e.g. Logo, Footer, Sidebar"
    )
else:
    content_target = content_choice

st.markdown("### 📄 Current Version")

current_version = st.text_area(
    "Current version:",
    placeholder="Paste or describe the current content here..."
)

st.markdown("### 💼 Offer Definition")
offer_definition = st.text_area(
    "Offer Definition:",
    placeholder="Explain your business, product, or service..."
)

st.markdown("### 🔗 Link of the pages")

with st.container():
    for i, step in enumerate(st.session_state.funnel_steps):
        st.text_input(f"Step {i+1} Name", step["name"], key=f"step_name_{i}")
        st.text_input(f"Step {i+1} Link", step["link"], key=f"step_link_{i}")
        st.number_input(
            f"Step {i+1} Conversion Rate (%)",
            value=step["rate"],
            min_value=0.0,
            max_value=100.0,
            key=f"step_rate_{i}"
        )
        st.checkbox(
            "✅ I want to improve this step",
            value=step.get("improve", False),
            key=f"step_improve_{i}"
        )
        st.divider()

    if st.button("➕ Add Step"):
        st.session_state.funnel_steps.append({"name": "", "link": "", "rate": 0.0, "improve": False})

        user_id = st.session_state.get("user", {}).get("email", "anonymous")
        track_event(user_id, "funnel_step_added", {"step_index": len(st.session_state.funnel_steps)})

        st.rerun()

st.markdown("### 🕒 Past Experience")
past_experience = st.text_area(
    "Your past experiences:",
    placeholder="Describe what improvements you tried before and what happened..."
)

st.markdown("### 🎯 Audience Characteristic")
audience_characteristic = st.text_area(
    "Your audience characteristics:",
    placeholder="Describe your audience..."
)

if st.button("Generate Improvement Suggestions"):
    st.info("Generating AI suggestions... ⏳")

    user_id = st.session_state.get("user", {}).get("email", "anonymous")
    track_event(user_id, "generate_clicked", {"content_target": content_target})

    funnel_data = []
    funnel_html = ""

    for i, step in enumerate(st.session_state.funnel_steps):
        name = st.session_state.get(f"step_name_{i}", "")
        link = st.session_state.get(f"step_link_{i}", "")
        rate = st.session_state.get(f"step_rate_{i}", 0.0)
        improve = st.session_state.get(f"step_improve_{i}", False)

        html_content = fetch_page_content(link) if link else ""

        funnel_data.append({"name": name, "link": link, "rate": rate, "improve": improve})

        funnel_html += f"\n\n---\nSTEP: {name}\nURL: {link}\nConversion: {rate}%\nImprove: {improve}\nContent:\n{html_content[:1000]}..."

    desired_outcome = (
        f"This is a business looking to improve their conversion rate. "
        f"They are working on their {content_target}.\n\n"
        f"Past experiences:\n{past_experience}\n\n"
        f"Funnel pages:\n{funnel_html}\n\n"
        f"Offer: {offer_definition}\n\n"
        f"Audience: {audience_characteristic}"
    )

    suggestions = run_agents(content_target, "", None, desired_outcome)

    st.subheader("💡 AI Suggestions")
    choice = st.radio("Select one:", suggestions)

    if st.button("Apply & Update Code"):
        update_github_file("index.html", choice)
        st.success("✅ Code updated on GitHub!")

        st.session_state.chat_history.append({
            "content_target": content_target,
            "offer_definition": offer_definition,
            "past_experience": past_experience,
            "audience_characteristic": audience_characteristic,
            "funnel_data": funnel_data,
            "current_version": current_version,
            "suggestions": suggestions,
            "chosen": choice,
        })

        track_event(user_id, "suggestion_applied", {"chosen_suggestion": choice})

if st.session_state.chat_history:
    st.subheader("💬 Chat History")
    for i, chat in enumerate(st.session_state.chat_history[::-1], 1):
        st.markdown(f"**Interaction {i}:**")
        st.markdown(f"- **Content Target:** {chat['content_target']}")
        st.markdown(f"- **Offer Definition:** {chat['offer_definition']}")
        st.markdown(f"- **Past Experience:** {chat['past_experience']}")
        st.markdown(f"- **Audience Characteristic:** {chat['audience_characteristic']}")
        st.markdown(f"- **Funnel Data:** {chat['funnel_data']}")
        st.markdown(f"- **Current Version:** {chat['current_version']}")
        st.markdown(f"- **Suggestions:** {chat['suggestions']}")
        st.markdown(f"- **Chosen:** {chat['chosen']}")
        st.markdown("---")
