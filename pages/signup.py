import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from pathlib import Path

st.set_page_config(page_title="Sign Up", page_icon="📝")

st.title("📝 Create a New Account")

# --- Load users config ---
config_path = Path(__file__).parent.parent / "users.yaml"
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
        if password != confirm:
            st.error("Passwords do not match.")
        elif username in config["credentials"]["usernames"]:
            st.warning("Username already exists.")
        else:
            # --- Hash password ---
            hashed_password = stauth.Hasher([password]).generate()[0]

            # --- Add new user ---
            config["credentials"]["usernames"][username] = {
                "email": email,
                "name": name,
                "password": hashed_password
            }

            # --- Save updated users to YAML ---
            with open(config_path, "w") as file:
                yaml.dump(config, file, default_flow_style=False)

            st.success("✅ Account created successfully! You can now log in.")
            st.switch_page("pages/login.py")
