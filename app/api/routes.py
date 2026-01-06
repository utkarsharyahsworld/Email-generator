from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Optional
from app.core.schema import EmailResponse, ErrorResponse, EmailRequest
from app.core.service import generate_email_service, transcribe_audio_service
from app.core.errors import ServiceError
import logging

logger = logging.getLogger("email-generator")
router = APIRouter()

@router.post(
    "/generate",
    response_model=EmailResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def generate_email(req: EmailRequest):
    try:
        return generate_email_service(req)

    except ServiceError as e:
        logger.warning(f"Service error: {e.code} - {e.message}")
        status_code = 400 if e.code == "INVALID_INPUT" else 500
        raise HTTPException(
            status_code=status_code,
            detail={"error": {"code": e.code, "message": e.message}},
        )
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": {"code": "OUTPUT_VALIDATION_FAILED", "message": str(e)}},
        )
    except Exception as e:
        logger.error(f"Unhandled system error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected system error occurred."}},
        )

@router.post("/generate/voice", response_model=EmailResponse)
async def generate_email_voice(
    file: UploadFile = File(...),
    user_name: str = Form(...),
    user_email: Optional[str] = Form(None),
    user_job_title: Optional[str] = Form(None)
):
    try:
        # 1. Read audio
        file_content = await file.read()
        
        # 2. Transcribe
        transcribed_text = await transcribe_audio_service(file_content, file.filename)
        logger.info(f"Voice transcribed: {transcribed_text[:50]}...")

        # 3. Create request
        req = EmailRequest(
            description=transcribed_text,
            user_name=user_name,
            user_email=user_email,
            user_job_title=user_job_title
        )

        # 4. Generate
        return generate_email_service(req)

    except Exception as e:
        logger.error(f"Voice generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": {"code": "VOICE_PROCESSING_FAILED", "message": str(e)}}
        )
@router.post("/transcribe")
async def transcribe_only(file: UploadFile = File(...)):
    """
    New Endpoint: Takes audio, returns text. 
    Does NOT generate email.
    """
    try:
        file_content = await file.read()
        text = await transcribe_audio_service(file_content, file.filename)
        logger.info(f"Transcription success: {text[:30]}...")
        return {"text": text}
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))