RISK_WEIGHTS = {
    "PHISHING": 30,
    "FRAUD": 35,
    "MALWARE": 40,
    "EXTORTION": 50,
}

ENTITY_RISK = {
    "URL": 10,
    "EMAIL": 10,
    "IPV4": 15,
    "malware": 25,
    "attack-pattern": 20,
    "threat-actor": 30,
}

def calculate_risk(scam_type, entities):
    score = RISK_WEIGHTS.get(scam_type, 5)

    for ent in entities:
        score += ENTITY_RISK.get(ent, 5)

    return {
        "risk_score": min(score, 100),
        "risk_level": (
            "LOW" if score < 30 else
            "MEDIUM" if score < 60 else
            "HIGH"
        )
    }
