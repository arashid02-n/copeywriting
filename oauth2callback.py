# pages/oauth2callback.py
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Google Auth Callback", page_icon="🔑")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

st.write("⏳ Authenticating with Google...")

# Parse query params
query_params = st.query_params
if "state" not in query_params or "code" not in query_params:
    st.error("❌ Missing OAuth parameters. Try again.")
    st.stop()

try:
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
    id_info = id_token.verify_oauth2_token(
        credentials._id_token,
        requests.Request(),
        GOOGLE_CLIENT_ID
    )

    email = id_info.get("email")
    name = id_info.get("name")

    st.session_state["authenticated"] = True
    st.session_state["user"] = {"email": email, "name": name}
    st.success(f"✅ Welcome {name} ({email})!")
    st.switch_page("app.py")

except Exception as e:
    st.error(f"⚠️ Google Authentication failed: {e}")
