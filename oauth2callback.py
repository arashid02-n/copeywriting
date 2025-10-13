# oauth2callback.py
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from dotenv import load_dotenv
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import streamlit_authenticator as stauth
from passlib.hash import bcrypt

# --- Load env ---
load_dotenv()

st.set_page_config(page_title="Google Auth", page_icon="🔑")
st.write("⏳ Authenticating with Google...")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

query_params = st.query_params
if "code" not in query_params:
    st.error("❌ Invalid OAuth request — no code parameter found.")
    st.stop()

try:
    # --- OAuth Flow ---
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["openid", "email", "profile"]
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    flow.fetch_token(code=query_params["code"][0])

    credentials = flow.credentials
    idinfo = id_token.verify_oauth2_token(
        credentials._id_token,
        requests.Request(),
        GOOGLE_CLIENT_ID
    )

    email = idinfo.get("email")
    name = idinfo.get("name")

    # --- Load YAML users file ---
    config_path = Path(__file__).parent / "users.yaml"

    if not config_path.exists():
        st.error("❌ users.yaml file not found on server.")
        st.stop()

    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=SafeLoader)

    # --- If user not exists, add it ---
    usernames = config["credentials"]["usernames"]
    username_key = email.split("@")[0]  # create username base on email

     if username_key not in usernames:
    # use bcrypt to hash a dummy password for google user
     hashed_password = safe_bcrypt_hash("google_oauth_user")

        usernames[username_key] = {
            "name": name,
            "email": email,
            "password": hashed_password
        }

        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        st.info(f"👤 New Google user added: {email}")

    # --- Set session ---
    st.session_state["authenticated"] = True
    st.session_state["user"] = {"email": email, "name": name}

    st.success(f"✅ Logged in as {name} ({email})")
    st.switch_page("app.py")

except Exception as e:
    st.error(f"⚠️ Authentication failed: {e}")
