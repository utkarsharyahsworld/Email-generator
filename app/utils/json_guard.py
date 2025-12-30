import json

def safe_parse_json(text: str) -> dict:
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        clean = text[start:end]
        return json.loads(clean)
    except Exception:
        raise ValueError("Invalid JSON from LLM")
