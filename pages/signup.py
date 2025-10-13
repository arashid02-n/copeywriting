import streamlit as st
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import re
import os
from dotenv import load_dotenv
from passlib.hash import bcrypt

# --- Safe bcrypt hash (truncate to 72 bytes) ---
def safe_bcrypt_hash(password: str) -> str:
    if password is None:
        password = ""
    pw_bytes = password.encode("utf-8")[:72]  # truncate to 72 bytes
    pw_truncated = pw_bytes.decode("utf-8", errors="ignore")
    return bcrypt.hash(pw_truncated)

# --- Page setup ---
st.set_page_config(page_title="Sign Up", page_icon="📝")
st.title("📝 Create a New Account")

# --- Load users.yaml ---
config_path = Path(__file__).parent.parent / "users.yaml"
try:
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("❌ Configuration file not found.")
    st.stop()

# --- Sign up form ---
with st.form("signup_form", clear_on_submit=True):
    name = st.text_input("Full Name")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Sign Up")

if submitted:
    if not all([name, username, email, password, confirm]):
        st.error("⚠️ Please fill in all fields.")
        st.stop()
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
        st.error("❌ Invalid email format.")
        st.stop()
    if len(password) < 8:
        st.error("❌ Password must be at least 8 characters long.")
        st.stop()
    if password != confirm:
        st.error("❌ Passwords do not match.")
        st.stop()
    if username in config["credentials"]["usernames"]:
        st.warning("⚠️ Username already exists. Please choose another one.")
        st.stop()

    hashed_password = safe_bcrypt_hash(password)

    config["credentials"]["usernames"][username] = {
        "name": name,
        "email": email,
        "password": hashed_password
    }

    with open(config_path, "w") as file:
        yaml.dump(config, file, default_flow_style=False)

    st.success("✅ Account created successfully! You can now log in.")
    st.switch_page("pages/login.py")

# --- Google Sign Up ---
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

st.markdown("----")
st.markdown("### Or Sign Up with Google")
google_url = (
    "https://accounts.google.com/o/oauth2/auth"
    f"?client_id={GOOGLE_CLIENT_ID}"
    f"&redirect_uri={GOOGLE_REDIRECT_URI}"
    "&response_type=code"
    "&scope=openid%20https://www.googleapis.com/auth/userinfo.profile%20https://www.googleapis.com/auth/userinfo.email"
    "&access_type=offline"
)
st.markdown(f"[🟢 Continue with Google]({google_url})", unsafe_allow_html=True)
