import json

def parse_groq_response(response_text: str):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {
            "is_phishing": False,
            "risk_level": "low",
            "confidence": 0.0,
            "reasons": ["Invalid LLM response"]
        }


def aggregate_results(results):
    if not results:
        return {
            "final_risk": "low",
            "confidence": 0.0,
            "reasons": []
        }

    risk_priority = {"low": 1, "medium": 2, "high": 3}

    final = max(results, key=lambda r: risk_priority.get(r["risk_level"], 1))

    return {
        "final_risk": final["risk_level"],
        "confidence": final["confidence"],
        "reasons": final["reasons"]
    }
