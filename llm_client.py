"""
LLM call wrapper for the Invoice GL Coding Assistant.
Uses Google Gemini API.
"""

import json
import os
import google.generativeai as genai
from prompts import build_system_prompt, build_user_message


def get_client():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)


def code_invoice(vendor, description, amount, notes="", model="gemini-2.5-flash", temperature=0.0):
    get_client()
    system_prompt = build_system_prompt()
    user_msg = build_user_message(vendor, description, amount, notes)
    full_prompt = system_prompt + "\n\n" + user_msg + "\n\nIMPORTANT: Reply with ONLY a JSON object, no other text."

    try:
        m = genai.GenerativeModel(model_name=model)
        response = m.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=2048,
                response_mime_type="application/json",
            )
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON: {e}"}
    except Exception as e:
        return {"error": str(e)}


def code_invoice_plain_prompt(vendor, description, amount, notes="", model="gemini-2.5-flash"):
    get_client()
    plain_prompt = (
        "You are an accounting assistant. Given invoice details, "
        "suggest an appropriate general ledger account category.\n\n"
        + build_user_message(vendor, description, amount, notes)
    )
    try:
        m = genai.GenerativeModel(model_name=model)
        response = m.generate_content(plain_prompt)
        return {"raw_text": response.text.strip()}
    except Exception as e:
        return {"error": str(e)}