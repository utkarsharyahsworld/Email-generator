from app.llm.client import call_llm
from app.ml.intent_predictor import predict_intent

import json

CLASSIFIER_PROMPT = """
You are an intent classifier for an email automation system.

Extract and return ONLY valid JSON with fields:
- domain (education, hr, corporate, personal, other)
- email_type (fee_reminder, internship_status, application, request, announcement, other)
- sender_role (institute, hr, company, teacher, admin, individual)
- receiver_role (student, candidate, employee, team, individual)
- tone (formal, semi-formal, informal)

User description:
"{description}"
"""
INTENT_CONFIDENCE_THRESHOLD = 0.6

def classify_email_intent(description: str) -> dict:
    raw = call_llm(CLASSIFIER_PROMPT.format(description=description))

    try:
        return json.loads(raw)
    except Exception:
        # Production-safe fallback
        return {
            "domain": "other",
            "email_type": "other",
            "sender_role": "individual",
            "receiver_role": "individual",
            "tone": "formal"
        }

def infer_controls(description: str) -> dict:
    # Default safe controls (Phase 0 behaviour)
    controls = {
        "tone": "professional",
        "length": "medium",
        "recipient": "Recipient",
    }

    # --- Phase 1: ML-based intent detection ---
    try:
        intent, confidence = predict_intent(description)

        if confidence >= INTENT_CONFIDENCE_THRESHOLD:
            if intent == "HR_EMAIL":
                controls["recipient"] = "HR"
            elif intent == "MANAGER_EMAIL":
                controls["recipient"] = "Manager"
            elif intent == "CLIENT_EMAIL":
                controls["recipient"] = "Client"
            elif intent == "COLLEGE_EMAIL":
                controls["recipient"] = "College"
            else:
                controls["recipient"] = "Recipient"

        # If confidence is low → do nothing (fallback)

    except Exception:
        # Any ML failure → fallback silently
        pass

    return controls
    

