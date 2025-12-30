def validate_description(desc: str):
    if not desc or len(desc.strip()) < 10:
        raise ValueError("Description too short")

    if len(desc) > 500:
        raise ValueError("Description too long")
