# pages/login.py
import os
import streamlit as st
from urllib.parse import urlencode
from dotenv import load_dotenv
import streamlit_authenticator as stauth

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")  # http://localhost:8503 یا دامنه واقعی

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")
st.title("🔐 Sign in to Copey AI")

# -------------------------------
# Simple login (username/password)
# -------------------------------
names = ["Rashid"]
usernames = ["rashid"]
passwords = ["1234"]  # حتماً پسورد واقعی را امن ذخیره کن

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords,
    "copey_cookie", "abcdef", cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.session_state["user"] = {"name": name, "username": username}
    st.success(f"Welcome {name} 👋")
elif authentication_status == False:
    st.error("Username/password is incorrect")
elif authentication_status == None:
    st.warning("Please enter your username and password")

# -------------------------------
# Google OAuth login
# -------------------------------
st.markdown("---")
st.subheader("Or sign in with Google")

auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
    "client_id": GOOGLE_CLIENT_ID,
    "redirect_uri": GOOGLE_REDIRECT_URI,
    "response_type": "token",
    "scope": "openid email profile",
    "prompt": "select_account"
})

st.markdown(f"[Click here to authorize with Google]({auth_url})")
