# app.py
import streamlit as st
from agents import run_agents
from github_utils import update_github_file
from dotenv import load_dotenv
import os

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Copywriting Improvement AI",
    page_icon="✍️",
    layout="centered"
)

# -------------------------------
# Check if user is logged in
# -------------------------------
if "user" not in st.session_state:
    st.warning("Please login first from the Login page.")
    st.stop()

# -------------------------------
# Helper to read user fields safely
# -------------------------------
def _user_field(user, key):
    if user is None:
        return None
    if isinstance(user, dict):
        return user.get(key)
    return getattr(user, key, None)

user = st.session_state["user"]
user_name = _user_field(user, "name") or _user_field(user, "email") or "User"

st.sidebar.markdown(f"**Signed in as:** {user_name}")

# -------------------------------
# Chat app content
# -------------------------------
st.title("✍️ Copywriting Improvement AI")
st.markdown("Welcome! Let's improve your website content using AI 💡")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.form("input_form"):
    content_target = st.text_area(
        "What part of your website do you want to change?",
        placeholder="Example: Homepage headline, product section, CTA button text..."
    )

    st.markdown("Provide your website link **or** upload your page files (HTML, etc.)")
    page_link = st.text_input("Website Link (optional)")
    uploaded_file = st.file_uploader("Upload your HTML or content file (optional)", type=["html", "htm", "txt"])

    desired_outcome = st.text_area(
        "Describe how you want the improved content to be:",
        placeholder="Example: More persuasive, clearer message, better conversion rate..."
    )

    submitted = st.form_submit_button("Generate Improvement Suggestions")

if submitted:
    st.info("Generating AI suggestions... please wait ⏳")

    page_content = None
    if uploaded_file is not None:
        try:
            page_content = uploaded_file.read().decode("utf-8")
        except Exception:
            page_content = uploaded_file.read().decode("latin-1")

    suggestions = run_agents(
        content_target=content_target,
        page_link=page_link,
        page_content=page_content,
        desired_outcome=desired_outcome
    )

    st.subheader("💡 AI Suggestions")
    choice = st.radio("Select the one you like best:", suggestions)

    if st.button("Apply & Update Code"):
        file_path = "index.html"
        update_github_file(file_path, choice)
        st.success("✅ Code updated successfully on GitHub!")

        st.session_state.chat_history.append({
            "content_target": content_target,
            "page_link": page_link,
            "desired_outcome": desired_outcome,
            "uploaded_file_name": uploaded_file.name if uploaded_file else None,
            "suggestions": suggestions,
            "chosen": choice
        })

if st.session_state.chat_history:
    st.subheader("💬 Chat History")
    for i, chat in enumerate(st.session_state.chat_history[::-1], 1):
        st.markdown(f"**Interaction {i}:**")
        st.markdown(f"- **Content Target:** {chat['content_target']}")
        st.markdown(f"- **Page Link:** {chat['page_link']}")
        st.markdown(f"- **Uploaded File:** {chat['uploaded_file_name']}")
        st.markdown(f"- **Desired Outcome:** {chat['desired_outcome']}")
        st.markdown(f"- **Suggestions:** {chat['suggestions']}")
        st.markdown(f"- **Chosen:** {chat['chosen']}")
        st.markdown("---")
