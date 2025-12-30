from pydantic import BaseModel, Field


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
