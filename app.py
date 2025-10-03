import streamlit as st
from agents import run_agents
from github_utils import update_github_file

# Streamlit page setup
st.set_page_config(page_title="Copywriting Improvement AI", page_icon="✍️", layout="centered")

st.title("✍️ Copywriting Improvement AI")

# Input form for user
with st.form("input_form"):
    offer_definition = st.text_area("Offer definition")
    page_link = st.text_input("Link of the page")
    past_experience = st.text_area("Past experience")
    audience_characteristics = st.text_area("Audience characteristics")
    problem_area = st.selectbox(
        "Which part do you want to improve?",
        ["Headline", "Sub-headline", "CTA"]
    )
    submitted = st.form_submit_button("Generate Suggestions")

if submitted:
    st.info("Generating suggestions... please wait ⏳")
    
    # Run multi-agent pipeline
    suggestions = run_agents(
        offer_definition,
        page_link,
        past_experience,
        audience_characteristics,
        problem_area
    )
    
    st.subheader("Suggestions")
    choice = st.radio("Pick one:", suggestions)
    
    if st.button("Apply & Update Code"):
        # Example: Update GitHub file (simplified demo)
        file_path = "index.html"  # you can adjust this later
        update_github_file(file_path, choice)
        st.success("✅ Code updated on GitHub!")
