import json
import re
from app.core.errors import ServiceError

JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)

def safe_parse_json(text: str) -> dict:
    if not text or not text.strip():
        raise ServiceError(
            code="LLM_EMPTY_RESPONSE",
            message="LLM returned empty response",
        )

    match = JSON_BLOCK_RE.search(text)

    if not match:
        raise ServiceError(
            code="LLM_INVALID_OUTPUT",
            message="No JSON object found in LLM response",
        )

    json_str = match.group(0)

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ServiceError(
            code="LLM_INVALID_JSON",
            message=f"Invalid JSON returned by LLM: {str(e)}",
        )

    if not isinstance(parsed, dict):
        raise ServiceError(
            code="LLM_INVALID_JSON",
            message="Parsed JSON is not an object",
        )

    return parsed
