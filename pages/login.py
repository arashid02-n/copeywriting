# pages/login.py
import os
import yaml
import streamlit as st
from urllib.parse import urlencode
from dotenv import load_dotenv
import streamlit_authenticator as stauth

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# -------------------------------
# Load credentials from YAML
# -------------------------------
CREDENTIALS_PATH = "users.yaml"

def load_credentials():
    with open(CREDENTIALS_PATH, "r") as file:
        return yaml.safe_load(file)

def save_credentials(data):
    with open(CREDENTIALS_PATH, "w") as file:
        yaml.safe_dump(data, file, default_flow_style=False)

config = load_credentials()

# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

st.title("🔐 Welcome to Copey AI")

# -------------------------------
# Authenticator setup
# -------------------------------
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# -------------------------------
# Login form
# -------------------------------
st.subheader("Login")

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

# -------------------------------
# Divider
# -------------------------------
st.markdown("---")
st.subheader("🆕 Create a new account (Sign Up)")

with st.form("signup_form"):
    new_username = st.text_input("Choose a username")
    new_name = st.text_input("Full name")
    new_password = st.text_input("Choose a password", type="password")
    signup = st.form_submit_button("Sign Up")

    if signup:
        if not new_username or not new_password:
            st.warning("Please enter both username and password")
        elif new_username in config['credentials']['usernames']:
            st.error("❌ Username already exists, please choose another")
        else:
            hashed_pw = stauth.Hasher([new_password]).generate()[0]
            config['credentials']['usernames'][new_username] = {
                "name": new_name or new_username,
                "password": hashed_pw
            }
            save_credentials(config)
            st.success("✅ Account created successfully! You can now log in.")

# -------------------------------
# Google OAuth (optional)
# -------------------------------
st.markdown("---")
st.subheader("Or sign in with Google")

if GOOGLE_CLIENT_ID and GOOGLE_REDIRECT_URI:
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "token",
        "scope": "openid email profile",
        "prompt": "select_account"
    })
    st.markdown(f"[👉 Click here to authorize with Google]({auth_url})")
else:
    st.info("Google OAuth not configured. Add credentials in .env")
