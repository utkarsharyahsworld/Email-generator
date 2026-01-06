# from fastapi import UploadFile
from app.core.validator import validate_description
from app.core.control import infer_controls
from app.core.prompt import build_prompt
from app.llm.client import client, call_llm
from app.utils.json_guard import safe_parse_json
from app.core.schema import EmailResponse, EmailRequest
from app.core.logger import logger
from app.core.output_validator import validate_email_output
from app.core.errors import ServiceError

async def transcribe_audio_service(file_content: bytes, filename: str) -> str:
    """
    Transcribes audio using Groq's Whisper model (distil-whisper-large-v3-en).
    """
    try:
        # We use the same 'client' imported from app.llm.client
        transcription = client.audio.transcriptions.create(
            file=(filename, file_content),
            model="whisper-large-v3", # Fastest model for English
            response_format="text",
            temperature=0.0
        )
        return transcription
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise ServiceError(code="TRANSCRIPTION_FAILED", message="Failed to process audio file.")

def generate_email_service(req: EmailRequest) -> EmailResponse:
    logger.info("Request received")
    
    # 1. Validate description
    validate_description(req.description)

    # 2. Infer controls
    controls = infer_controls(req.description)
    logger.info(f"Inferred controls: {controls}")

    # 3. Prepare user details for the prompt
    # Inside generate_email_service...

    # Prepare user details
    user_details = {
        "name": req.user_name,
        "email": req.user_email,
        "role": req.sender_type,          # e.g., "student"
        "company": req.user_company,      # for professionals
        "university": req.user_university # for students
    }

    # Pass to build_prompt...
    # prompt = build_prompt(controls, req.description, user_details)

    # 4. Build prompt
    prompt = build_prompt(controls, req.description, user_details)

    # 5. Call LLM
    raw_output = call_llm(prompt)
    logger.info("LLM response received")

    # 6. Parse and Validate
    parsed = safe_parse_json(raw_output)
    logger.info("JSON parsed successfully")

    validate_email_output(parsed)
    logger.info("Output validation passed")
    
    return EmailResponse(**parsed)