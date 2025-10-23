import streamlit as st
import os
from dotenv import load_dotenv
from db import init_db, get_user_by_username, verify_hash, set_last_login  # using db.py functions
from db_accounts import init_db, get_user_by_username, verify_hash, set_last_login

# --- Initialize database ---
init_db()

# --- Page config ---
st.set_page_config(page_title="Login", page_icon="🔐")
st.title("🔐 Login")

# --- Login form ---
with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

if submitted:
    user_row = get_user_by_username(username)
    if not user_row:
        st.error("❌ Username does not exist.")
    else:
        stored_hash = user_row["password_hash"]
        if verify_hash(password, stored_hash):
            st.session_state["authentication_status"] = True
            st.session_state["authenticated"] = True
            st.session_state["user"] = {
                "id": user_row["id"],
                "name": user_row["name"],
                "email": user_row["email"]
            }
            set_last_login(user_row["id"])
            st.success(f"✅ Welcome, {user_row['name']}!")
            st.session_state["rerun"] = True
            st.query_params = st.query_params  # forces a rerun
        else:
            st.error("❌ Incorrect password.")

# --- Google Login ---
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

st.markdown("----")
st.markdown("### Or Log In with Google")
google_url = (
    "https://accounts.google.com/o/oauth2/auth"
    f"?client_id={GOOGLE_CLIENT_ID}"
    f"&redirect_uri={GOOGLE_REDIRECT_URI}"
    "&response_type=code"
    "&scope=openid%20https://www.googleapis.com/auth/userinfo.profile%20https://www.googleapis.com/auth/userinfo.email"
    "&access_type=offline"
)
st.markdown(f"[🔵 Log in with Google]({google_url})", unsafe_allow_html=True)
