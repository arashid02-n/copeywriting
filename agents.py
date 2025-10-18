# agents.py
import os
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load .env
load_dotenv()

# Create client with key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in .env file!")

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

def call_openai_chat(prompt: str, max_tokens: int = 400, temperature: float = 0.2) -> str:
    """
    Use new OpenAI API (>=1.0.0) to get completion
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful and concise copywriting assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

def run_agents(content_target: str,
               page_link: Optional[str] = None,
               page_content: Optional[str] = None,
               desired_outcome: Optional[str] = None) -> List[str]:
    """
    Generate 4 short, numbered suggestions for copywriting improvements
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
Each suggestion should be short and ready to use directly.
Only return numbered suggestions (1., 2., 3., 4.).
"""
    raw_output = call_openai_chat(prompt, max_tokens=400, temperature=0.2)

    lines = [l.strip() for l in raw_output.splitlines() if l.strip()]
    suggestions = []

    for line in lines:
        if line[0].isdigit() and (line[1:2] in [".", ")", "-", ":"]):
            parts = line.split(maxsplit=1)
            cleaned = parts[1] if len(parts) > 1 else line
            suggestions.append(cleaned.strip())
        else:
            if len(suggestions) < 4:
                suggestions.append(line.strip())
        if len(suggestions) >= 4:
            break

    if not suggestions:
        chunks = [p.strip() for p in raw_output.split("\n\n") if p.strip()]
        suggestions = chunks[:4]

    return suggestions[:4]
