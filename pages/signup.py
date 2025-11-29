import streamlit as st
import re
import os
from dotenv import load_dotenv
from db_accounts import init_db, create_user, get_user_by_username, get_user_by_email
from posthog_client import track_event

# --- Initialize database ---
init_db()

# --- Page setup ---
st.set_page_config(page_title="Sign Up", page_icon="📝")
st.title("📝 Create a New Account")

# --- Sign up form ---
with st.form("signup_form", clear_on_submit=True):
    name = st.text_input("Full Name")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    submitted = st.form_submit_button("Sign Up")

if submitted:
    if not all([name, username, email, password, confirm]):
        st.error("⚠️ Please fill in all fields.")
        st.stop()
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
        st.error("❌ Invalid email format.")
        st.stop()
    if len(password) < 8:
        st.error("❌ Password must be at least 8 characters long.")
        st.stop()
    if password != confirm:
        st.error("❌ Passwords do not match.")
        st.stop()
    if get_user_by_username(username):
        st.warning("⚠️ Username already exists. Please choose another one.")
        st.stop()
    if get_user_by_email(email):
        st.warning("⚠️ Email already registered.")
        st.stop()

    create_user(username=username, name=name, email=email, password=password)
    st.success("✅ Account created successfully! You can now log in.")

    # --- Track sign up event ---
    new_user = get_user_by_username(username)
    if new_user:
        track_event(new_user["id"], "sign_up")

    st.switch_page("pages/login.py")

# --- Google Sign Up ---
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

st.markdown("----")
st.markdown("### Or Sign Up with Google")
google_url = (
    "https://accounts.google.com/o/oauth2/auth"
    f"?client_id={GOOGLE_CLIENT_ID}"
    f"&redirect_uri={GOOGLE_REDIRECT_URI}"
    "&response_type=code"
    "&scope=openid%20https://www.googleapis.com/auth/userinfo.profile%20https://www.googleapis.com/auth/userinfo.email"
    "&access_type=offline"
)
st.markdown(f"[🟢 Continue with Google]({google_url})", unsafe_allow_html=True)
