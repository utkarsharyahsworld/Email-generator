# ACTIONABLE IMPROVEMENT PLAN
## Email Generation System - Next 4 Weeks

**Prepared**: December 30, 2025  
**Target**: Production-ready v1.0 by January 27, 2026

---

## QUICK REFERENCE: PRIORITY MATRIX

```
PHASE 0: BLOCKERS (Must complete before ANY production deployment)
├── P0.1: Structured Logging [2-4h]
├── P0.2: Output Content Validation [6-8h]
├── P0.3: ML-based Intent Classifier [8-12h] ⭐ HIGHEST IMPACT
├── P0.4: Graceful LLM Degradation [3-5h]
├── P0.5: Audit Trail & Request IDs [2-3h]
└── P0.6: JSON Extraction Error Handling [1-2h]

Total Phase 0: ~25-35 hours (spread across week 1)

PHASE 1: HARDENING (Complete before production)
├── P1.1: Configuration Management [2-3h]
├── P1.2: Rate Limiting [2-4h]
├── P1.3: Async/Await Conversion [4-6h]
├── P1.4: Performance Monitoring [3-5h]
├── P1.5: Unit & Integration Tests [8-10h] ⭐ HIGH CONFIDENCE
├── P1.6: Few-Shot Prompt Examples [2-3h]
└── P1.7: User Feedback Loop [4-6h]

Total Phase 1: ~25-37 hours (spread across weeks 2-3)

PHASE 2+: SCALABILITY (Post-production enhancements)
```

---

## SPRINT BREAKDOWN

### WEEK 1: Foundation & Core Fixes

**Goal**: Implement all Phase 0 items. System becomes debuggable and safe.

#### Day 1 (Monday): Logging + Validation Foundation

**Task: P0.1 - Structured Logging**

Create `app/core/logger.py`:
```python
import logging
import json
from datetime import datetime
from typing import Any, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/email_generator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_request(request_id: str, description: str, char_count: int):
    logger.info(f"[{request_id}] Request received: {char_count} chars")

def log_intent_inference(request_id: str, controls: dict):
    logger.info(f"[{request_id}] Intent inferred: domain={controls.get('intent')}, "
                f"confidence={controls.get('confidence')}")

def log_llm_call(request_id: str, prompt_tokens: int, latency_ms: float):
    logger.info(f"[{request_id}] LLM called: {prompt_tokens} tokens, {latency_ms:.1f}ms")

def log_error(request_id: str, error_type: str, error_msg: str):
    logger.error(f"[{request_id}] {error_type}: {error_msg}")

def log_success(request_id: str, latency_ms: float):
    logger.info(f"[{request_id}] SUCCESS: {latency_ms:.1f}ms total")
```

**Task: P0.2 - Output Content Validation**

Create `app/core/output_validator.py`:
```python
import re
from app.core.schema import EmailResponse

def validate_email_output(email: EmailResponse, context: dict) -> tuple[bool, str]:
    """
    Validate generated email for safety and appropriateness.
    Returns: (is_valid, reason)
    """
    
    # Rule 1: Field length constraints
    if len(email.subject) < 3 or len(email.subject) > 100:
        return False, f"Subject length invalid: {len(email.subject)} chars"
    
    if len(email.body) < 20 or len(email.body) > 1000:
        return False, f"Body length invalid: {len(email.body)} chars"
    
    if len(email.greeting) > 50:
        return False, "Greeting too long"
    
    if len(email.closing) > 50:
        return False, "Closing too long"
    
    # Rule 2: Profanity (basic list - expand as needed)
    BANNED_WORDS = [
        'hate', 'stupid', 'idiot', 'damn', 'hell',
        'threat', 'resign', 'fire', 'lawsuit'
    ]
    text_lower = (email.subject + email.body).lower()
    for word in BANNED_WORDS:
        if word in text_lower:
            return False, f"Inappropriate language detected: {word}"
    
    # Rule 3: All-caps warnings (aggressive tone)
    caps_ratio = sum(1 for c in email.body if c.isupper()) / len(email.body)
    if caps_ratio > 0.3:  # More than 30% caps
        return False, "Email appears to be written in ALL CAPS (aggressive tone)"
    
    # Rule 4: Unmatched quotes/brackets
    if email.body.count('"') % 2 != 0 or email.body.count('[') != email.body.count(']'):
        return False, "Email has unmatched quotes or brackets"
    
    # Rule 5: PII patterns (basic regex)
    pii_patterns = [
        r'\d{3}-\d{2}-\d{4}',  # SSN
        r'(\d{3})[-.\s]?(\d{3})[-.\s]?(\d{4})',  # Phone
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email (allow 1 reference)
    ]
    
    email_refs = len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                                email.body + email.subject))
    if email_refs > 1:
        return False, f"Too many email addresses in output: {email_refs}"
    
    # Rule 6: Check for placeholder text (LLM sometimes leaves these)
    placeholders = ['[name]', '[date]', '[number]', '[email]', '...', '[fill in]']
    full_text = email.subject + email.body + email.greeting + email.closing
    for placeholder in placeholders:
        if placeholder in full_text.lower():
            return False, f"Email contains placeholder: {placeholder}"
    
    # Rule 7: Tone consistency check (if formal context, should be formal)
    tone_required = context.get('tone', 'formal')
    if tone_required == 'formal':
        informal_markers = ["yo", "lol", "btw", "imho", "fyi", "lmao", "omg"]
        for marker in informal_markers:
            if marker in email.body.lower():
                return False, f"Informal tone found in formal context: {marker}"
    
    return True, "Valid"
```

Update `service.py` to use validation:
```python
from app.core.output_validator import validate_email_output

def generate_email_service(description: str) -> EmailResponse:
    validate_description(description)
    controls = infer_controls(description)
    prompt = build_prompt(controls, description)
    raw_output = call_llm(prompt)
    parsed = safe_parse_json(raw_output)
    
    email = EmailResponse(**parsed)
    
    # NEW: Validate output
    is_valid, reason = validate_email_output(email, controls)
    if not is_valid:
        logger.warning(f"Output validation failed: {reason}")
        # For now, still return it, but log it. Later: regenerate or fallback
    
    return email
```

**Estimated time**: 3-4 hours

---

#### Days 2-3 (Tue-Wed): ML-Based Intent Classification

**Task: P0.3 - Replace Rule-Based Classifier**

Create `app/core/intent_classifier.py`:

```python
import pickle
from pathlib import Path
import json

# For now, use simple Naive Bayes (can upgrade to logistic regression later)
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class IntentClassifier:
    """
    Lightweight ML-based intent classifier.
    Replaces brittle keyword matching with data-driven approach.
    """
    
    def __init__(self, model_path: str = "app/models/intent_classifier.pkl"):
        self.model_path = Path(model_path)
        self.vectorizer = None
        self.model = None
        self.intent_map = {
            0: ("fee_related", "student", "academic office"),
            1: ("leave_request", "employee", "manager"),
            2: ("payment", "client", "accounts team"),
            3: ("general", "user", "recipient"),
        }
        
        self._load_or_train()
    
    def _load_or_train(self):
        """Load model if exists, otherwise train on seed data."""
        if self.model_path.exists():
            with open(self.model_path, 'rb') as f:
                state = pickle.load(f)
                self.vectorizer = state['vectorizer']
                self.model = state['model']
            return
        
        # Training data: (text, intent_index, confidence)
        training_data = [
            ("i need to pay the college fees urgently", 0, 0.95),
            ("my college fee is pending, need reminder to parents", 0, 0.90),
            ("fee waiver request for financial hardship", 0, 0.85),
            ("I need to take sick leave for medical appointment", 1, 0.95),
            ("need to request leave for 3 days next week", 1, 0.90),
            ("my manager needs to approve my leave", 1, 0.85),
            ("invoice payment is due on the 15th", 2, 0.95),
            ("payment reminder for project", 2, 0.90),
            ("kindly process this payment request", 2, 0.85),
            ("I need to write an email", 3, 0.50),
            ("help me draft a professional message", 3, 0.50),
        ]
        
        texts = [t[0] for t in training_data]
        labels = [t[1] for t in training_data]
        
        # Train vectorizer and model
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        X = self.vectorizer.fit_transform(texts)
        
        self.model = MultinomialNB(alpha=1.0)
        self.model.fit(X, labels)
        
        # Save
        self.model_path.parent.mkdir(exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({'vectorizer': self.vectorizer, 'model': self.model}, f)
    
    def classify(self, text: str) -> dict:
        """
        Classify email intent.
        Returns: {domain, intent, sender, recipient, confidence}
        """
        try:
            X = self.vectorizer.transform([text])
            intent_idx = self.model.predict(X)[0]
            confidence_scores = self.model.predict_proba(X)[0]
            confidence = float(confidence_scores[intent_idx])
            
            intent, sender, recipient = self.intent_map[intent_idx]
            
            return {
                "intent": intent,
                "sender": sender,
                "recipient": recipient,
                "confidence": confidence,  # 0.0 - 1.0 (much better!)
                "domain": self._infer_domain(intent),
            }
        except Exception as e:
            # Fallback to generic
            return {
                "intent": "general",
                "sender": "user",
                "recipient": "recipient",
                "confidence": 0.0,
                "domain": "other",
            }
    
    def _infer_domain(self, intent: str) -> str:
        """Infer domain from intent."""
        mapping = {
            "fee_related": "education",
            "leave_request": "hr",
            "payment": "corporate",
            "general": "other",
        }
        return mapping.get(intent, "other")
```

Update `control.py`:

```python
from app.core.intent_classifier import IntentClassifier

classifier = IntentClassifier()

def infer_controls(description: str) -> dict:
    """
    Infer email controls using ML-based classifier.
    Fallback to rule-based if ML fails.
    """
    result = classifier.classify(description)
    
    # Confidence threshold: if < 0.4, treat as low confidence
    confidence_level = "high" if result['confidence'] > 0.4 else "low"
    
    return {
        "tone": "formal",
        "length": "short",
        "sender": result['sender'],
        "recipient": result['recipient'],
        "intent": result['intent'],
        "domain": result['domain'],
        "confidence": confidence_level,
        "confidence_score": result['confidence'],  # For logging
    }
```

**Estimated time**: 6-8 hours (includes training data curation, testing)

---

#### Day 4 (Thu): Graceful Degradation + Audit Trail

**Task: P0.4 - Resilient LLM Client**

Update `llm/client.py`:

```python
import requests
import time
import logging

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "mistral"
MAX_RETRIES = 3
TIMEOUT = 60  # Reduced from 120s

def call_llm_with_retries(prompt: str, attempt: int = 0) -> str:
    """Call LLM with exponential backoff retries."""
    
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "num_predict": 120,
            "temperature": 0.2
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=TIMEOUT
        )
        latency_ms = (time.time() - start_time) * 1000
        logger.info(f"LLM call success: {latency_ms:.1f}ms")
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    
    except (requests.Timeout, requests.ConnectionError) as e:
        if attempt < MAX_RETRIES:
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            logger.warning(f"LLM call failed (attempt {attempt+1}/{MAX_RETRIES}), "
                          f"retrying in {wait_time}s: {e}")
            time.sleep(wait_time)
            return call_llm_with_retries(prompt, attempt + 1)
        else:
            logger.error(f"LLM unavailable after {MAX_RETRIES} retries")
            raise
    
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise

def call_llm(prompt: str) -> str:
    """
    Public API for calling LLM.
    Handles retries and degradation.
    """
    return call_llm_with_retries(prompt)
```

**Task: P0.5 - Audit Trail**

Create `app/core/audit.py`:

```python
import json
import uuid
from datetime import datetime
from pathlib import Path

AUDIT_LOG_PATH = Path("logs/audit.jsonl")

class AuditLogger:
    @staticmethod
    def log_request(request_id: str, description: str, char_count: int):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "event_type": "REQUEST_RECEIVED",
            "input_length": char_count,
        }
        AuditLogger._write(event)
    
    @staticmethod
    def log_intent(request_id: str, intent: str, confidence: float):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "event_type": "INTENT_INFERRED",
            "intent": intent,
            "confidence": confidence,
        }
        AuditLogger._write(event)
    
    @staticmethod
    def log_output(request_id: str, email_obj: dict, is_valid: bool):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "event_type": "OUTPUT_GENERATED",
            "output_valid": is_valid,
            "output_length": sum(len(v) for v in email_obj.values() if isinstance(v, str)),
        }
        AuditLogger._write(event)
    
    @staticmethod
    def log_error(request_id: str, error_type: str, error_msg: str):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "event_type": "ERROR",
            "error_type": error_type,
            "error_message": error_msg,
        }
        AuditLogger._write(event)
    
    @staticmethod
    def _write(event: dict):
        AUDIT_LOG_PATH.parent.mkdir(exist_ok=True)
        with open(AUDIT_LOG_PATH, 'a') as f:
            f.write(json.dumps(event) + '\n')

def generate_request_id() -> str:
    return str(uuid.uuid4())[:8]
```

Update `service.py`:

```python
from app.core.audit import AuditLogger, generate_request_id

def generate_email_service(description: str) -> dict:
    request_id = generate_request_id()
    
    try:
        AuditLogger.log_request(request_id, description, len(description))
        
        validate_description(description)
        
        controls = infer_controls(description)
        AuditLogger.log_intent(request_id, controls['intent'], 
                              controls.get('confidence_score', 0.0))
        
        prompt = build_prompt(controls, description)
        raw_output = call_llm(prompt)
        parsed = safe_parse_json(raw_output)
        
        email = EmailResponse(**parsed)
        is_valid, _ = validate_email_output(email, controls)
        AuditLogger.log_output(request_id, email.dict(), is_valid)
        
        return {"request_id": request_id, "email": email}
    
    except Exception as e:
        AuditLogger.log_error(request_id, type(e).__name__, str(e))
        raise
```

**Estimated time**: 2-3 hours

---

#### Day 5 (Fri): JSON Handling + Testing

**Task: P0.6 - Robust JSON Extraction**

Update `json_guard.py`:

```python
import json
import logging

logger = logging.getLogger(__name__)

def safe_parse_json(text: str, max_attempts: int = 2) -> dict:
    """
    Attempt to extract and parse JSON from text with fallback.
    """
    
    # Attempt 1: Extract JSON block using bracket matching
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        clean = text[start:end]
        return json.loads(clean)
    except Exception as e:
        logger.warning(f"JSON extraction attempt 1 failed: {e}")
    
    # Attempt 2: Try to find valid JSON by parsing progressively
    try:
        for end in range(len(text), 0, -1):
            try:
                return json.loads(text[text.index("{"):end])
            except json.JSONDecodeError:
                continue
    except Exception as e:
        logger.warning(f"JSON extraction attempt 2 failed: {e}")
    
    # Attempt 3: If all else fails, raise with helpful error
    raise ValueError(f"Could not extract valid JSON from LLM response. Got: {text[:200]}")
```

**Basic Test Suite** (create `tests/test_service.py`):

```python
import pytest
from app.core.service import generate_email_service
from app.core.output_validator import validate_email_output
from app.core.schema import EmailResponse

def test_fee_request():
    """Test fee-related email (high confidence)."""
    desc = "I need to inform the office about my college fee payment status"
    # Would need to mock LLM call
    pass

def test_ambiguous_request():
    """Test ambiguous email (low confidence)."""
    desc = "write an email"
    # Should fall back to neutral tone
    pass

def test_output_validation():
    """Test that inappropriate emails are flagged."""
    email = EmailResponse(
        subject="URGENT!!!",
        greeting="Hey",
        body="YOU ARE FIRED" * 100,  # All caps
        closing="Bye"
    )
    is_valid, reason = validate_email_output(email, {"tone": "formal"})
    assert not is_valid

def test_json_extraction():
    """Test JSON extraction from LLM noise."""
    text = "Sure! Here's the email:\n{\"subject\": \"Test\", \"greeting\": \"Hi\", " \
           "\"body\": \"Hello\", \"closing\": \"Regards\"}\n\nGood luck!"
    from app.utils.json_guard import safe_parse_json
    result = safe_parse_json(text)
    assert result['subject'] == "Test"
```

**Estimated time**: 2-3 hours

---

### Week 1 Summary

| Item | Hours | Status |
|------|-------|--------|
| P0.1 Logging | 2-3h | ✅ |
| P0.2 Output Validation | 3-4h | ✅ |
| P0.3 ML Classifier | 6-8h | ✅ |
| P0.4 Graceful Degradation | 2-3h | ✅ |
| P0.5 Audit Trail | 2h | ✅ |
| P0.6 JSON Handling | 1-2h | ✅ |
| Testing & Integration | 3-4h | ✅ |
| **Total** | **~22-27h** | |

**Outcome**: System is now safe to deploy internally. All critical failures are logged, intent inference is data-driven, and output is validated.

---

### WEEK 2: Hardening & Scalability

**Goal**: Implement Phase 1 items. System becomes scalable and enterprise-hardened.

#### P1.1: Configuration Management (2-3h)

Create `app/config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM settings
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))
    
    # Generation settings
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "120"))
    
    # Validation settings
    MIN_DESCRIPTION_LENGTH = int(os.getenv("MIN_DESC_LENGTH", "10"))
    MAX_DESCRIPTION_LENGTH = int(os.getenv("MAX_DESC_LENGTH", "500"))
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
    RATE_LIMIT_WINDOW_SECS = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/email_generator.log")
```

#### P1.2: Rate Limiting (2-4h)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/generate")
@limiter.limit("10/minute")
def generate_email(req: EmailRequest):
    return generate_email_service(req.description)
```

#### P1.3: Async/Await (4-6h)

Convert to async pipeline (full conversion of service layer).

#### P1.4: Performance Monitoring (3-5h)

Add metrics collection and Prometheus export.

#### P1.5: Unit & Integration Tests (8-10h)

Build test suite with 70%+ coverage.

---

### WEEK 3: Optimization & Feedback

**Goal**: Polish and gather user feedback.

- P1.6: Few-Shot Prompt Examples (2-3h)
- P1.7: User Feedback Loop (4-6h)
- Manual testing & bug fixes

---

### WEEK 4: Launch Preparation

**Goal**: Deploy to production.

- Documentation
- Deployment runbook
- Monitoring setup
- Soft launch (limited capacity)
- Production monitoring

---

## CRITICAL SUCCESS FACTORS

1. **P0.3 (ML Classifier)** is highest-priority: spend most effort here
2. **Testing** should start immediately; don't defer to end
3. **Logging** is non-negotiable for production debugging
4. **Output Validation** prevents embarrassing failures
5. **Configuration** must allow easy tuning without redeploying

---

## DEPLOYMENT CHECKLIST

Before going to production:

- [ ] All Phase 0 items complete and tested
- [ ] Logging verified (check logs/email_generator.log)
- [ ] Audit trail verified (check logs/audit.jsonl)
- [ ] Rate limiting tested
- [ ] Error handling tested (Ollama offline, invalid JSON, etc.)
- [ ] Output validation tested (inappropriate content caught)
- [ ] 70%+ test coverage achieved
- [ ] Performance baseline established (avg latency < 30s)
- [ ] Documentation complete
- [ ] Monitoring dashboards configured
- [ ] Runbook for common issues
- [ ] Rollback plan defined

---

## SUCCESS METRICS (Week 4)

- ✅ **Reliability**: 99.0% uptime (after P0.4 retries)
- ✅ **Latency**: p95 < 20s (after P1.3 async)
- ✅ **Output Quality**: 95%+ emails pass validation
- ✅ **Intent Accuracy**: 85%+ correct classification (vs 60% rule-based)
- ✅ **Coverage**: 70%+ test coverage, 0 critical bugs

---

**Ready to start? Create a dev branch and begin with P0.1 on Monday.**
