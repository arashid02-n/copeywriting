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

# --- Create login form ---
try:
    name, authentication_status, username = authenticator.login(location="main")
except Exception as e:
    st.error(f"⚠️ Error loading login form: {e}")
    st.stop()

# --- Handle login result ---
if authentication_status:
    st.success(f"✅ Welcome, {name}!")
    authenticator.logout("Logout", "sidebar")
    st.switch_page("app.py")

elif authentication_status is False:
    st.error("❌ Incorrect username or password.")

elif authentication_status is None:
    st.info("Please enter your username and password.")
