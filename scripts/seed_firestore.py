from google.cloud import firestore

# HARDCODED PROJECT ID as string literal (required for Vertex AI Agent Platform)
PROJECT_ID = "qwiklabs-gcp-03-59f89a78fde9"
COLLECTION_NAME = "tax_case_studies"

print(f"Connecting to Firestore database for project '{PROJECT_ID}'...")
db = firestore.Client(project=PROJECT_ID)

SEED_CASE_STUDIES = [
    {
        "id": "cs_1065_001",
        "title": "Form 1065: Guaranteed Payments vs. Special Allocations",
        "form_type": "1065",
        "difficulty": "intermediate",
        "topic": "Schedule K-1 & Guaranteed Payments",
        "scenario_description": (
            "Partnership AB has two equal 50% partners, Alex and Blake. "
            "In 2025, Partnership AB generated $200,000 of gross ordinary trade or business income "
            "and incurred $50,000 in operating expenses. "
            "Under the partnership agreement, Alex receives a guaranteed payment of $40,000 for services "
            "rendered to the partnership, regardless of net partnership income."
        ),
        "key_question": "What is the net ordinary business income (Form 1065, Page 1, Line 22) and what amounts appear on Alex's Schedule K-1?",
        "solution_key": (
            "1. Gross income = $200,000. Deductions = $50,000 operating expenses + $40,000 guaranteed payment = $90,000.\n"
            "2. Form 1065, Page 1, Line 22 Ordinary Business Income = $110,000 ($200,000 - $90,000).\n"
            "3. Alex's Schedule K-1: Line 1 Ordinary Business Income (50%) = $55,000. Line 4c Guaranteed Payments = $40,000.\n"
            "4. Alex reports $95,000 total income on Form 1040 ($55,000 ordinary share + $40,000 guaranteed payment subject to SE tax)."
        ),
    },
    {
        "id": "cs_1120_001",
        "title": "Form 1120: Schedule M-1 Book-to-Tax Reconciliation",
        "form_type": "1120",
        "difficulty": "advanced",
        "topic": "Schedule M-1 Reconciliation",
        "scenario_description": (
            "Apex Corporation (a C Corp with $5 million in total assets) reports net book income of $500,000 on its financial statements. "
            "Book expenses include $15,000 in officer life insurance premiums (Apex is beneficiary), $20,000 in business meals ($10,000 nondeductible 50% limit), "
            "and $30,000 in federal income tax expense. Apex also received $12,000 in tax-exempt municipal bond interest."
        ),
        "key_question": "Calculate Apex Corporation's taxable income on Form 1120, Line 28, and detail the Schedule M-1 reconciliation items.",
        "solution_key": (
            "1. Net income per books = $500,000.\n"
            "2. Additions (Schedule M-1): Federal income tax expense ($30,000) + Key-man life insurance ($15,000) + 50% Nondeductible meals ($10,000) = $55,000.\n"
            "3. Subtractions (Schedule M-1): Tax-exempt municipal interest ($12,000).\n"
            "4. Taxable income before NOL/special deductions (Form 1120, Line 28) = $500,000 + $55,000 - $12,000 = $543,000."
        ),
    },
    {
        "id": "cs_1120s_001",
        "title": "Form 1120-S: Schedule M-2 Accumulated Adjustments Account (AAA) Sourcing",
        "form_type": "1120-S",
        "difficulty": "advanced",
        "topic": "AAA Account & Distributions",
        "scenario_description": (
            "S-Corp Zeta begins 2025 with an AAA balance of $30,000 and Accumulated Earnings & Profits (AE&P from prior C Corp years) of $15,000. "
            "During 2025, Zeta earns $25,000 in ordinary business income and makes a cash distribution of $40,000 to its sole shareholder, Chris."
        ),
        "key_question": "Determine the year-end AAA balance and the tax treatment of Chris's $40,000 distribution.",
        "solution_key": (
            "1. AAA Adjustment Order: Beginning AAA ($30,000) + 2025 Ordinary Income ($25,000) = $55,000 available AAA prior to distributions.\n"
            "2. Distribution Sourcing: The $40,000 distribution is fully covered by available AAA ($55,000) -> Tax-free return of basis to Chris.\n"
            "3. Ending AAA Balance = $55,000 - $40,000 = $15,000. AE&P remains untouched at $15,000."
        ),
    },
]

collection_ref = db.collection(COLLECTION_NAME)

for item in SEED_CASE_STUDIES:
    doc_id = item["id"]
    print(f"Seeding document '{doc_id}' into collection '{COLLECTION_NAME}'...")
    collection_ref.document(doc_id).set(item)

print("✅ Firestore seed complete!")
