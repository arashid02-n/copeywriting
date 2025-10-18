# agents.py
import os
from typing import List, Optional
from dotenv import load_dotenv
import openai

# load .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set. Put your OpenAI key in .env.")

openai.api_key = OPENAI_API_KEY

# default model
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

def call_openai_chat(prompt: str, max_tokens: int = 400, temperature: float = 0.2) -> str:
    """
    Call OpenAI ChatCompletion (gpt-3.5-turbo) and return the assistant text.
    """
    messages = [
        {"role": "system", "content": "You are a helpful, concise copywriting assistant."},
        {"role": "user", "content": prompt}
    ]

    resp = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        n=1
    )

    # Extract assistant reply
    return resp["choices"][0]["message"]["content"].strip()

def run_agents(content_target: str,
               page_link: Optional[str] = None,
               page_content: Optional[str] = None,
               desired_outcome: Optional[str] = None) -> List[str]:
    """
    Generate up to 4 short suggestions for copy improvements using OpenAI.
    """

    prompt = f"""
You are a professional copywriting assistant specialized in improving website content.

Content target:
{content_target or ''}

Website link:
{page_link or "No link provided."}

Uploaded content (first 1200 characters):
{(page_content[:1200] if page_content else "No uploaded content provided.")}

Desired outcome:
{desired_outcome or "No specific outcome provided."}

Task:
Provide 4 short, actionable, and numbered suggestions that improve the above content.
Each suggestion should be a short sentence ready to replace or update the website text.
Only return the numbered suggestions (1., 2., 3., 4.).
"""

    raw_output = call_openai_chat(prompt, max_tokens=400, temperature=0.2)

    # Parse suggestions into up to 4 items
    lines = [l.strip() for l in raw_output.splitlines() if l.strip()]
    suggestions = []

    for line in lines:
        # try to detect leading number
        if line and line[0].isdigit() and (line[1:2] in [".", ")", "-", ":"]):
            # split after the number token
            parts = line.split(maxsplit=1)
            cleaned = parts[1] if len(parts) > 1 else line
            suggestions.append(cleaned.strip())
        else:
            if len(suggestions) < 4:
                suggestions.append(line.strip())
        if len(suggestions) >= 4:
            break

    # fallback if empty
    if not suggestions:
        # split by double newline
        chunks = [p.strip() for p in raw_output.split("\n\n") if p.strip()]
        suggestions = chunks[:4]

    return suggestions[:4]
