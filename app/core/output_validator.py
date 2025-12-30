import re

PLACEHOLDER_PATTERN = re.compile(r"\[.*?\]")

def validate_email_output(data: dict) -> None:
    required_fields = ["subject", "greeting", "body", "closing"]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing field: {field}")

        value = data[field].strip()

        if not value:
            raise ValueError(f"Empty field: {field}")

        if PLACEHOLDER_PATTERN.search(value):
            raise ValueError(f"Placeholder detected in field: {field}")

    if len(data["subject"]) > 150:
        raise ValueError("Subject too long")

    if len(data["body"]) < 20:
        raise ValueError("Body too short")
