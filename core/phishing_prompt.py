def build_phishing_prompt(text: str) -> str:
    return f"""
You are a cybersecurity expert specializing in phishing and scam detection.

Classify the risk level of the following text.

Risk definitions:
- LOW: Normal or harmless content.
- MEDIUM: Suspicious intent, vague account-related requests, social engineering language, but no strong threat.
- HIGH: Clear phishing indicators such as urgency, threats, fake rewards, impersonation, or suspicious links.

Return ONLY valid JSON in this format:

{{
  "is_phishing": true or false,
  "risk_level": "low" | "medium" | "high",
  "confidence": number between 0 and 1,
  "reasons": [short reasons]
}}

Rules:
- Account-related requests without context should be MEDIUM risk.
- Urgency + account threat + link = HIGH risk.
- Ignore OCR/UI noise.

TEXT:
\"\"\"
{text}
\"\"\"
"""
