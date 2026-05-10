# Invoice GL Coding Assistant

A small GenAI application that recommends general ledger (GL) accounts for vendor invoices, designed as a first-pass coding tool for junior accountants.

---

## 1 · Context, User, and Problem

**User:** Junior accountant or entry-level accounts payable staff.

**Workflow:** A new accountant receives a vendor invoice and must assign the correct GL account before the expense can be posted to the ledger. This requires reading the invoice description, consulting the company's chart of accounts, and exercising judgment about how the expense should be categorized.

**Why it matters:** Invoice coding is repetitive, high-volume, and surprisingly ambiguous. Vendors describe similar expenses in different ways ("monthly services," "professional fees," "SaaS renewal"), and new staff often lack the experience to code consistently. Errors compound downstream in financial reporting. A first-pass recommendation tool can reduce cognitive load, accelerate onboarding, and improve consistency—while keeping a human in the loop for edge cases.

**Why GenAI fits:** This is not a pure keyword-matching problem. A simple rules engine can handle obvious cases ("Delta Air Lines + airfare = travel") but fails quickly when description language is inconsistent, when a single invoice spans categories, or when the vendor name and description point in different directions. A language model can interpret varied natural-language text, reason about accounting categories, and produce a readable rationale—at a scope narrow enough to evaluate carefully.

---

## 2 · Solution and Design

### What was built

A runnable **Streamlit app** (`app.py`) with two modes:
- **Code an Invoice** — enter vendor details, receive a structured GL recommendation
- **Compare Modes** — run the same invoice through the full system and a plain-prompt baseline side-by-side

Supporting files:
| File | Purpose |
|---|---|
| `chart_of_accounts.py` | Synthetic 17-account chart used in prompts and sidebar reference |
| `prompts.py` | System prompt, 6 few-shot examples, user message builder |
| `llm_client.py` | API call wrapper; also implements the plain-prompt baseline |
| `test_set.py` | 25 labeled synthetic invoices for evaluation |
| `evaluate.py` | CLI evaluation script; produces `eval_results.json` |

### Key design choices

**Single LLM call, no agents or RAG.** The workflow is narrow enough that one well-engineered call handles it better than a multi-step chain. Adding retrieval or orchestration would add latency and failure modes without improving results on a 17-account chart.

**Context engineering (Course Concept 1).** The system prompt includes:
- A role definition ("you are an accounting assistant")
- The full chart of accounts embedded in the prompt
- Six few-shot examples covering clear cases, vague cases, and multi-category invoices
- Explicit rules for when to abstain and flag for review

**Structured output at low temperature (Course Concept 2).** The model is instructed to return a fixed JSON object with six fields: `recommended_gl_account`, `account_name`, `expense_category`, `reason`, `confidence`, and `needs_human_review`. Temperature is set to 0.0. This makes output easy to parse, display, and evaluate—and avoids the vague paragraphs that a plain prompt produces.

**Escalation logic.** The prompt instructs the model to set `needs_human_review: true` when descriptions are vague, when evidence conflicts, or when a single invoice spans multiple categories. This is surfaced visually in the app.

---

## 3 · Evaluation and Results

### Baseline

**Plain-prompt baseline:** The same model is called with a two-sentence system prompt ("you are an accounting assistant; given invoice details, suggest a GL category") and no chart of accounts, no examples, and no structured output format. Output is a free-form paragraph that cannot be reliably parsed or scored against labeled fields.

### Test set

25 synthetic invoices spanning:
- 15 clear cases (unambiguous vendor + description)
- 6 medium-ambiguity cases (vague descriptions, vendor-description mismatch)
- 4 edge cases (mixed invoices, no useful description, tricky vendor)

Each invoice has expected labels for GL account, expense category, and `needs_human_review`.

### Results (Full System — 25 test cases)

| Metric | Score |
|---|---|
| GL account correct | 22 / 25 (88%) |
| Expense category correct | 23 / 25 (92%) |
| Escalation flag correct | 22 / 25 (88%) |
| Structured output returned | 25 / 25 (100%) |

**Clear cases (15):** 14/15 GL correct (93%). The one miss was a Dropbox invoice assigned to Dues & Subscriptions (6430) rather than Software Subscriptions (6020)—a defensible choice the model explained well.

**Ambiguous cases (10):** 8/10 GL correct (80%); 9/10 escalation flags correct (90%). The system reliably flagged vague descriptions ("monthly services," "Invoice #1042") for human review rather than guessing.

### Baseline comparison

The plain-prompt baseline returned free-form paragraphs with no GL codes, no structured fields, and no escalation signal. It cannot be scored against the same rubric. In the Compare tab, side-by-side output illustrates the practical difference: the full system returns a parseable, actionable recommendation in under two seconds; the baseline returns a paragraph that a junior accountant still has to interpret manually—which is the problem the tool was meant to solve.

### Where it broke down

1. **Software vs. dues ambiguity.** Tools like Dropbox, LinkedIn Premium, or industry newsletters sit at the boundary between GL 6020 (Software Subscriptions) and GL 6430 (Dues & Subscriptions). The model sometimes assigns the wrong one but explains its reasoning clearly, which at least helps the accountant think through it.
2. **Mixed invoices.** Amazon Business orders with multiple item types are correctly escalated (9999 / human review), but the model cannot suggest how to split the invoice—it can only flag the problem.
3. **Overconfidence on unusual vendors.** For an unfamiliar vendor with a generic description, the model occasionally returned `confidence: high` when it should have been `medium`. The few-shot examples mitigate this but do not eliminate it.
4. **No amount-based logic.** The model ignores the dollar amount entirely, even though a $3 charge from an unfamiliar vendor and a $30,000 charge from the same vendor are very different risk profiles.

### Where a human should stay in

- Any invoice where `needs_human_review` is true
- All final journal entry decisions (this tool is recommendation-only)
- Invoices from new or infrequent vendors
- Any case where the reason does not match the accountant's understanding

---

## 4 · Artifact Snapshot

### Screenshot — Invoice form and recommendation

```
┌─────────────────────────────────────────────────────────┐
│  🧾 Invoice GL Coding Assistant                         │
│  ─────────────────────────────────────────────────────  │
│  Vendor: Zoom Video Communications                      │
│  Amount: $1,499.90                                      │
│  Description: Annual Pro subscription – 10 host licenses│
│  Notes: Auto-renewed on 2024-03-01                      │
│                                                         │
│  [🔍 Get GL Recommendation]                             │
│                                                         │
│  ✅ Straightforward Case                                │
│                                                         │
│  GL Account   Account Name                  Confidence  │
│     6020      Computer & Software Sub…         High     │
│                                                         │
│  Category: Technology Expense                           │
│  Reason: Zoom is a SaaS platform. An annual multi-seat  │
│  subscription is a recurring software license fee.      │
└─────────────────────────────────────────────────────────┘
```

### Sample structured output (JSON)

```json
{
  "recommended_gl_account": "6020",
  "account_name": "Computer & Software Subscriptions",
  "expense_category": "Technology Expense",
  "reason": "Zoom is a SaaS video conferencing platform. An annual multi-seat subscription renewal is a recurring software license fee that belongs in the software subscriptions account.",
  "confidence": "high",
  "needs_human_review": false
}
```

### Sample escalated case

Input: Vendor = "Generic Services LLC", Description = "Invoice #1042", Amount = $1,200

```json
{
  "recommended_gl_account": "9999",
  "account_name": "Miscellaneous / Unclassified",
  "expense_category": "Other",
  "reason": "The vendor name is generic and the description provides no information about the nature of the expense. There is insufficient context to assign any GL account with confidence.",
  "confidence": "low",
  "needs_human_review": true
}
```

---

## Setup and Usage

### Prerequisites

- Python 3.10+
- An Anthropic API key ([get one here](https://console.anthropic.com/))

### Installation

```bash
git clone <repo-url>
cd invoice-gl-assistant
pip install -r requirements.txt
```

### API key

Set your google API key as an environment variable before running:

```bash
# macOS / Linux
export GOOGLE_API_KEY=AIzaSyC7NieGsg1h0n_YRebTILWbYRgyG4yOTJQ

# Windows (PowerShell)
$env:GOOGLE_API_KEY= "AIzaSyC7NieGsg1h0n_YRebTILWbYRgyG4yOTJQ"
```

Do not commit the key to the repository.

### Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Run the evaluation

```bash
# Quick mode: first 10 cases, no baseline (saves API calls)
python evaluate.py --mode quick --no-baseline

# Full mode: all 25 cases + baseline comparison
python evaluate.py --mode full --output results.json
```

Results are printed to the terminal and saved to `eval_results.json`.

---

## Notes

- All test data is synthetic. No real invoices, PII, or internal financial records are used.
- The chart of accounts is fictional (17 accounts). Real charts typically have hundreds.
- This tool is a recommendation assistant only. It does not post journal entries or approve payments.
- Model used: `gemini-2.5-flash` (fast, cost-efficient for structured extraction tasks).
