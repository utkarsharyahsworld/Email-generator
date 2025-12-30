from pydantic import BaseModel, Field
from pydantic import BaseModel


class EmailRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=5,
        description="User description of the email to be generated"
    )


class EmailResponse(BaseModel):
    subject: str
    greeting: str
    body: str
    closing: str


class ErrorResponse(BaseModel):
    error: dict
