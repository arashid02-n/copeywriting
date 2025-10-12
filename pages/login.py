# pages/login.py
import os
import streamlit as st
from dotenv import load_dotenv
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

# -------------------------------
# Load credentials
# -------------------------------
with open("users.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# -------------------------------
# Streamlit Config
# -------------------------------
st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")
st.title("🔐 Login to Copey AI")

# -------------------------------
# Authenticator setup
# -------------------------------
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# -------------------------------
# Login Form
# -------------------------------
try:
    name, authentication_status, username = authenticator.login("Login", location="main")
except TypeError:
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
    st.error("❌ Username or password incorrect")
elif authentication_status is None:
    st.info("Please enter your credentials")

st.markdown("---")
st.markdown("Don't have an account? [👉 Sign Up here](signup)")
