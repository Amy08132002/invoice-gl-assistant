"""
LLM call wrapper for the Invoice GL Coding Assistant.
Makes a single structured API call and returns a parsed result dict.
"""

import json
import os
import anthropic
from prompts import build_system_prompt, build_user_message


def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Please set it before running the app."
        )
    return anthropic.Anthropic(api_key=api_key)


def code_invoice(
    vendor: str,
    description: str,
    amount: float,
    notes: str = "",
    model: str = "claude-3-5-haiku-20241022",
    temperature: float = 0.0,
) -> dict:
    """
    Call the LLM and return a structured GL coding recommendation.

    Returns a dict with keys:
        recommended_gl_account, account_name, expense_category,
        reason, confidence, needs_human_review
    On error, returns a dict with an 'error' key.
    """
    client = get_client()
    system_prompt = build_system_prompt()
    user_msg = build_user_message(vendor, description, amount, notes)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=512,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown fences if model adds them despite instructions
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        result = json.loads(raw)
        return result
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse model output as JSON: {e}", "raw": raw}
    except Exception as e:
        return {"error": str(e)}


def code_invoice_plain_prompt(
    vendor: str,
    description: str,
    amount: float,
    notes: str = "",
    model: str = "claude-3-5-haiku-20241022",
) -> dict:
    """
    Weaker baseline: no few-shot examples, no structured output instruction,
    no chart of accounts. Returns dict with 'raw_text' key.
    """
    client = get_client()
    plain_system = (
        "You are an accounting assistant. Given invoice details, "
        "suggest an appropriate general ledger account category."
    )
    user_msg = build_user_message(vendor, description, amount, notes)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=256,
            system=plain_system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return {"raw_text": response.content[0].text.strip()}
    except Exception as e:
        return {"error": str(e)}
