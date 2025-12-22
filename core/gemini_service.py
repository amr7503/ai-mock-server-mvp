import google.generativeai as genai
import json
import time


def configure_gemini(api_key):
    genai.configure(api_key=api_key)


def generate_response(schema, request_payload=None):
    model = genai.GenerativeModel("models/gemini-flash-latest")

    prompt = f"""
You are an expert API mock generator.
Generate ONLY JSON. No explanation.

Follow this schema strictly:
{schema}

Rules:
- Must be valid JSON
- Must match field types
- Use realistic values
- Do NOT add extra fields
- If relationships exist, keep them consistent
"""

    if request_payload:
        prompt += f"\nRequest Body Context:\n{request_payload}\n"

    start = time.time()
    response = model.generate_content(prompt)
    latency = (time.time() - start) * 1000

    try:
        return json.loads(response.text), latency
    except:
        return response.text, latency
