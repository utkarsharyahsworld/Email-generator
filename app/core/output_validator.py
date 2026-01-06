import re
from app.core.logger import logger

# Regex to find [Placeholders]
PLACEHOLDER_PATTERN = re.compile(r"\[.*?\]")

def validate_email_output(data: dict) -> None:
    required_fields = ["subject", "greeting", "body", "closing"]

    for field in required_fields:
        # 1. Check for missing keys
        if field not in data:
            raise ValueError(f"Missing field: {field}")
        
        value = data[field]
        
        # 2. Check for empty strings
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Empty field: {field}")

        # 3. Check for placeholders (CRITICAL FIX: Log warning only, DO NOT CRASH)
        if PLACEHOLDER_PATTERN.search(value):
            logger.warning(f"⚠️ Placeholder detected in '{field}'. Passed to user for manual edit.")
            # We allow it to pass so you can edit it in the UI.

    # 4. Length checks
    if len(data["subject"]) > 200: # Relaxed slightly to 200
        raise ValueError("Subject too long (max 200 chars)")
        
    if len(data["body"]) < 10:
        raise ValueError("Body too short (min 10 chars)")