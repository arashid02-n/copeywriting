import streamlit as st
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import streamlit_authenticator as stauth

# --- Page config ---
st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 Login to Copey AI")

# --- Load config file ---
config_path = Path(__file__).parent.parent / "users.yaml"

try:
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("❌ User configuration file not found. Please contact admin.")
    st.stop()

# --- Initialize authenticator ---
try:
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config.get('preauthorized', {}).get('emails', [])
    )
except Exception as e:
    st.error(f"⚠️ Error initializing authenticator: {e}")
    st.stop()

# --- Render login form ---
authenticator.login(fields={'Form name': 'Login to your account'}, location="main")

# --- Handle authentication result ---
if st.session_state.get("authentication_status"):
    st.success(f"✅ Welcome, {st.session_state.get('name')}!")
    authenticator.logout("Logout", "sidebar")
    st.switch_page("app.py")

elif st.session_state.get("authentication_status") is False:
    st.error("❌ Incorrect username or password.")

elif st.session_state.get("authentication_status") is None:
    st.info("Please enter your username and password to continue.")
