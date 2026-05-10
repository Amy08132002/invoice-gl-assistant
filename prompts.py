"""
Prompt engineering for the Invoice GL Coding Assistant.
Contains the system prompt, few-shot examples, and output schema.
"""

from chart_of_accounts import get_coa_text

FEW_SHOT_EXAMPLES = [
    {
        "input": {
            "vendor": "Office Depot",
            "description": "Copy paper (case of 10 reams), ballpoint pens (box of 12), manila folders",
            "amount": 87.43,
            "notes": ""
        },
        "output": {
            "recommended_gl_account": "6010",
            "account_name": "Office Supplies",
            "expense_category": "Operating Expense",
            "reason": "Invoice is from a well-known office supply retailer and the items listed—copy paper, pens, and folders—are standard consumable office materials.",
            "confidence": "high",
            "needs_human_review": False
        }
    },
    {
        "input": {
            "vendor": "Zoom Video Communications",
            "description": "Annual Pro subscription renewal – 10 host licenses",
            "amount": 1499.90,
            "notes": "Auto-renewed on 2024-03-01"
        },
        "output": {
            "recommended_gl_account": "6020",
            "account_name": "Computer & Software Subscriptions",
            "expense_category": "Technology Expense",
            "reason": "Zoom is a SaaS video conferencing platform. An annual multi-seat subscription is a recurring software license fee.",
            "confidence": "high",
            "needs_human_review": False
        }
    },
    {
        "input": {
            "vendor": "Delta Air Lines",
            "description": "Round-trip airfare – Chicago to New York – J. Martinez – Client visit",
            "amount": 412.00,
            "notes": "Travel dates: April 14-16"
        },
        "output": {
            "recommended_gl_account": "6110",
            "account_name": "Travel & Transportation",
            "expense_category": "Travel Expense",
            "reason": "Airfare for a named employee traveling for client business is a clear travel and transportation expense.",
            "confidence": "high",
            "needs_human_review": False
        }
    },
    {
        "input": {
            "vendor": "WeWork",
            "description": "Monthly coworking membership – April 2024 – 4 desks",
            "amount": 2400.00,
            "notes": ""
        },
        "output": {
            "recommended_gl_account": "6210",
            "account_name": "Rent & Occupancy",
            "expense_category": "Facilities Expense",
            "reason": "WeWork is a coworking space provider. A monthly membership fee for desks is effectively office rent.",
            "confidence": "high",
            "needs_human_review": False
        }
    },
    {
        "input": {
            "vendor": "Smith & Associates LLP",
            "description": "Monthly services – March",
            "amount": 3500.00,
            "notes": ""
        },
        "output": {
            "recommended_gl_account": "6310",
            "account_name": "Professional Services",
            "expense_category": "Professional Expense",
            "reason": "The vendor name suggests a professional services firm (likely legal or accounting), but the description 'monthly services' is too vague to confirm. Categorized as Professional Services based on vendor pattern, but the actual nature of services should be verified.",
            "confidence": "medium",
            "needs_human_review": True
        }
    },
    {
        "input": {
            "vendor": "Amazon Business",
            "description": "Mixed order: USB hub x2, coffee pods (box of 48), HDMI cable, desk organizer",
            "amount": 156.22,
            "notes": "Single invoice for multiple item types"
        },
        "output": {
            "recommended_gl_account": "9999",
            "account_name": "Miscellaneous / Unclassified",
            "expense_category": "Other",
            "reason": "This invoice contains both technology accessories (USB hub, HDMI cable) and kitchen/breakroom supplies (coffee pods) and general supplies (desk organizer). It spans multiple GL categories and cannot be cleanly assigned to one account without splitting.",
            "confidence": "low",
            "needs_human_review": True
        }
    },
]


def _format_examples() -> str:
    lines = []
    for i, ex in enumerate(FEW_SHOT_EXAMPLES, 1):
        inp = ex["input"]
        out = ex["output"]
        lines.append(f"--- Example {i} ---")
        lines.append(f"Vendor: {inp['vendor']}")
        lines.append(f"Description: {inp['description']}")
        lines.append(f"Amount: ${inp['amount']:.2f}")
        lines.append(f"Notes: {inp['notes'] or '(none)'}")
        lines.append("Output:")
        lines.append(f"  recommended_gl_account: {out['recommended_gl_account']}")
        lines.append(f"  account_name: {out['account_name']}")
        lines.append(f"  expense_category: {out['expense_category']}")
        lines.append(f"  reason: {out['reason']}")
        lines.append(f"  confidence: {out['confidence']}")
        lines.append(f"  needs_human_review: {str(out['needs_human_review']).lower()}")
        lines.append("")
    return "\n".join(lines)


def build_system_prompt() -> str:
    coa = get_coa_text()
    examples = _format_examples()
    return f"""You are an accounting assistant that helps junior accountants assign general ledger (GL) accounts to vendor invoices. Your job is to review invoice information and recommend the most appropriate GL account from the company's chart of accounts.

CHART OF ACCOUNTS:
{coa}

YOUR TASK:
Given an invoice's vendor name, description, amount, and any notes, recommend the best GL account. Always explain your reasoning in plain language that a junior accountant can understand.

RULES:
1. Only recommend accounts from the chart of accounts above. Do not invent new accounts.
2. If an invoice clearly fits one account, assign it with high confidence.
3. If the description is vague, the vendor name and description conflict, or the invoice spans multiple categories, set confidence to "medium" or "low" and set needs_human_review to true.
4. If you genuinely cannot determine the right account, use GL 9999 (Miscellaneous / Unclassified) and flag for human review.
5. Keep the reason field concise (2-4 sentences). Write as if explaining to a new accountant.
6. Never guess or fabricate invoice details that were not provided.

FEW-SHOT EXAMPLES:
{examples}

OUTPUT FORMAT:
You must respond with a JSON object only. No markdown, no extra text, no code fences. Use exactly these fields:
{{
  "recommended_gl_account": "<4-digit code>",
  "account_name": "<account name from chart>",
  "expense_category": "<category from chart>",
  "reason": "<plain-language explanation>",
  "confidence": "<high | medium | low>",
  "needs_human_review": <true | false>
}}"""


def build_user_message(vendor: str, description: str, amount: float, notes: str) -> str:
    return f"""Please code the following invoice:

Vendor: {vendor}
Description: {description}
Amount: ${amount:.2f}
Notes: {notes if notes.strip() else '(none)'}"""
