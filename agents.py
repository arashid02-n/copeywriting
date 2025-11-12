import os
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in .env file!")

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

def call_openai_chat(prompt: str, max_tokens: int = 400, temperature: float = 0.2) -> str:
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
    prompt = f"""
You are a professional copywriting assistant specialized in improving website conversion rate.

This is a business looking to improve their conversion rate.
They are currently working on their [{content_target}] page of their funnel.

Here is their past experience as they say themselves:
{desired_outcome or 'No experience provided.'}

This is the content of each page of their funnel:
- Step Name
- Step URL
- Step Content (truncated if too long)

Task:
Provide 4 short, actionable, and numbered suggestions (1., 2., 3., 4.) to improve conversion rate and copywriting.
Each suggestion must be concise, clear, and directly implementable.
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
