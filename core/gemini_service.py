import google.generativeai as genai
import json
import time
import re


def configure_gemini(api_key):
    genai.configure(api_key=api_key)


def clean_json(text):
    text = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"\{[\s\S]*\}|\[[\s\S]*\]", text)
    return match.group(0) if match else text


def build_prompt(schema, method, request_payload=None, error_type=None):
    if error_type == "400":
        return "Generate a realistic API validation failure JSON response."
    if error_type == "404":
        return "Generate a realistic resource not found error JSON."
    if error_type == "500":
        return "Generate a realistic internal server error JSON."

    base = f"""
You are an API mock generator.
Return ONLY valid JSON. No markdown. No code fences.

STRICTLY follow this schema:
{schema}

Rules:
- JSON only
- No extra fields
- Realistic values
"""

    if method == "POST":
        base += "\nAction: Create a NEW resource."
    elif method == "PUT":
        base += "\nAction: Update EXISTING resource. Keep identifiers consistent."
    else:
        base += "\nAction: Provide realistic fetch response."

    if request_payload and request_payload.strip() != "{}":
        base += f"\nRequest Context:\n{request_payload}\n"

    return base


def generate_response(schema, method, request_payload=None, error_type=None):
    model = genai.GenerativeModel(
        "models/gemini-flash-latest",
        generation_config={
            "temperature": 0.5,
            "response_mime_type": "application/json"
        }
    )

    prompt = build_prompt(schema, method, request_payload, error_type)

    start = time.time()
    response = model.generate_content(prompt)
    latency = (time.time() - start) * 1000

    text = clean_json(response.text)

    try:
        return json.loads(text), latency
    except Exception as e:
        return {"error": "JSON parse failed", "raw": text, "reason": str(e)}, latency
