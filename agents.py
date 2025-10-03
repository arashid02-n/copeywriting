import os
from langchain_anthropic import ChatAnthropic

# Initialize Claude
client = ChatAnthropic(model="claude-3-sonnet-20240229", api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_agents(offer_definition, page_link, past_experience, audience_characteristics, problem_area):
    # Prompt template for Claude
    prompt = f"""
    You are a copywriting improvement assistant.
    The user wants to improve the {problem_area}.
    
    Offer: {offer_definition}
    Page: {page_link}
    Experience: {past_experience}
    Audience: {audience_characteristics}
    
    Please generate 4 improved {problem_area} suggestions.
    Only return the suggestions in a numbered list.
    """
    
    response = client.invoke(prompt)
    text = response.content[0].text if response.content else ""
    suggestions = [s.strip() for s in text.split("\n") if s.strip()]
    
    return suggestions[:4]
