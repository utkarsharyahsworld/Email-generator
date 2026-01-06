# Request Flow Analysis

## Complete Request Lifecycle

### Entry Point: FastAPI Route

**File**: [app/api/routes.py](app/api/routes.py)  
**Function**: `generate_email()`

```
POST /generate (EmailRequest)
  ↓
  ├─ Pydantic validates: description field exists and meets Field constraints
  │  (Field constraint: min_length=5, but actual validation is stricter)
  │
  └─ Calls: generate_email_service(req.description)
```

---

### Step 1: Input Validation

**File**: [app/core/service.py](app/core/service.py#L11) → calls [app/core/validator.py](app/core/validator.py)  
**Function**: `validate_description(description: str)`

**Validation Rules**:
- If `desc` is empty or `len(desc.strip()) < 10`: raise `ServiceError(code="INVALID_INPUT")`
- If `len(desc) > 500`: raise `ServiceError(code="INVALID_INPUT")`

**Flow**:
```
validate_description()
  ↓
  ├─ Check: len(desc.strip()) >= 10
  ├─ Check: len(desc) <= 500
  └─ If violation: raise ServiceError → caught by router → HTTP 400
```

**Logged**: No explicit logging in validator

---

### Step 2: Intent Inference & Control Extraction

**File**: [app/core/service.py](app/core/service.py#L14) → calls [app/core/control.py](app/core/control.py#L33)  
**Function**: `infer_controls(description: str) -> dict`

**Default Controls** (Phase 0):
```python
{
  "tone": "professional",
  "length": "medium",
  "recipient": "Recipient"
}
```

**ML Intent Detection** (Phase 1):
```
infer_controls()
  ↓
  ├─ Try: predict_intent(description)
  │  ├─ Loads pickled vectorizer and model from disk
  │  ├─ Transforms description to feature vector
  │  ├─ Gets prediction probabilities
  │  ├─ Returns (intent: str, confidence: float)
  │  └─ File: app/ml/intent_predictor.py
  │
  ├─ If confidence >= 0.6:
  │  ├─ "HR_EMAIL" → controls["recipient"] = "HR"
  │  ├─ "MANAGER_EMAIL" → controls["recipient"] = "Manager"
  │  ├─ "CLIENT_EMAIL" → controls["recipient"] = "Client"
  │  ├─ "COLLEGE_EMAIL" → controls["recipient"] = "College"
  │  └─ Other intents → do nothing (keep "Recipient")
  │
  ├─ If confidence < 0.6 → no control changes (silent fallback)
  │
  └─ If ANY exception (model not found, pickle corruption, etc.):
     └─ Silently fall back to defaults
```

**Logged**: `logger.info(f"Inferred controls: {controls}")`

**Important**: ML failures are **silent and non-blocking**. The system degrades gracefully.

---

### Step 3: Prompt Construction

**File**: [app/core/service.py](app/core/service.py#L15) → calls [app/core/prompt.py](app/core/prompt.py)  
**Function**: `build_prompt(controls: dict, description: str) -> str`

**Prompt Variables Used**:
- `confidence = controls.get("confidence", "low")` ← **Note: "confidence" is never set in controls!**
- `sender = controls.get("sender", "Sender")` ← **Note: "sender" is never set in controls!**
- `recipient = controls.get("recipient", "Recipient")` ← Set by intent inference or defaults to "Recipient"
- `intent = controls.get("intent", "general_email")` ← **Note: "intent" is never set in controls!**
- `length = controls.get("length", "medium")` ← Set to "medium" in defaults
- `tone = controls.get("tone", "professional")` ← Set to "professional" in defaults

**Prompt Guidance Logic**:
```
if confidence == "high":
    guidance = "Write strictly according to sender, recipient, intent"
else:
    guidance = "Request is ambiguous. Write neutral, professional. Don't assume authority/deadlines."
```

Since `confidence` is **never set**, the condition is always `False`, and the system always uses the **"ambiguous" guidance**.

**Output**: Formatted prompt string with user description appended

**Logged**: No explicit logging for prompt construction

---

### Step 4: LLM Invocation

**File**: [app/core/service.py](app/core/service.py#L16) → calls [app/llm/client.py](app/llm/client.py)  
**Function**: `call_llm(prompt: str) -> str`

**LLM Configuration**:
- **API**: Groq (requires `GROQ_API_KEY` environment variable)
- **Model**: `llama-3.1-8b-instant`
- **Temperature**: `0.2` (low randomness, deterministic)
- **Max tokens**: `300` (limits response length)

**Error Handling**:
```
call_llm()
  ↓
  ├─ Check: if not client.api_key:
  │  └─ raise RuntimeError("GROQ_API_KEY not set")
  │
  ├─ Call: client.chat.completions.create(...)
  │
  └─ Return: response.choices[0].message.content
```

**Flow**:
- If API key is missing: raises `RuntimeError` (not caught at this layer)
- If Groq API call fails: propagates Groq exception (not caught)
- If response is empty/null: returns empty string (handled later)

**Logged**: `logger.info("LLM response received")`

---

### Step 5: JSON Extraction & Safe Parsing

**File**: [app/core/service.py](app/core/service.py#L17) → calls [app/utils/json_guard.py](app/utils/json_guard.py)  
**Function**: `safe_parse_json(text: str) -> dict`

**Parsing Logic**:
```
safe_parse_json()
  ↓
  ├─ Check: if not text or not text.strip():
  │  └─ raise ServiceError(code="LLM_EMPTY_RESPONSE")
  │
  ├─ Regex search: \{.*\} (DOTALL mode, greedy match)
  │  └─ Finds first { and last } in the response
  │
  ├─ If no match:
  │  └─ raise ServiceError(code="LLM_INVALID_OUTPUT")
  │
  ├─ Try: json.loads(json_str)
  │  ├─ If JSONDecodeError:
  │  │  └─ raise ServiceError(code="LLM_INVALID_JSON")
  │  └─ If successful: continue
  │
  ├─ Check: if not isinstance(parsed, dict):
  │  └─ raise ServiceError(code="LLM_INVALID_JSON")
  │
  └─ Return: parsed dict
```

**Regex Caveat**: Uses greedy matching `\{.*\}` with DOTALL. If LLM returns multiple JSON objects, only content between first `{` and last `}` is extracted.

**Logged**: `logger.info("JSON parsed successfully")`

---

### Step 6: Output Validation

**File**: [app/core/service.py](app/core/service.py#L18) → calls [app/core/output_validator.py](app/core/output_validator.py)  
**Function**: `validate_email_output(data: dict) -> None`

**Validation Rules** (in order):
```
validate_email_output()
  ↓
  ├─ Required fields: ["subject", "greeting", "body", "closing"]
  │  └─ If any missing: raise ValueError("Missing field: {field}")
  │
  ├─ For each field:
  │  ├─ Strip whitespace
  │  ├─ If empty: raise ValueError("Empty field: {field}")
  │  ├─ If contains placeholder pattern [.*?]: raise ValueError("Placeholder detected")
  │  └─ Placeholder regex: \[.*?\] (matches [Anything])
  │
  ├─ Check subject length: if len(subject) > 150:
  │  └─ raise ValueError("Subject too long")
  │
  └─ Check body length: if len(body) < 20:
     └─ raise ValueError("Body too short")
```

**Validation Fails**: Raises `ValueError` (not `ServiceError`!)

**Logged**: `logger.info("Output validation passed")`

---

### Step 7: Response Construction & Error Handling

**File**: [app/core/service.py](app/core/service.py#L20)  
**Function**: `generate_email_service()` return

```
generate_email_service()
  ↓
  └─ Return: EmailResponse(**parsed)
     └─ Pydantic models the response
```

All exceptions are caught at the **route layer** in [app/api/routes.py](app/api/routes.py#L16):

```python
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
```

**Critical Issue**: Only `ServiceError` is caught. Other exceptions (`ValueError`, `RuntimeError`, Groq exceptions) are **not caught** and will return HTTP 500 with FastAPI's default error format (not the custom ErrorResponse format).

---

## Complete Flow Diagram

```
POST /generate
  ↓
[Pydantic validates EmailRequest]
  ↓
generate_email_service(description)
  ├─ validate_description() → ServiceError("INVALID_INPUT")
  │    ↓ (if fails, caught by route, HTTP 400)
  ├─ infer_controls() → dict (with silent fallbacks)
  │    ↓
  ├─ build_prompt(controls, description) → str
  │    ↓
  ├─ call_llm(prompt) → str
  │    ↓ (RuntimeError or Groq exception → NOT CAUGHT)
  ├─ safe_parse_json(raw_output) → dict
  │    ↓ (ServiceError → caught by route, HTTP 400/500)
  ├─ validate_email_output(parsed) → None
  │    ↓ (ValueError → NOT CAUGHT)
  └─ return EmailResponse(**parsed)
       ↓ (Pydantic validation)
       ↓ (If validation passes → HTTP 200)
       ↓ (If validation fails → Pydantic error → HTTP 422)
```

---

## Summary of Logging Points

1. `service.py:11` → "Request received"
2. `control.py:55` → "Inferred controls: {controls}"
3. `client.py:18` → "LLM response received"
4. `json_guard.py:6` → "JSON parsed successfully"
5. `output_validator.py:27` → "Output validation passed"

No logging for prompt construction, ML failures, or validation failures.

---

## Error Codes Reference

| Code | Status | Cause | Handled? |
|------|--------|-------|----------|
| INVALID_INPUT | 400 | Description too short/long | ✓ |
| LLM_EMPTY_RESPONSE | 500 | LLM returned empty/null | ✓ |
| LLM_INVALID_OUTPUT | 500 | No JSON found in response | ✓ |
| LLM_INVALID_JSON | 500 | JSON syntax error or non-dict | ✓ |
| ValueError (from output validator) | 500 | Missing/empty/invalid fields | ✗ |
| RuntimeError (from LLM client) | 500 | GROQ_API_KEY not set | ✗ |
| Other exceptions | 500 | Groq API errors, ML model errors | ✗ |
