from app.llm.client import call_llm
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
    d = description.lower()

    sender = "user"
    recipient = "recipient"
    intent = "general"
    confidence = "low"

    if any(k in d for k in ["student", "exam", "fee", "college"]):
        sender = "student"
        recipient = "academic office"
        intent = "fee_related"
        confidence = "high"

    elif any(k in d for k in ["leave", "sick", "manager"]):
        sender = "employee"
        recipient = "manager"
        intent = "leave_request"
        confidence = "high"

    elif any(k in d for k in ["payment", "invoice", "amount", "due"]):
        sender = "client"
        recipient = "accounts team"
        intent = "payment"
        confidence = "high"

    return {
        "sender": sender,
        "recipient": recipient,
        "intent": intent,
        "tone": "formal",
        "length": "short",
        "confidence": confidence
    }


