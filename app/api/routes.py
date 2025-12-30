from fastapi import APIRouter, HTTPException
from app.core.schema import EmailResponse, ErrorResponse
from app.core.service import generate_email_service
from app.core.errors import ServiceError
from app.core.schema import EmailRequest


router = APIRouter()
@router.post(
    "/generate",
    response_model=EmailResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def generate_email(req: EmailRequest):
    try:
        return generate_email_service(req.description)

    except ServiceError as e:
        status_code = 400 if e.code == "INVALID_INPUT" else 500

        raise HTTPException(
            status_code=status_code,
            detail={
                "error": {
                    "code": e.code,
                    "message": e.message,
                }
            },
        )
