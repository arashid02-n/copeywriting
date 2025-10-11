# pages/login.py
import os
import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")
st.title("🔐 Sign in to Copey AI")

# -------------------------------
# Google Authenticator
# -------------------------------
authenticator = stauth.GoogleAuthenticator(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    redirect_uri="http://localhost:8503"  # وقتی روی سرور است، آدرس دامنه خودت را بگذار
)

# -------------------------------
# Login button
# -------------------------------
user_info = authenticator.login("Sign in with Google")

if user_info:
    # Save user info in session state
    st.session_state["user"] = user_info
    st.success(f"Welcome {user_info['name']} 👋")
    
    # Redirect to main page (app.py)
    st.experimental_set_query_params(page="main")

