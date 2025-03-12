def get_drug_info(drug_name: str) -> dict:
    """
    Get information about a drug.
    This is a simple implementation that returns basic information.
    In a production environment, this would connect to a proper drug database.
    """
    # Dictionary mapping common drugs to their information
    drug_database = {
        "aspirin": {
            "name": "Aspirin",
            "generic_name": "Acetylsalicylic acid",
            "drug_class": "Nonsteroidal anti-inflammatory drug (NSAID)",
            "description": "A common pain reliever and fever reducer that also has anti-inflammatory properties.",
            "common_uses": [
                "Pain relief",
                "Fever reduction",
                "Prevention of heart attacks and strokes",
                "Reduction of inflammation"
            ],
            "typical_dosage": [
                "Adult pain/fever: 325-650mg every 4-6 hours",
                "Heart attack prevention: 81-325mg daily",
                "Maximum daily dose: 4,000mg"
            ],
            "side_effects": [
                "Stomach upset or pain",
                "Heartburn",
                "Nausea",
                "Easy bruising or bleeding",
                "Ringing in ears (with high doses)"
            ],
            "warnings": [
                "May cause stomach bleeding",
                "Avoid if allergic to NSAIDs",
                "Consult doctor before use if pregnant",
                "Do not give to children/teenagers with flu symptoms",
                "Consult healthcare provider before long-term use"
            ]
        },
        "ibuprofen": {
            "name": "Ibuprofen",
            "generic_name": "Ibuprofen",
            "drug_class": "Nonsteroidal anti-inflammatory drug (NSAID)",
            "description": "An over-the-counter pain reliever and fever reducer with anti-inflammatory properties.",
            "common_uses": [
                "Pain relief",
                "Fever reduction",
                "Treatment of inflammation",
                "Menstrual cramp relief"
            ],
            "typical_dosage": [
                "Adult pain/fever: 200-400mg every 4-6 hours",
                "Anti-inflammatory: 400-800mg 3-4 times daily",
                "Maximum daily dose: 3,200mg"
            ],
            "side_effects": [
                "Stomach pain or upset",
                "Heartburn",
                "Nausea",
                "Dizziness",
                "Mild headache"
            ],
            "warnings": [
                "May increase risk of heart attack or stroke",
                "Can cause stomach bleeding",
                "Avoid if allergic to NSAIDs",
                "Use lowest effective dose",
                "Consult healthcare provider before long-term use"
            ]
        }
    }

    drug_name = drug_name.strip().lower()

    # If drug is in our database, return its information
    if drug_name in drug_database:
        return drug_database[drug_name]

    # For drugs not in our database, return a template with placeholder info
    return {
        "name": drug_name.capitalize(),
        "generic_name": drug_name.capitalize(),
        "drug_class": "Information not available",
        "description": f"Detailed information about {drug_name.capitalize()} is not available in our database.",
        "common_uses": [
            "Please consult your healthcare provider for specific usage information"
        ],
        "typical_dosage": [
            "Please consult your healthcare provider for proper dosing information"
        ],
        "side_effects": [
            "Please consult your healthcare provider for information about side effects"
        ],
        "warnings": [
            "Always consult your healthcare provider before taking any medication",
            "Follow prescribed dosage instructions carefully",
            "Report any adverse reactions to your healthcare provider"
        ]
    }