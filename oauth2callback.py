# oauth2callback.py  
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

st.set_page_config(page_title="Google Auth", page_icon="🔑")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# --- Page UI ---
st.write("⏳ Authenticating with Google...")

query_params = st.query_params
if "code" not in query_params:
    st.error("❌ Invalid OAuth request — no code parameter found.")
    st.stop()

try:
    # --- Create OAuth Flow ---
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

    # --- Exchange code for tokens ---
    flow.fetch_token(code=query_params["code"][0])
    credentials = flow.credentials

    # --- Verify ID token ---
    idinfo = id_token.verify_oauth2_token(
        credentials._id_token,
        requests.Request(),
        GOOGLE_CLIENT_ID
    )

    email = idinfo.get("email")
    name = idinfo.get("name")

    st.session_state["authenticated"] = True
    st.session_state["user"] = {"email": email, "name": name}

    st.success(f"✅ Logged in as {name} ({email})")

    # --- Redirect to main app ---
    st.switch_page("app.py")

except Exception as e:
    st.error(f"⚠️ Authentication failed: {e}")
