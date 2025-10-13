import streamlit as st
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import os
from dotenv import load_dotenv
import hashlib

# --- Secure hash check ---
def verify_hash(password: str, hashed: str) -> bool:
    try:
        salt, hash_val = hashed.split("$")
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest() == hash_val
    except Exception:
        return False

# --- Page config ---
st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 Login")

# --- Load users.yaml ---
config_path = Path(__file__).parent.parent / "users.yaml"
try:
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("❌ User configuration file not found.")
    st.stop()

# --- Login form ---
with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

if submitted:
    usernames = config["credentials"]["usernames"]
    if username not in usernames:
        st.error("❌ Username does not exist.")
    else:
        stored_hash = usernames[username]["password"]
        if verify_hash(password, stored_hash):
            st.session_state["authentication_status"] = True
            st.session_state["authenticated"] = True
            st.session_state["user"] = {"name": usernames[username]["name"], "email": usernames[username]["email"]}
            st.success(f"✅ Welcome, {usernames[username]['name']}!")
            st.experimental_rerun()
        else:
            st.error("❌ Incorrect password.")

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
