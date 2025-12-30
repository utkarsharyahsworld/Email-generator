from app.core.errors import ServiceError

def validate_description(desc: str):
    if not desc or len(desc.strip()) < 10:
        raise ServiceError(
            code="INVALID_INPUT",
            message="Description too short",
        )

    if len(desc) > 500:
        raise ServiceError(
            code="INVALID_INPUT",
            message="Description too long",
        )
