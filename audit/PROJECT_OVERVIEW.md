# Project Overview

## System Purpose

This is a **FastAPI-based email generation service** that generates professional emails based on user descriptions. The system combines LLM-driven content generation with optional ML-based intent classification to produce structured email outputs.

## What It Does

1. **Accepts a user request**: A text description of the email to be written (5-500 characters)
2. **Infers email intent**: Uses ML model (`intent_predictor.py`) to classify the email type with confidence scoring
3. **Builds a prompt**: Constructs a detailed prompt for the LLM based on inferred intent and controls
4. **Calls LLM API**: Invokes Groq's Llama-3.1-8b-instant model with temperature=0.2
5. **Parses JSON response**: Extracts JSON from LLM output using regex pattern matching
6. **Validates output**: Ensures all required fields are present, no placeholders exist, and content meets length constraints
7. **Returns structured email**: Returns subject, greeting, body, and closing as JSON

## What It Does NOT Do

- **Does NOT handle authentication/authorization**: No user identity verification or role-based access control
- **Does NOT persist data**: No database, no audit logs, no request history storage
- **Does NOT implement rate limiting**: No throttling or quota management per user/IP
- **Does NOT handle attachments or HTML formatting**: Only plain text JSON structure
- **Does NOT support multi-language output**: Default language is English
- **Does NOT include frontend**: Only backend API with FastAPI
- **Does NOT train/update ML models at runtime**: Models are pre-trained and loaded from disk
- **Does NOT perform content moderation**: No filtering for sensitive/inappropriate content
- **Does NOT retry failed LLM calls**: Single attempt only with no exponential backoff

## Intended Users

- Backend systems or frontend applications that need to auto-generate professional emails
- Unknown if multi-tenant or single-user deployment

## Input Contract

**Endpoint**: `POST /generate`

**Request Body**:
```json
{
  "description": "string (5-500 characters)"
}
```

Validation rules:
- Minimum 10 characters (note: schema says 5, validator enforces 10)
- Maximum 500 characters
- Must be non-empty after stripping whitespace

## Output Contract

**Success Response** (HTTP 200):
```json
{
  "subject": "string (max 150 chars, no placeholders)",
  "greeting": "string (no empty, no placeholders)",
  "body": "string (min 20 chars, no placeholders)",
  "closing": "string (no empty, no placeholders)"
}
```

**Error Responses**:
- HTTP 400: Invalid input (description validation fails)
- HTTP 500: LLM failures, JSON parsing errors, output validation failures

Error body format:
```json
{
  "error": {
    "code": "INVALID_INPUT|LLM_EMPTY_RESPONSE|LLM_INVALID_OUTPUT|LLM_INVALID_JSON",
    "message": "string"
  }
}
```

## Architecture Type

**Hybrid approach**:
- **Phase 0**: Default safe controls (tone="professional", length="medium")
- **Phase 1**: ML-based intent detection that optionally adjusts the recipient field based on confidence threshold (0.6)
- **Phase 2**: LLM-driven generation with prompt engineering based on controls

The system is designed with **graceful degradation**: if ML fails, it falls back to defaults silently.

## Production Readiness Assessment Scope

This audit covers:
- Architecture stability and safety
- Request flow integrity
- Error handling completeness
- Failure mode handling
- Production deployment readiness

This assessment is based entirely on code inspection; runtime behavior cannot be verified without execution.
