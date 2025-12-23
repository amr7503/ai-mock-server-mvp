import google.generativeai as genai
import json
import time
import re

def configure_gemini(api_key):
    genai.configure(api_key=api_key)


def clean_json(text):
    """
    Removes ```json ``` fences or other markdown noise
    Extracts pure JSON string.
    """
    # Remove triple backticks + json tags
    text = re.sub(r"```json|```", "", text)
    text = text.strip()

    # Try to extract only the JSON part
    match = re.search(r"\{[\s\S]*\}|\[[\s\S]*\]", text)
    if match:
        return match.group(0)

    return text


def generate_response(schema, request_payload=None):
    model = genai.GenerativeModel(
        "models/gemini-flash-latest",
        generation_config={
            "temperature": 0.4,
            "response_mime_type": "application/json"
        }
    )

    prompt = f"""
You are an API mock generator.
STRICT RULES:
- Output ONLY valid JSON
- No explanation
- No code fences
- No markdown
- Must strictly follow this schema:

{schema}

Generate realistic, production-like values.
"""

    if request_payload and request_payload.strip() != "{}":
        prompt += f"\nRequest Body Context:\n{request_payload}\n"

    start = time.time()
    response = model.generate_content(prompt)
    latency = (time.time() - start) * 1000

    text = response.text
    text = clean_json(text)

    try:
        return json.loads(text), latency
    except Exception as e:
        # return raw for debugging if needed
        return {"error": "JSON parse failed", "raw": text, "reason": str(e)}, latency
