import re

ENTITY_COLORS = {
    "URL": "🔗",
    "EMAIL": "📧",
    "IPV4": "🌐",
    "malware": "🦠",
    "attack-pattern": "⚔️",
    "threat-actor": "👤",
}

def highlight_entities(text, entities):
    explanations = []
    for ent in entities:
        icon = ENTITY_COLORS.get(ent, "⚠️")
        explanations.append(f"{icon} {ent}")

    return {
        "highlighted_text": text,
        "entities_detected": explanations,
        "reason": "Multiple cyber threat indicators detected in content"
        if len(entities) >= 2 else "Single suspicious indicator detected"
    }
