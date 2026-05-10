"""
Synthetic test set of 25 labeled invoices for evaluation.
Each entry has input fields and expected output for comparison.
"""

TEST_INVOICES = [
    # ── CLEAR CASES ──────────────────────────────────────────────────────────
    {
        "id": "T01",
        "vendor": "Staples",
        "description": "Sticky notes (12-pack), correction tape, black markers (box)",
        "amount": 34.17,
        "notes": "",
        "expected_gl": "6010",
        "expected_category": "Operating Expense",
        "expected_review": False,
        "label": "Office Supplies – clear"
    },
    {
        "id": "T02",
        "vendor": "Slack Technologies",
        "description": "Slack Pro – monthly billing – 25 users",
        "amount": 212.50,
        "notes": "",
        "expected_gl": "6020",
        "expected_category": "Technology Expense",
        "expected_review": False,
        "label": "Software subscription – clear"
    },
    {
        "id": "T03",
        "vendor": "Adobe Systems",
        "description": "Creative Cloud for Teams – annual renewal",
        "amount": 4800.00,
        "notes": "12-month license for 8 seats",
        "expected_gl": "6020",
        "expected_category": "Technology Expense",
        "expected_review": False,
        "label": "Software subscription – clear"
    },
    {
        "id": "T04",
        "vendor": "Apple Store",
        "description": "MacBook Pro 14-inch M3 – employee workstation",
        "amount": 1999.00,
        "notes": "Asset tag to be assigned",
        "expected_gl": "6030",
        "expected_category": "Technology Expense",
        "expected_review": False,
        "label": "Hardware – clear"
    },
    {
        "id": "T05",
        "vendor": "United Airlines",
        "description": "Airfare – SFO to ORD – Sarah Chen – Q2 sales conference",
        "amount": 387.00,
        "notes": "Travel date: May 7",
        "expected_gl": "6110",
        "expected_category": "Travel Expense",
        "expected_review": False,
        "label": "Airfare – clear"
    },
    {
        "id": "T06",
        "vendor": "Uber",
        "description": "Business rides – March 2024 – account #BZ-4421",
        "amount": 94.30,
        "notes": "",
        "expected_gl": "6110",
        "expected_category": "Travel Expense",
        "expected_review": False,
        "label": "Ground transport – clear"
    },
    {
        "id": "T07",
        "vendor": "Marriott Hotels",
        "description": "Hotel stay – 3 nights – T. Nguyen – client site visit",
        "amount": 567.00,
        "notes": "Check-in Apr 22, check-out Apr 25",
        "expected_gl": "6120",
        "expected_category": "Travel Expense",
        "expected_review": False,
        "label": "Lodging – clear"
    },
    {
        "id": "T08",
        "vendor": "Grubhub Corporate",
        "description": "Team lunch – product roadmap meeting – 12 people",
        "amount": 218.40,
        "notes": "Catered to office",
        "expected_gl": "6130",
        "expected_category": "Travel Expense",
        "expected_review": False,
        "label": "Meals – clear"
    },
    {
        "id": "T09",
        "vendor": "Regus",
        "description": "Private office rental – May 2024 – Floor 8, Suite 801",
        "amount": 1850.00,
        "notes": "",
        "expected_gl": "6210",
        "expected_category": "Facilities Expense",
        "expected_review": False,
        "label": "Rent – clear"
    },
    {
        "id": "T10",
        "vendor": "Con Edison",
        "description": "Electricity bill – April 2024 – Account 77-2291-004",
        "amount": 430.55,
        "notes": "",
        "expected_gl": "6220",
        "expected_category": "Facilities Expense",
        "expected_review": False,
        "label": "Utilities – clear"
    },
    {
        "id": "T11",
        "vendor": "Verizon Business",
        "description": "Monthly internet & phone service – May 2024",
        "amount": 289.00,
        "notes": "",
        "expected_gl": "6220",
        "expected_category": "Facilities Expense",
        "expected_review": False,
        "label": "Utilities – clear"
    },
    {
        "id": "T12",
        "vendor": "Baker McKenzie LLP",
        "description": "Legal services – contract review for vendor agreement",
        "amount": 4200.00,
        "notes": "Invoice #BM-20240412",
        "expected_gl": "6310",
        "expected_category": "Professional Expense",
        "expected_review": False,
        "label": "Legal / professional services – clear"
    },
    {
        "id": "T13",
        "vendor": "Google Ads",
        "description": "Advertising spend – April 2024 – Campaign: Spring Promo",
        "amount": 3120.00,
        "notes": "",
        "expected_gl": "6320",
        "expected_category": "Marketing Expense",
        "expected_review": False,
        "label": "Advertising – clear"
    },
    {
        "id": "T14",
        "vendor": "FedEx",
        "description": "Express shipping – 4 packages – client deliveries",
        "amount": 78.60,
        "notes": "",
        "expected_gl": "6330",
        "expected_category": "Operating Expense",
        "expected_review": False,
        "label": "Shipping – clear"
    },
    {
        "id": "T15",
        "vendor": "Coursera for Business",
        "description": "Annual team learning subscription – 15 licenses",
        "amount": 2250.00,
        "notes": "Includes data science and leadership tracks",
        "expected_gl": "6440",
        "expected_category": "Administrative Expense",
        "expected_review": False,
        "label": "Training – clear"
    },

    # ── MEDIUM AMBIGUITY ─────────────────────────────────────────────────────
    {
        "id": "T16",
        "vendor": "Amazon Business",
        "description": "Monthly services",
        "amount": 500.00,
        "notes": "",
        "expected_gl": "9999",
        "expected_category": "Other",
        "expected_review": True,
        "label": "Vague description – should escalate"
    },
    {
        "id": "T17",
        "vendor": "ABC Consulting Group",
        "description": "Professional fees – March",
        "amount": 7500.00,
        "notes": "",
        "expected_gl": "6310",
        "expected_category": "Professional Expense",
        "expected_review": True,
        "label": "Consulting – vague, medium confidence"
    },
    {
        "id": "T18",
        "vendor": "Whole Foods Market",
        "description": "Groceries and supplies",
        "amount": 312.88,
        "notes": "Team offsite – kitchen stocking",
        "expected_gl": "6130",
        "expected_category": "Travel Expense",
        "expected_review": True,
        "label": "Grocery / meals – ambiguous"
    },
    {
        "id": "T19",
        "vendor": "Best Buy Business",
        "description": "Monitor x2, office chair, HDMI cables x4, power strip",
        "amount": 1245.00,
        "notes": "",
        "expected_gl": "9999",
        "expected_category": "Other",
        "expected_review": True,
        "label": "Mixed invoice – hardware + furniture"
    },
    {
        "id": "T20",
        "vendor": "Dropbox Business",
        "description": "Annual plan – storage and collaboration",
        "amount": 960.00,
        "notes": "",
        "expected_gl": "6020",
        "expected_category": "Technology Expense",
        "expected_review": False,
        "label": "SaaS – could be 6020 or 6430"
    },

    # ── TRICKY / EDGE CASES ──────────────────────────────────────────────────
    {
        "id": "T21",
        "vendor": "Kwik Trip",
        "description": "Fuel and snacks",
        "amount": 67.40,
        "notes": "Road trip – client site visit",
        "expected_gl": "6110",
        "expected_category": "Travel Expense",
        "expected_review": True,
        "label": "Mixed travel expense – fuel + snacks"
    },
    {
        "id": "T22",
        "vendor": "Legalzoom",
        "description": "Business formation documents and registered agent service – annual",
        "amount": 399.00,
        "notes": "",
        "expected_gl": "6310",
        "expected_category": "Professional Expense",
        "expected_review": False,
        "label": "Legal services – less obvious vendor"
    },
    {
        "id": "T23",
        "vendor": "Brex",
        "description": "Card transaction fee – April 2024",
        "amount": 45.00,
        "notes": "",
        "expected_gl": "6420",
        "expected_category": "Administrative Expense",
        "expected_review": False,
        "label": "Financial charges – clear"
    },
    {
        "id": "T24",
        "vendor": "Generic Services LLC",
        "description": "Invoice #1042",
        "amount": 1200.00,
        "notes": "",
        "expected_gl": "9999",
        "expected_category": "Other",
        "expected_review": True,
        "label": "No useful info – should escalate"
    },
    {
        "id": "T25",
        "vendor": "Home Depot",
        "description": "Paint, brushes, drop cloths, light fixtures",
        "amount": 892.00,
        "notes": "Office renovation – landlord pre-approved",
        "expected_gl": "6510",
        "expected_category": "Facilities Expense",
        "expected_review": False,
        "label": "Repairs & maintenance – clear with context"
    },
]
