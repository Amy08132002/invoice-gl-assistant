"""
Synthetic Chart of Accounts for the Invoice GL Coding Assistant.
These accounts are fictional and created solely for evaluation purposes.
"""

CHART_OF_ACCOUNTS = [
    {"gl_code": "6010", "account_name": "Office Supplies", "category": "Operating Expense",
     "description": "Paper, pens, printer ink, folders, and other consumable office materials"},
    {"gl_code": "6020", "account_name": "Computer & Software Subscriptions", "category": "Technology Expense",
     "description": "SaaS licenses, cloud software, productivity tools, antivirus, development tools"},
    {"gl_code": "6030", "account_name": "Computer Hardware & Equipment", "category": "Technology Expense",
     "description": "Laptops, monitors, keyboards, peripherals, servers, networking equipment"},
    {"gl_code": "6110", "account_name": "Travel & Transportation", "category": "Travel Expense",
     "description": "Airfare, train tickets, rideshare, taxis, mileage reimbursement, parking"},
    {"gl_code": "6120", "account_name": "Lodging & Accommodation", "category": "Travel Expense",
     "description": "Hotel stays, Airbnb, serviced apartments for business travel"},
    {"gl_code": "6130", "account_name": "Meals & Entertainment", "category": "Travel Expense",
     "description": "Business meals, team lunches, client dinners, coffee meetings"},
    {"gl_code": "6210", "account_name": "Rent & Occupancy", "category": "Facilities Expense",
     "description": "Office rent, coworking space fees, storage unit rental"},
    {"gl_code": "6220", "account_name": "Utilities", "category": "Facilities Expense",
     "description": "Electricity, gas, water, internet, phone service"},
    {"gl_code": "6310", "account_name": "Professional Services", "category": "Professional Expense",
     "description": "Legal fees, accounting, consulting, HR advisory, staffing agency fees"},
    {"gl_code": "6320", "account_name": "Marketing & Advertising", "category": "Marketing Expense",
     "description": "Ad spend, agency fees, printing/design for campaigns, sponsorships"},
    {"gl_code": "6330", "account_name": "Postage & Shipping", "category": "Operating Expense",
     "description": "FedEx, UPS, USPS, courier services, freight"},
    {"gl_code": "6410", "account_name": "Insurance", "category": "Administrative Expense",
     "description": "General liability, property, workers comp, D&O, cyber insurance premiums"},
    {"gl_code": "6420", "account_name": "Bank & Financial Charges", "category": "Administrative Expense",
     "description": "Wire fees, credit card processing, transaction fees, loan interest"},
    {"gl_code": "6430", "account_name": "Dues & Subscriptions", "category": "Administrative Expense",
     "description": "Professional association memberships, industry publications, non-software subscriptions"},
    {"gl_code": "6440", "account_name": "Training & Education", "category": "Administrative Expense",
     "description": "Courses, certifications, conferences, workshops, online learning platforms"},
    {"gl_code": "6510", "account_name": "Repairs & Maintenance", "category": "Facilities Expense",
     "description": "Office equipment repair, building maintenance, cleaning services"},
    {"gl_code": "9999", "account_name": "Miscellaneous / Unclassified", "category": "Other",
     "description": "Expenses that do not clearly fit any other category; requires human review"},
]


def get_coa_text() -> str:
    """Return chart of accounts as formatted text for inclusion in prompts."""
    lines = ["GL Code | Account Name | Category | Description"]
    lines.append("-" * 80)
    for acct in CHART_OF_ACCOUNTS:
        lines.append(f"{acct['gl_code']} | {acct['account_name']} | {acct['category']} | {acct['description']}")
    return "\n".join(lines)


def get_coa_dict() -> dict:
    """Return {gl_code: account_name} mapping."""
    return {a["gl_code"]: a["account_name"] for a in CHART_OF_ACCOUNTS}
