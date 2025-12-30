from fastapi import APIRouter
from app.core.service import generate_email_service
from app.core.schema import EmailRequest

router = APIRouter()

@router.post("/generate")
def generate_email(req: EmailRequest):
    return generate_email_service(req.description)
