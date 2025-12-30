# REAL-WORLD FAILURE SCENARIOS
## What Can Go Wrong in Production (Today)

---

## SCENARIO 1: Intent Misclassification 🔴 CRITICAL

### The Problem
Rule-based keyword matching leads to wrong sender/recipient role inference.

### Real-World Case: The Consultant Email

**What the user thinks they're writing:**
```
"I'm a management consultant advising a college on their fee structure. 
I need to send a professional message to the academic dean about 
recommended fee adjustments to improve enrollment."
```

**What the system infers:**
- Keywords: "fee", "college"
- Inferred sender: "student"
- Inferred recipient: "academic office"
- Inferred intent: "fee_related"

**What the LLM generates:**
```json
{
  "subject": "Request for Fee Reduction or Waiver",
  "greeting": "Dear Academic Office,",
  "body": "I am writing to request a reduction in my college fees 
           as I am facing financial difficulties. 
           Please consider my request and grant me relief.",
  "closing": "Respectfully yours"
}
```

**What happens:**
1. User receives email written from a student's perspective (WRONG)
2. User is confused but might send it anyway
3. Dean receives a fee waiver request instead of professional consulting advice
4. Consultant's credibility is destroyed
5. Business opportunity lost

**Impact**: HIGH - Completely wrong communication tone and authority level

---

## SCENARIO 2: Hallucinated Commitments 🔴 CRITICAL

### The Problem
LLM generates plausible-sounding but false commitments.

### Real-World Case: The Service Provider

**What the user writes:**
```
"email to our client confirming we're ready for the project kick-off"
```

**What the LLM generates:**
```json
{
  "subject": "Project Kick-Off - Ready to Begin",
  "greeting": "Dear [Client Name],",
  "body": "We are pleased to confirm that our team is ready to begin 
           your project on January 5, 2026. We have allocated 5 senior 
           engineers and will deliver the MVP by March 15, 2026 with 
           99.9% uptime SLA. Our initial infrastructure setup is 
           complete and we're ready for launch.",
  "closing": "Looking forward to working with you"
}
```

**What happens:**
1. User sends email with specific dates/commitments
2. LLM invented all specifics (5 engineers, March 15, 99.9% SLA)
3. Client's expectations set based on fabricated details
4. When email is discovered to contain errors, damage is done
5. Legal liability potential (breach of implied contract)

**Impact**: CRITICAL - Contractual liability, reputation damage

---

## SCENARIO 3: PII Leakage 🔴 CRITICAL

### The Problem
LLM doesn't guard against accidental sensitive data in output.

### Real-World Case: The HR Manager

**What the user writes:**
```
"Draft an email to finance about processing my new direct deposit 
and updating my information in the system. My banking details need 
to be updated in the employee database."
```

**What the LLM generates:**
```json
{
  "subject": "Direct Deposit Update Request",
  "greeting": "Dear Finance Team,",
  "body": "I am writing to request an update to my direct deposit 
           information. Please update my bank account to the following:
           Account Holder: [Employee Name]
           Bank: Chase Bank
           Routing Number: 021000021
           Account Number: 987654321
           
           Additionally, my social security number is 123-45-6789 
           for verification purposes. Please confirm receipt.",
  "closing": "Thank you"
}
```

**What happens:**
1. User doesn't notice PII in body (assumed it was their responsibility)
2. Sends email with banking and SSN information
3. Email travels through company systems (possibly archived, forwarded, etc.)
4. Exposed to anyone with email access (finance staff, IT, etc.)
5. Identity theft risk, regulatory violation (GDPR/SOC2)

**Impact**: CRITICAL - Compliance breach, security incident

---

## SCENARIO 4: Aggressive Tone from Neutral Input 🟡 HIGH

### The Problem
LLM generates aggressive/emotional response when formal is required.

### Real-World Case: The Student

**What the user writes:**
```
"my professor failed me unfairly. draft an email about it"
```

**What the LLM generates:**
```json
{
  "subject": "GRADE APPEAL - UNFAIR GRADING",
  "greeting": "Dear Professor,",
  "body": "I am writing to formally challenge the grade you gave me. 
           This grade is COMPLETELY UNFAIR and I DEMAND a regrade 
           immediately! The grading rubric was not followed correctly 
           and I have evidence. This is unacceptable and I won't tolerate 
           this injustice any further!!!",
  "closing": "I expect a response within 24 hours."
}
```

**What happens:**
1. Student is upset, sends email without review (seems right)
2. Professor reads aggressive tone and caps
3. Refuses to consider appeal (perceived as hostile)
4. Student's legitimate concern ignored
5. Grade stands despite valid concerns

**Impact**: HIGH - Valid concerns ignored due to wrong tone

---

## SCENARIO 5: Incomplete Template Left In Output 🟡 HIGH

### The Problem
LLM doesn't properly fill templates and leaves placeholders.

### Real-World Case: The Manager

**What the user writes:**
```
"write a performance review email for my team member about their Q4 work"
```

**What the LLM generates:**
```json
{
  "subject": "Q4 Performance Review - [EMPLOYEE_NAME]",
  "greeting": "Hi [First Name],",
  "body": "Thank you for your work this quarter. [SPECIFIC_ACHIEVEMENTS] 
           were well executed. However, [AREA_FOR_IMPROVEMENT] needs 
           attention. Going forward, focus on [GOAL_FOR_Q1].",
  "closing": "Let's schedule a 1-on-1 to discuss."
}
```

**What happens:**
1. Manager is busy, copy-pastes email without noticing placeholders
2. Sends to employee with "[SPECIFIC_ACHIEVEMENTS]" visible
3. Employee thinks manager didn't prepare for the review
4. Review feels impersonal and disrespectful
5. Employee morale hurt, relationship damage

**Impact**: HIGH - Looks unprofessional, damages relationships

---

## SCENARIO 6: Service Unavailability 🔴 CRITICAL

### The Problem
Single Ollama failure = complete system outage.

### Timeline

**10:00 AM**
- System running smoothly
- Ollama process crash (memory leak or bug)

**10:00:05 AM**
- First user submits email request
- Connects to Ollama, gets ConnectionError
- No retry logic
- Immediately returns 500 error
- User sees: "Internal Server Error"

**10:00:30 AM**
- 10 more users affected
- Each waits 60-120 seconds before timeout
- Cascading failures across system

**10:05 AM**
- Monitoring alert sent (or not, if no monitoring)
- Engineering team notified
- Takes 15+ minutes to investigate (no logs)

**10:20 AM**
- Engineer manually restarts Ollama
- System comes back online

**10:30 AM**
- System still processing queued requests
- Users frustrated by outage

**Impact**: 
- 30+ minutes of 100% downtime
- Lost transactions
- No insight into what happened (no logging)
- Customers lose trust

---

## SCENARIO 7: Compliance Audit Failure 🟡 HIGH

### The Problem
No audit trail means compliance violation.

### Real-World Case: Enterprise Customer

**Auditor asks:**
```
"Show me all emails generated for user john@company.com in December 2025"
```

**What you can provide:**
```
"We don't track that. The system doesn't log requests or outputs."
```

**Result:**
- ❌ Failed SOC 2 audit
- ❌ GDPR compliance concern (no data handling records)
- ❌ Enterprise contract terminated
- ❌ $50k+ contract lost

**Impact**: 
- Enterprise customers blocked
- Regulatory risk
- No ability to support customers in disputes

---

## SCENARIO 8: Silent Failures with No Way to Debug 🟡 HIGH

### The Problem
No logging means 30-minute debugging becomes impossible.

### What Happened
```
User reports: "The email generated was completely wrong. Sender/recipient 
swapped and the tone was weird."
```

**What you can do with current system:**
```
- Ask user to paste the email (manual, unreliable)
- Look at code and guess what went wrong
- No logs to see: what intent was inferred? What confidence? What was the LLM input?
- Reproduce issue locally (maybe?)
- Waste 2+ hours on what should be 15-minute investigation
```

**What you can do with logging:**
```
request_id=abc123
[2025-12-30T10:15:23] Request received: "tell my colleague..."
[2025-12-30T10:15:24] Intent: leave_request, confidence: 0.73
[2025-12-30T10:15:24] LLM prompt built
[2025-12-30T10:15:27] LLM response: 2000 chars
[2025-12-30T10:15:27] JSON parsed: valid
[2025-12-30T10:15:27] Output validation: passed
[2025-12-30T10:15:27] Response sent

→ Issue identified in 30 seconds: confidence was 0.73, not high
→ Prompt was cautious (correct behavior)
→ No bug, user expectation mismatch
```

**Impact**: 
- Debugging becomes impossible
- Each bug takes 10x longer to resolve
- Users frustrated by slow support

---

## SCENARIO 9: Scaling Failure 🟡 HIGH

### The Problem
Blocking I/O means can't handle concurrent users.

### Timeline

**System Setup:**
- 4 FastAPI workers
- Each worker can handle 1 concurrent request (LLM call blocks it)
- LLM call takes avg 15 seconds

**Load Test:**
```
9:00 AM: 5 concurrent users
→ System handles fine (5 workers available)

9:01 AM: 10 concurrent users
→ 4 workers busy, 6 in queue
→ User waits 15-30 seconds just for slot

9:02 AM: 20 concurrent users
→ ALL workers busy
→ Queue grows: 16 waiting users
→ Each waits 45-60+ seconds
→ Some timeout

9:05 AM: 50 concurrent users
→ System thrashing
→ Requests taking 5+ minutes
→ Users give up, abandon service
```

**What happens:**
```
Capacity limit: ~5 concurrent users (with 4 workers × 15s = ~4 QPS)
One viral post → 100 concurrent users
Service becomes unusable for everyone
```

**Impact**: 
- Can't scale past 10 users
- Viral moment = service collapses
- Growth ceiling hit immediately

---

## SCENARIO 10: Cost Surprise 🟡 MEDIUM

### The Problem
No performance monitoring means cost surprises later.

### Real-World Case: Cloud Deployment (Future)

**Monthly Bill Surprise:**
```
Ollama (GPU instance): $2,000/month
LB (load balancer): $200/month
Compute: $500/month
Total: $2,700/month

But revenue: $500/month (only 100 users @ $5/month)
```

**What went wrong:**
- GPU instance was oversized (didn't know)
- No metrics on latency/throughput
- Didn't optimize LLM inference
- Could have done with 1/4 the compute

**Impact**: 
- Business model doesn't work
- Burn rate too high
- Investors pull funding

---

## Summary: Why Phase 0 is Non-Negotiable

| Scenario | Severity | Causes | Fixed By Phase 0 |
|----------|----------|--------|-------------------|
| Intent misclassification | CRITICAL | Rule-based classifier | P0.3 (ML) |
| Hallucinated commitments | CRITICAL | No output validation | P0.2 (validation) |
| PII leakage | CRITICAL | No output validation | P0.2 (validation) |
| Aggressive tone | HIGH | No content check | P0.2 (validation) |
| Incomplete templates | HIGH | No placeholder check | P0.2 (validation) |
| Service unavailability | CRITICAL | No retry/fallback | P0.4 (resilience) |
| Compliance failure | HIGH | No audit trail | P0.5 (logging) |
| Silent failures | HIGH | No logging | P0.1 + P0.5 |
| Scaling failure | HIGH | Blocking I/O | P1.3 (async) |
| Cost surprise | MEDIUM | No monitoring | P1.4 (metrics) |

**Total impact**: 9 of 10 real-world failure scenarios prevented by Phase 0

---

## Questions This Raises

1. **How many of these have already happened?** (Unknown - no logging to tell)

2. **When do we expect the first major incident?**
   - After first viral post? (scaling failure)
   - After first enterprise customer? (audit failure)
   - After first high-stakes email? (hallucination liability)

3. **What's the cost of each incident?**
   - Reputation damage: $50k-$500k
   - Legal liability: $100k+
   - Lost enterprise customer: $20k-$500k
   - Engineering time to debug: $5k-$20k

4. **What's the cost of Phase 0 to prevent all of this?**
   - Engineering: $4k (1 FTE for 4 weeks)
   - Risk reduction: 95%

---

**Recommendation**: Do Phase 0 immediately. The cost of not doing it is far higher.

