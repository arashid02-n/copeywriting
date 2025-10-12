# pages/login.py
import os
import streamlit as st
import yaml
from yaml.loader import SafeLoader
from passlib.hash import bcrypt
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")
st.title("🔐 Login to Copey AI")

# Load users
CREDENTIALS_PATH = "users.yaml"
with open(CREDENTIALS_PATH, "r") as f:
    config = yaml.safe_load(f)

users = config.get("credentials", {}).get("usernames", {})

# --- Manual login form ---
with st.form("login_form"):
    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

    if submitted:
        if username_input not in users:
            st.error("Username not found.")
        else:
            stored = users[username_input]
            stored_hash = stored.get("password", "")
            # Verify bcrypt password
            try:
                ok = bcrypt.verify(password_input, stored_hash)
            except Exception as e:
                ok = False
            if ok:
                # login success
                st.session_state["user"] = {"name": stored.get("name", username_input),
                                            "username": username_input,
                                            "email": stored.get("email", "")}
                st.success(f"Welcome {st.session_state['user']['name']} 👋")
                st.experimental_rerun()
            else:
                st.error("Incorrect password.")

st.markdown("---")
st.markdown("Don't have an account? [👉 Sign Up here](signup)")

# Google OAuth (optional link)
st.markdown("---")
st.subheader("Or sign in with Google")
if GOOGLE_CLIENT_ID and GOOGLE_REDIRECT_URI:
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "token",
        "scope": "openid email profile",
        "prompt": "select_account"
    })
    st.markdown(f"[👉 Click here to authorize with Google]({auth_url})")
else:
    st.info("Google OAuth not configured. Add GOOGLE_CLIENT_ID and GOOGLE_REDIRECT_URI in .env")
