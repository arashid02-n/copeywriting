# pages/login.py
import os
import streamlit as st
from urllib.parse import urlencode
from dotenv import load_dotenv
import streamlit_authenticator as stauth

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")  # e.g. http://localhost:8503 or your domain

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")
st.title("🔐 Sign in to Copey AI")

# -------------------------------
# Credentials for normal login
# -------------------------------
credentials = {
    "usernames": {
        "rashid": {
            "name": "Rashid",
            # NOTE: for production, hash your password!
            "password": "1234"
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "copey_cookie",
    "abcdef",
    cookie_expiry_days=1
)

# -------------------------------
# Normal login form
# -------------------------------
try:
    name, authentication_status, username = authenticator.login("Login", location="main")
except TypeError:
    # Fix for recent Streamlit Authenticator versions
    result = authenticator.login(location="main")
    if result:
        name, authentication_status, username = result
    else:
        name = authentication_status = username = None

if authentication_status:
    st.session_state["user"] = {"name": name, "username": username}
    st.success(f"Welcome {name} 👋")
    st.switch_page("app.py")
elif authentication_status is False:
    st.error("Username or password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")

# -------------------------------
# Google OAuth login
# -------------------------------
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
    st.info("Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_REDIRECT_URI in your .env file.")

# Optional: Link to signup page
st.markdown("---")
st.markdown("Don't have an account? [Create one here](signup)")
