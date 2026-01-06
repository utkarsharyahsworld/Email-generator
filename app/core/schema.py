from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any

class EmailRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=500)
    user_name: str = Field(..., min_length=2, max_length=50)
    user_email: Optional[str] = None
    tone: Optional[str] = "professional"
    
    # NEW: Dynamic Fields
    sender_type: str = "professional"  # professional, student, business
    
    # Optional context fields
    user_company: Optional[str] = None
    user_university: Optional[str] = None
    
class EmailResponse(BaseModel):
    subject: str
    greeting: str
    body: str
    closing: str

class ErrorResponse(BaseModel):
    error: Dict[str, Any]   