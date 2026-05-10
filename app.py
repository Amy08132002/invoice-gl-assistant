"""
Invoice GL Coding Assistant — Streamlit App
Run with:  streamlit run app.py
"""

import streamlit as st
from llm_client import code_invoice, code_invoice_plain_prompt
from chart_of_accounts import CHART_OF_ACCOUNTS

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Invoice GL Coding Assistant",
    page_icon="🧾",
    layout="centered",
)

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.review-banner {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 12px 16px;
    border-radius: 4px;
    margin: 12px 0;
}
.clear-banner {
    background: #d4edda;
    border-left: 4px solid #28a745;
    padding: 12px 16px;
    border-radius: 4px;
    margin: 12px 0;
}
.gl-chip {
    display: inline-block;
    background: #e8f4fd;
    border: 1px solid #bee3f8;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 1.05em;
    font-weight: 600;
    color: #1a6496;
}
.conf-high { color: #28a745; font-weight: 600; }
.conf-medium { color: #fd7e14; font-weight: 600; }
.conf-low { color: #dc3545; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🧾 Invoice GL Coding Assistant")
st.caption("First-pass GL account recommendations for junior accountants · Powered by Claude")
st.divider()

# ── Sidebar: Chart of Accounts Reference ─────────────────────────────────────
with st.sidebar:
    st.subheader("📋 Chart of Accounts")
    for acct in CHART_OF_ACCOUNTS:
        st.markdown(f"**{acct['gl_code']}** — {acct['account_name']}")
        st.caption(acct["description"])
    st.divider()
    st.caption("This tool provides first-pass recommendations only. "
               "Always confirm GL codes with your supervisor or a senior accountant.")

# ── Tabs: Single Invoice / Compare Mode ──────────────────────────────────────
tab_main, tab_compare, tab_about = st.tabs(["Code an Invoice", "Compare Modes", "About"])

# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — Main Invoice Form
# ────────────────────────────────────────────────────────────────────────────
with tab_main:
    st.subheader("Enter Invoice Details")

    col1, col2 = st.columns([3, 1])
    with col1:
        vendor = st.text_input("Vendor Name *", placeholder="e.g., Zoom Video Communications")
    with col2:
        amount = st.number_input("Amount ($) *", min_value=0.01, value=100.00, step=0.01, format="%.2f")

    description = st.text_area(
        "Invoice Description *",
        placeholder="e.g., Annual Pro subscription renewal – 10 host licenses",
        height=90
    )
    notes = st.text_input("Notes (optional)", placeholder="e.g., Auto-renewed, asset tag pending")

    submitted = st.button("🔍 Get GL Recommendation", type="primary", use_container_width=True)

    if submitted:
        if not vendor.strip() or not description.strip():
            st.warning("Please fill in at least the vendor name and description.")
        else:
            with st.spinner("Analyzing invoice…"):
                result = code_invoice(
                    vendor=vendor.strip(),
                    description=description.strip(),
                    amount=amount,
                    notes=notes.strip(),
                )

            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.divider()
                st.subheader("Recommendation")

                # Human review banner
                if result.get("needs_human_review"):
                    st.markdown(
                        '<div class="review-banner">⚠️ <strong>Human Review Recommended</strong> — '
                        'This invoice has ambiguous details. Please verify before posting.</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div class="clear-banner">✅ <strong>Straightforward Case</strong> — '
                        'Recommendation appears clear, but always sanity-check before posting.</div>',
                        unsafe_allow_html=True
                    )

                # GL account display
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("GL Account", result.get("recommended_gl_account", "—"))
                with col_b:
                    st.metric("Account Name", result.get("account_name", "—"))
                with col_c:
                    conf = result.get("confidence", "—").capitalize()
                    st.metric("Confidence", conf)

                st.markdown(f"**Category:** {result.get('expense_category', '—')}")
                st.markdown("**Reasoning:**")
                st.info(result.get("reason", "No reason provided."))

                # Raw JSON expander
                with st.expander("Show raw JSON output"):
                    st.json(result)

# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — Compare: Full System vs. Plain Prompt
# ────────────────────────────────────────────────────────────────────────────
with tab_compare:
    st.subheader("Compare: Full System vs. Plain Prompt Baseline")
    st.caption(
        "Run the same invoice through both the context-engineered system and a simple "
        "plain-prompt baseline to see the difference in output quality."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        cmp_vendor = st.text_input("Vendor Name", placeholder="e.g., Smith & Associates LLP", key="cmp_vendor")
    with col2:
        cmp_amount = st.number_input("Amount ($)", min_value=0.01, value=500.00, step=0.01, format="%.2f", key="cmp_amount")

    cmp_desc = st.text_area("Description", placeholder="e.g., Monthly services – March", height=80, key="cmp_desc")
    cmp_notes = st.text_input("Notes (optional)", key="cmp_notes")

    cmp_btn = st.button("⚡ Run Comparison", type="secondary", use_container_width=True)

    if cmp_btn:
        if not cmp_vendor.strip() or not cmp_desc.strip():
            st.warning("Please fill in vendor and description.")
        else:
            col_sys, col_base = st.columns(2)

            with col_sys:
                st.markdown("### 🎯 Full System")
                with st.spinner("Running full system…"):
                    sys_res = code_invoice(
                        vendor=cmp_vendor.strip(),
                        description=cmp_desc.strip(),
                        amount=cmp_amount,
                        notes=cmp_notes.strip(),
                    )
                if "error" in sys_res:
                    st.error(sys_res["error"])
                else:
                    st.metric("GL Account", sys_res.get("recommended_gl_account", "—"))
                    st.metric("Account Name", sys_res.get("account_name", "—"))
                    st.metric("Confidence", sys_res.get("confidence", "—").capitalize())
                    flag = "⚠️ Yes" if sys_res.get("needs_human_review") else "✅ No"
                    st.metric("Needs Review", flag)
                    st.markdown(f"**Reason:** {sys_res.get('reason', '—')}")

            with col_base:
                st.markdown("### 📝 Plain Prompt Baseline")
                with st.spinner("Running baseline…"):
                    base_res = code_invoice_plain_prompt(
                        vendor=cmp_vendor.strip(),
                        description=cmp_desc.strip(),
                        amount=cmp_amount,
                        notes=cmp_notes.strip(),
                    )
                if "error" in base_res:
                    st.error(base_res["error"])
                else:
                    st.markdown(
                        "_Free-form response — no GL codes, no structured fields, "
                        "no escalation logic:_"
                    )
                    st.text_area("Raw output", value=base_res.get("raw_text", ""), height=200,
                                 disabled=True, key="base_out")

# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — About
# ────────────────────────────────────────────────────────────────────────────
with tab_about:
    st.subheader("About This Tool")
    st.markdown("""
**Invoice GL Coding Assistant** is a GenAI application built for a graduate course project 
(BU.350.790 / BU.330.760 — Applied AI for Business).

**What it does**

A junior accountant enters vendor invoice details (vendor name, description, amount, notes). 
The system returns a structured GL account recommendation from the company's chart of accounts, 
including a plain-language reason and a flag for cases that need human review before posting.

**Key design choices**

| Choice | Detail |
|---|---|
| Single LLM call | No agents, no RAG, no multi-step chains |
| Context engineering | Role definition, chart of accounts, 6 few-shot examples, output schema |
| Structured output | Fixed JSON fields; low temperature (0.0) for consistency |
| Escalation logic | `needs_human_review` flag set when confidence is low or description is ambiguous |

**Baseline comparison**

The Compare tab runs both the full system and a plain-prompt baseline (no chart of accounts, 
no examples, no structured output) on the same invoice so you can see the quality difference directly.

**Limitations**

- Uses a synthetic chart of accounts (17 GL codes). Real companies have hundreds.
- Cannot split invoices across multiple GL codes in one call.
- May be overconfident when vendor names are misleading.
- Not a substitute for final human review — all output should be verified before journal entry.

**Data**

All test data is synthetic. No real invoices, PII, or internal financial records were used.
    """)
