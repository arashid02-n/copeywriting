import streamlit as st
from agents import run_agents
from github_utils import update_github_file
from dotenv import load_dotenv
load_dotenv()


# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Copywriting Improvement AI",
    page_icon="✍️",
    layout="centered"
)

st.title("✍️ Copywriting Improvement AI")
st.markdown("Welcome! Let's improve your website content using AI 💡")

# -------------------------------
# Input Form
# -------------------------------
with st.form("input_form"):
    # 1️⃣ Ask user what content they want to change
    content_target = st.text_area(
        "What part of your website do you want to change?",
        placeholder="Example: Homepage headline, product section, CTA button text..."
    )

    # 2️⃣ Ask for the website link (or allow file upload)
    st.markdown("Provide your website link **or** upload the page files (HTML, etc.)")

    page_link = st.text_input("Website Link (optional)")
    uploaded_file = st.file_uploader("Upload your HTML or content file (optional)", type=["html", "htm", "txt"])

    # 3️⃣ Ask what the user wants the new result to look like
    desired_outcome = st.text_area(
        "Describe how you want the improved content to be:",
        placeholder="Example: More persuasive, clearer message, better conversion rate..."
    )

    # Submit button
    submitted = st.form_submit_button("Generate Improvement Suggestions")

# -------------------------------
# Processing after submission
# -------------------------------
if submitted:
    st.info("Generating AI suggestions... please wait ⏳")

    # Extract uploaded file content if provided
    page_content = None
    if uploaded_file is not None:
        page_content = uploaded_file.read().decode("utf-8")

    # Run the AI pipeline (multi-agent system)
    suggestions = run_agents(
        content_target=content_target,
        page_link=page_link,
        page_content=page_content,
        desired_outcome=desired_outcome
    )

    # Show suggestions to user
    st.subheader("💡 AI Suggestions")
    choice = st.radio("Select the one you like best:", suggestions)

    # Confirm and update GitHub
    if st.button("Apply & Update Code"):
        file_path = "index.html"  # You can make this dynamic later
        update_github_file(file_path, choice)
        st.success("✅ Code updated successfully on GitHub!")
