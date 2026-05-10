"""
Evaluation script for the Invoice GL Coding Assistant.
Runs the full test set and computes accuracy metrics vs. a plain-prompt baseline.

Usage:
    python evaluate.py [--mode full|quick] [--output results.json]

    full  : runs all 25 test cases x2 (system + baseline) — costs ~50 API calls
    quick : runs first 10 test cases, system prompt only
"""

import argparse
import json
import time
from datetime import datetime

from test_set import TEST_INVOICES
from llm_client import code_invoice, code_invoice_plain_prompt


CONFIDENCE_TO_REVIEW = {"low": True, "medium": True, "high": False}


def evaluate_result(result: dict, expected: dict) -> dict:
    """Score a single result against expected labels."""
    if "error" in result:
        return {"gl_correct": False, "category_correct": False, "review_correct": False,
                "structured": False, "error": result["error"]}

    gl_correct = result.get("recommended_gl_account") == expected["expected_gl"]
    cat_correct = result.get("expense_category") == expected["expected_category"]
    review_correct = bool(result.get("needs_human_review")) == expected["expected_review"]
    structured = all(k in result for k in [
        "recommended_gl_account", "account_name", "expense_category",
        "reason", "confidence", "needs_human_review"
    ])

    return {
        "gl_correct": gl_correct,
        "category_correct": cat_correct,
        "review_correct": review_correct,
        "structured": structured,
        "error": None
    }


def run_evaluation(cases, run_baseline=True, delay=0.5):
    records = []
    for case in cases:
        print(f"  [{case['id']}] {case['label'][:50]}...")

        # Full system
        sys_result = code_invoice(
            vendor=case["vendor"],
            description=case["description"],
            amount=case["amount"],
            notes=case.get("notes", ""),
        )
        sys_scores = evaluate_result(sys_result, case)
        time.sleep(delay)

        # Baseline
        base_result = {}
        base_scores = {}
        if run_baseline:
            base_result = code_invoice_plain_prompt(
                vendor=case["vendor"],
                description=case["description"],
                amount=case["amount"],
                notes=case.get("notes", ""),
            )
            # Baseline is unstructured – just record whether it errors
            base_scores = {
                "gl_correct": False,  # can't reliably parse free-form text
                "category_correct": False,
                "review_correct": False,
                "structured": False,
                "error": base_result.get("error")
            }
            time.sleep(delay)

        records.append({
            "id": case["id"],
            "label": case["label"],
            "input": {
                "vendor": case["vendor"],
                "description": case["description"],
                "amount": case["amount"],
                "notes": case.get("notes", "")
            },
            "expected": {
                "gl": case["expected_gl"],
                "category": case["expected_category"],
                "needs_review": case["expected_review"]
            },
            "system_result": sys_result,
            "system_scores": sys_scores,
            "baseline_result": base_result,
            "baseline_scores": base_scores,
        })

    return records


def summarize(records):
    total = len(records)
    sys_gl = sum(1 for r in records if r["system_scores"].get("gl_correct"))
    sys_cat = sum(1 for r in records if r["system_scores"].get("category_correct"))
    sys_rev = sum(1 for r in records if r["system_scores"].get("review_correct"))
    sys_struct = sum(1 for r in records if r["system_scores"].get("structured"))
    sys_errors = sum(1 for r in records if r["system_scores"].get("error"))

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total test cases     : {total}")
    print(f"\n── Full System (context-engineered + structured output) ──")
    print(f"  GL account correct : {sys_gl}/{total} ({100*sys_gl/total:.0f}%)")
    print(f"  Category correct   : {sys_cat}/{total} ({100*sys_cat/total:.0f}%)")
    print(f"  Review flag correct: {sys_rev}/{total} ({100*sys_rev/total:.0f}%)")
    print(f"  Structured output  : {sys_struct}/{total} ({100*sys_struct/total:.0f}%)")
    print(f"  Errors             : {sys_errors}")

    # Breakdown by ambiguity
    clear_cases = [r for r in records if "clear" in r["label"].lower()]
    ambig_cases = [r for r in records if r not in clear_cases]
    if clear_cases:
        c_gl = sum(1 for r in clear_cases if r["system_scores"].get("gl_correct"))
        print(f"\n  Clear cases ({len(clear_cases)}):  GL {c_gl}/{len(clear_cases)} correct")
    if ambig_cases:
        a_gl = sum(1 for r in ambig_cases if r["system_scores"].get("gl_correct"))
        a_esc = sum(1 for r in ambig_cases if r["system_scores"].get("review_correct"))
        print(f"  Ambiguous cases ({len(ambig_cases)}): GL {a_gl}/{len(ambig_cases)} correct, "
              f"escalation {a_esc}/{len(ambig_cases)} correct")

    print("\n── Failures ──")
    for r in records:
        if not r["system_scores"].get("gl_correct"):
            got = r["system_result"].get("recommended_gl_account", "ERR")
            exp = r["expected"]["gl"]
            conf = r["system_result"].get("confidence", "?")
            print(f"  [{r['id']}] {r['label'][:40]:<40}  got={got} exp={exp} conf={conf}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "quick"], default="quick")
    parser.add_argument("--output", default="eval_results.json")
    parser.add_argument("--no-baseline", action="store_true")
    args = parser.parse_args()

    cases = TEST_INVOICES if args.mode == "full" else TEST_INVOICES[:10]
    run_baseline = not args.no_baseline

    print(f"Running evaluation: {len(cases)} cases, baseline={'yes' if run_baseline else 'no'}")
    records = run_evaluation(cases, run_baseline=run_baseline)
    summarize(records)

    output = {
        "timestamp": datetime.now().isoformat(),
        "mode": args.mode,
        "records": records
    }
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nFull results saved to {args.output}")


if __name__ == "__main__":
    main()
