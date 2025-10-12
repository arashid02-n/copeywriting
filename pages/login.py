import streamlit as st
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import streamlit_authenticator as stauth
import os
from dotenv import load_dotenv

# --- Page config ---
st.set_page_config(page_title="Login", page_icon="🔐")

st.title("🔐 Login")

# --- Load config file ---
config_path = Path(__file__).parent.parent / "users.yaml"

try:
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("❌ User configuration file not found.")
    st.stop()

# --- Initialize authenticator ---
try:
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config.get("preauthorized", {}).get("emails", [])
    )
except Exception as e:
    st.error(f"⚠️ Authenticator init error: {e}")
    st.stop()

# --- Create login form ---
try:
    authenticator.login(location="main", fields={'Form name': 'User Login'})
except Exception as e:
    st.error(f"⚠️ Error loading login form: {e}")
    st.stop()
# --- Google Login ---
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

st.markdown("----")
st.markdown("### Or Log In with Google")

google_url = (
    "https://accounts.google.com/o/oauth2/auth"
    f"?client_id={GOOGLE_CLIENT_ID}"
    f"&redirect_uri={GOOGLE_REDIRECT_URI}"
    "&response_type=code"
    "&scope=openid%20https://www.googleapis.com/auth/userinfo.profile%20https://www.googleapis.com/auth/userinfo.email"
    "&access_type=offline"
)
st.markdown(f"[🔵 Log in with Google]({google_url})", unsafe_allow_html=True)
# --- Handle login state ---
auth_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")

if auth_status:
    st.success(f"✅ Welcome, {name}!")
    authenticator.logout("Logout", "sidebar")
    st.switch_page("app.py")

elif auth_status is False:
    st.error("❌ Incorrect username or password.")

else:
    st.info("Please log in to continue.")
