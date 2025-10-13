import os
from dotenv import load_dotenv
import requests
from typing import List, Optional

# --- Load .env file ---
dotenv_loaded = load_dotenv()
if not dotenv_loaded:
    print("⚠️ Warning: .env file not loaded. Make sure it exists in the project root.")

# --- Configuration from environment ---
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "tiiuae/falcon-7b-instruct")  # Default model if env missing

if not HF_API_KEY:
    raise RuntimeError("HF_API_KEY is not set. Please add it to your .env file.")

print(f"Using HF_MODEL: {HF_MODEL}")  # Debug: check which model is loaded

# ------------------------------
# Helper function to call Hugging Face Inference API
# ------------------------------
def call_hf_inference(prompt: str, max_tokens: int = 400) -> str:
    """
    Calls Hugging Face Inference API to generate text completions.
    """
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_tokens, "temperature": 0.2},
        "options": {"wait_for_model": True}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Catch 403 and provide a clear message
        if response.status_code == 403:
            raise RuntimeError(f"403 Forbidden: Check your HF_API_KEY or model access. Model: {HF_MODEL}")
        else:
            raise e

    data = response.json()

    # Parse possible response formats
    if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
        return data[0]["generated_text"].strip()
    elif isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"].strip()
    else:
        # fallback for unexpected format
        return str(data)

# ------------------------------
# Main function used by app.py
# ------------------------------
def run_agents(content_target: str,
               page_link: Optional[str] = None,
               page_content: Optional[str] = None,
               desired_outcome: Optional[str] = None) -> List[str]:
    """
    Generate up to 4 improved suggestions for the specified website content.
    """

    # Build a clear, structured prompt
    prompt = f"""
You are a professional copywriting assistant specialized in improving website content.

Content target:
{content_target}

Website link:
{page_link or "No link provided."}

Uploaded content (first 1200 characters):
{(page_content[:1200] if page_content else "No uploaded content provided.")}

Desired outcome:
{desired_outcome or "No specific outcome provided."}

Task:
Provide 4 short, actionable, and numbered suggestions that improve the above content.
Each suggestion should be a short sentence ready to replace or update the website text.
Only return the numbered suggestions.
"""

    # Call Hugging Face API
    raw_output = call_hf_inference(prompt, max_tokens=512)

    # Parse suggestions
    lines = [l.strip() for l in raw_output.splitlines() if l.strip()]
    suggestions = []

    for line in lines:
        if line[0].isdigit() and (line[1:2] in [".", ")", "-", ":"]):
            # Remove leading number (e.g., "1.", "2)")
            cleaned = line.split(maxsplit=1)[1] if len(line.split(maxsplit=1)) > 1 else line
            suggestions.append(cleaned.strip())
        else:
            if len(suggestions) < 4:
                suggestions.append(line)

        if len(suggestions) >= 4:
            break

    # If still empty, fallback to chunks
    if not suggestions:
        chunks = [p.strip() for p in raw_output.split("\n\n") if p.strip()]
        suggestions = chunks[:4]

    return suggestions[:4]
