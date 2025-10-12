# pages/signup.py
import streamlit as st
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from passlib.hash import bcrypt  # Password hashing with bcrypt

st.set_page_config(page_title="Sign Up", page_icon="📝", layout="centered")

st.title("📝 Create a New Account")

# --- Load users config ---
config_path = Path(__file__).parent.parent / "users.yaml"
if not config_path.exists():
    # If users.yaml does not exist, create a minimal skeleton
    initial = {
        "credentials": {"usernames": {}},
        "cookie": {"name": "copey_cookie", "key": "abcdef", "expiry_days": 1}
    }
    with open(config_path, "w") as f:
        yaml.safe_dump(initial, f)

with open(config_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

# --- Sign up form ---
with st.form("signup_form", clear_on_submit=True):
    name = st.text_input("Full Name")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Sign Up")

    if submitted:
        # Basic validation
        if not username or not password:
            st.error("Please provide both username and password.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif username in config.get("credentials", {}).get("usernames", {}):
            st.warning("Username already exists.")
        else:
            # --- Hash password using passlib bcrypt ---
            # English comment: Use passlib bcrypt to generate a secure bcrypt hash.
            hashed_password = bcrypt.hash(password)

            # --- Add new user to credentials ---
            if "credentials" not in config:
                config["credentials"] = {"usernames": {}}
            if "usernames" not in config["credentials"]:
                config["credentials"]["usernames"] = {}

            config["credentials"]["usernames"][username] = {
                "email": email or "",
                "name": name or username,
                "password": hashed_password
            }

            # --- Save updated users to YAML ---
            with open(config_path, "w") as file:
                yaml.safe_dump(config, file, default_flow_style=False)

            st.success("✅ Account created successfully! You can now log in.")
            # Redirect to login page
            st.experimental_rerun()
