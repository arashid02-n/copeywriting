# agents.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# --- Load .env ---
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY is not set in .env")

client = OpenAI(api_key=OPENAI_API_KEY)


def run_agents(content_target: str,
               current_version: str,
               offer_definition: str,
               funnel_links: list,
               desired_outcome: str) -> list:
    """
    Generate 4 improved suggestions for the specified website content.
    """

    # Prepare the funnel description
    funnel_text = "\n".join([
        f"- {step['name']} ({step['link']}): {step['rate']}%"
        for step in funnel_links
    ]) if funnel_links else "No funnel data provided."

    prompt = f"""
You are a professional copywriting assistant specialized in improving website conversion and clarity.

### Section to Improve:
{content_target}

### Current Version:
{current_version}

### Offer Definition:
{offer_definition}

### Funnel Data:
{funnel_text}

### Desired Outcome:
{desired_outcome or "Improve clarity, persuasion, and conversion."}

Please provide **4 short, numbered suggestions** to improve this section. 
Each suggestion should be clear, actionable, and under two sentences.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert marketing copywriter."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    text = response.choices[0].message.content.strip()
    suggestions = [s.strip() for s in text.split("\n") if s.strip()]

    # Ensure max 4
    return suggestions[:4]
