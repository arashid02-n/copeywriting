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
    # Proper indentation for the try block
    name, authentication_status, username = authenticator.login("Login", location="main")
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
if authentication_status:
    st.success(f"✅ Welcome, {name}!")
    authenticator.logout("Logout", "sidebar")
    # --- Set session_state flags so app.py can pick it up ---
    st.session_state["authentication_status"] = True
    st.session_state["authenticated"] = True
    st.session_state["user"] = {"name": name, "email": username}
    st.session_state["google_login_done"] = False
    st.experimental_rerun()  # safe only after normal login

elif authentication_status is False:
    st.error("❌ Incorrect username or password.")

else:
    st.info("Please log in to continue.")
