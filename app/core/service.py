from app.core.validator import validate_description
from app.core.control import infer_controls
from app.core.prompt import build_prompt
from app.llm.client import call_llm
from app.utils.json_guard import safe_parse_json
from app.core.schema import EmailResponse
from app.core.logger import logger
from app.core.output_validator import validate_email_output




def generate_email_service(description: str) -> EmailResponse:
    logger.info("Request received")
    validate_description(description)

    controls = infer_controls(description)
    logger.info(f"Inferred controls: {controls}")

    prompt = build_prompt(controls, description)

    raw_output = call_llm(prompt)
    logger.info("LLM response received")

    parsed = safe_parse_json(raw_output)
    logger.info("JSON parsed successfully")

    validate_email_output(parsed)
    logger.info("Output validation passed")
    

    return EmailResponse(**parsed)
