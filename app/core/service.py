from app.core.validator import validate_description
from app.core.control import infer_controls
from app.core.prompt import build_prompt
from app.llm.client import call_llm
from app.utils.json_guard import safe_parse_json
from app.core.schema import EmailResponse

def generate_email_service(description: str) -> EmailResponse:
    validate_description(description)

    controls = infer_controls(description)
    prompt = build_prompt(controls, description)

    raw_output = call_llm(prompt)
    parsed = safe_parse_json(raw_output)
    

    return EmailResponse(**parsed)
