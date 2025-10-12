import streamlit as st
from agents import run_agents
from github_utils import update_github_file
from dotenv import load_dotenv
import os
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import streamlit_authenticator as stauth
import time

# --- Google OAuth dependencies ---
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

# ---------------------------------
# Load environment variables
# ---------------------------------
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# ---------------------------------
# Handle Google OAuth callback
# ---------------------------------
query_params = st.query_params

if "code" in query_params and not st.session_state.get("google_login_done", False):
    st.write("⏳ Completing Google sign-in...")
    code = query_params["code"][0] if isinstance(query_params["code"], list) else query_params["code"]

    try:
        # --- Initialize Google OAuth flow ---
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

        # --- Verify token and extract user info ---
        idinfo = id_token.verify_oauth2_token(
            credentials._id_token,
            grequests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        name = idinfo.get("name")

        # --- Save user in users.yaml if not exists ---
        config_path = Path(__file__).parent / "users.yaml"
        if config_path.exists():
            with open(config_path, "r") as f:
                config = yaml.load(f, Loader=SafeLoader)
        else:
            config = {
                "credentials": {"usernames": {}},
                "cookie": {"name": "copey_cookie", "key": "super_secret_signature_key", "expiry_days": 30},
                "preauthorized": {"emails": []}
            }

        username_key = email.split("@")[0]
        if username_key not in config["credentials"]["usernames"]:
            # --- Hash default password for Google user ---
            hashed_password = stauth.Hasher(["google_oauth_user"]).generate()[0]
            config["credentials"]["usernames"][username_key] = {
                "name": name or username_key,
                "email": email,
                "password": hashed_password
            }
            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
            st.info(f"👤 New Google user added: {email}")

        # --- Set session state ---
        st.session_state["authentication_status"] = True
        st.session_state["authenticated"] = True
        st.session_state["user"] = {"email": email, "name": name}
        st.session_state["google_login_done"] = True

        # --- Show success message ---
        st.success(f"✅ Logged in successfully as {name}")

        # --- HTML redirect after 3 seconds to main app ---
        st.markdown("""
        <meta http-equiv="refresh" content="3;url=/">
        """, unsafe_allow_html=True)

        # --- Stop further execution ---
        st.stop()

    except Exception as e:
        st.error(f"⚠️ Google sign-in failed: {e}")
        st.stop()

# ---------------------------------
# Streamlit Page Configuration
# ---------------------------------
st.set_page_config(
    page_title="Copywriting Improvement AI",
    page_icon="✍️",
    layout="centered"
)

# ---------------------------------
# Authentication check
# ---------------------------------
if not st.session_state.get("authentication_status", False):
    st.warning("⚠️ Please login first from the Login page.")
    st.stop()

# Retrieve user info from session_state
user = st.session_state.get("user", {})
user_name = user.get("name") or user.get("email") or "User"

# ---------------------------------
# Sidebar user info and logout
# ---------------------------------
st.sidebar.markdown(f"**Signed in as:** {user_name}")
if st.sidebar.button("🚪 Logout"):
    st.session_state["authenticated"] = False
    st.session_state["user"] = {}
    st.session_state["authentication_status"] = False
    st.session_state["google_login_done"] = False
    st.experimental_rerun()  # فقط برای logout safe است

# ---------------------------------
# Main app content
# ---------------------------------
st.title("✍️ Copywriting Improvement AI")
st.markdown("Welcome! Let's improve your website content using AI 💡")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.form("input_form"):
    content_target = st.text_area(
        "What part of your website do you want to change?",
        placeholder="Example: Homepage headline, product section, CTA button text..."
    )

    st.markdown("Provide your website link **or** upload your page files (HTML, etc.)")
    page_link = st.text_input("Website Link (optional)")
    uploaded_file = st.file_uploader(
        "Upload your HTML or content file (optional)",
        type=["html", "htm", "txt"]
    )

    desired_outcome = st.text_area(
        "Describe how you want the improved content to be:",
        placeholder="Example: More persuasive, clearer message, better conversion rate..."
    )

    submitted = st.form_submit_button("Generate Improvement Suggestions")

if submitted:
    st.info("Generating AI suggestions... please wait ⏳")

    page_content = None
    if uploaded_file is not None:
        try:
            page_content = uploaded_file.read().decode("utf-8")
        except Exception:
            page_content = uploaded_file.read().decode("latin-1")

    # Run AI agent to generate suggestions
    suggestions = run_agents(
        content_target=content_target,
        page_link=page_link,
        page_content=page_content,
        desired_outcome=desired_outcome
    )

    st.subheader("💡 AI Suggestions")
    choice = st.radio("Select the one you like best:", suggestions)

    if st.button("Apply & Update Code"):
        file_path = "index.html"
        update_github_file(file_path, choice)
        st.success("✅ Code updated successfully on GitHub!")

        st.session_state.chat_history.append({
            "content_target": content_target,
            "page_link": page_link,
            "desired_outcome": desired_outcome,
            "uploaded_file_name": uploaded_file.name if uploaded_file else None,
            "suggestions": suggestions,
            "chosen": choice
        })

# ---------------------------------
# Chat history section
# ---------------------------------
if st.session_state.chat_history:
    st.subheader("💬 Chat History")
    for i, chat in enumerate(st.session_state.chat_history[::-1], 1):
        st.markdown(f"**Interaction {i}:**")
        st.markdown(f"- **Content Target:** {chat['content_target']}")
        st.markdown(f"- **Page Link:** {chat['page_link']}")
        st.markdown(f"- **Uploaded File:** {chat['uploaded_file_name']}")
        st.markdown(f"- **Desired Outcome:** {chat['desired_outcome']}")
        st.markdown(f"- **Suggestions:** {chat['suggestions']}")
        st.markdown(f"- **Chosen:** {chat['chosen']}")
        st.markdown("---")
