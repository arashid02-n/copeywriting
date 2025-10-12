import streamlit as st
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import re
import streamlit_authenticator as stauth

# --- Page setup ---
st.set_page_config(page_title="Sign Up", page_icon="📝")
st.title("📝 Create a New Account")

# --- Load users config ---
config_path = Path(__file__).parent.parent / "users.yaml"

try:
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("❌ Configuration file not found. Please contact the administrator.")
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
    # ✅ Validation 1: All fields filled
    if not all([name, username, email, password, confirm]):
        st.error("⚠️ Please fill in all fields.")
        st.stop()

    # ✅ Validation 2: Email format
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email):
        st.error("❌ Invalid email format.")
        st.stop()

    # ✅ Validation 3: Password length
    if len(password) < 8:
        st.error("❌ Password must be at least 8 characters long.")
        st.stop()

    # ✅ Validation 4: Password match
    if password != confirm:
        st.error("❌ Passwords do not match.")
        st.stop()

    # ✅ Validation 5: Username availability
    if username in config["credentials"]["usernames"]:
        st.warning("⚠️ Username already exists. Please choose another one.")
        st.stop()

    # --- Hash password securely ---
    hashed_password = stauth.Hasher().hash(password)

    # --- Add new user ---
    config["credentials"]["usernames"][username] = {
        "name": name,
        "email": email,
        "password": hashed_password,
    }

    # --- Save updated users to YAML ---
    with open(config_path, "w") as file:
        yaml.dump(config, file, default_flow_style=False)

    st.success("✅ Account created successfully! You can now log in.")
    st.switch_page("pages/login.py")
