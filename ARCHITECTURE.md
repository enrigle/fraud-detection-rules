# Architecture

## Overview

3-layer fraud detection system that separates decision-making from explanation.

**Core principle**: The LLM never influences risk scores or decisions. It only translates deterministic rule outputs into human-readable explanations.

## System Flow

```
Transaction Data
      ↓
[1. Rule Engine] ──→ RuleResult (risk_score, decision, matched_rule)
      ↓
[2. LLM Explainer] ──→ LLMExplanation (human_text, confidence, review_flag)
      ↓
[3. Final Output] ──→ Combined result for human review
```

## Components

### 1. Rule Engine (`src/rule_engine.py`)

**Purpose**: Deterministic decision-making

**Input**: Transaction dictionary (amount, velocity, country, etc.)

**Output**: `RuleResult` object with:
- `risk_score`: 0-100 integer
- `decision`: APPROVE | REVIEW | DECLINE
- `matched_rule_name`: Which rule triggered
- `rule_reason`: Technical reason from YAML

**How it works**:
1. Loads rules from `config/rules_v1.yaml`
2. Evaluates conditions top-to-bottom (first match wins)
3. Applies rule logic: AND/OR/ALWAYS
4. Supports operators: `>`, `<`, `>=`, `<=`, `==`, `!=`, `in`, `not_in`
5. Returns result immediately on first match

**Example rule**:
```yaml
- id: R003
  name: HIGH_VALUE_CRYPTO
  conditions:
    - field: transaction_amount
      operator: ">"
      value: 10000
    - field: merchant_category
      operator: "=="
      value: "crypto"
  logic: AND
  outcome:
    risk_score: 95
    decision: DECLINE
    reason: "High-value crypto transaction exceeds risk threshold"
```

**Anti-hallucination guarantee**: No LLM calls. Pure Python logic.

### 2. LLM Explainer (`src/llm_explainer.py`)

**Purpose**: Human-readable explanations

**Input**:
- Original transaction data
- `RuleResult` from step 1

**Output**: `LLMExplanation` object with:
- `human_readable_explanation`: 2-3 sentence summary
- `confidence`: HIGH | MEDIUM | LOW (quality of explanation, not decision)
- `needs_human_review`: Boolean flag
- `clarifying_questions`: List of questions for reviewers

**How it works**:
1. Sends transaction + existing `RuleResult` to Claude
2. Prompt explicitly states: "You do NOT make decisions. Explain the existing decision."
3. Uses structured JSON output (Pydantic validation)
4. Confidence assesses explanation clarity, not transaction risk
5. Auto-flags MEDIUM/LOW confidence for human review

**Example prompt structure**:
```
Transaction Data: {transaction JSON}
Rule Decision Already Made:
  - Risk Score: 95/100
  - Decision: DECLINE
  - Reason: High-value crypto transaction

Your Task: Explain this decision in plain language.
```

**Anti-hallucination guarantee**: LLM receives pre-computed decision as input, cannot override.

### 3. Data Models (`src/models.py`)

**Purpose**: Enforce structured I/O, prevent hallucinations

**Key models**:

```python
class Decision(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    DECLINE = "DECLINE"

class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RuleResult(BaseModel):
    transaction_id: str
    matched_rule_id: str
    matched_rule_name: str
    risk_score: int  # 0-100
    decision: Decision
    rule_reason: str

class LLMExplanation(BaseModel):
    human_readable_explanation: str
    confidence: Confidence
    needs_human_review: bool
    clarifying_questions: list[str]
    additional_context: str | None

class FinalDecisionOutput(BaseModel):
    transaction_id: str
    risk_score: int
    decision: Decision
    rule_matched: str
    rule_reason: str
    llm_explanation: str
    confidence: Confidence
    needs_human_review: bool
    clarifying_questions: list[str]
```

**Anti-hallucination guarantee**: Pydantic validates all LLM outputs. Enums prevent arbitrary values.

## Rule Configuration (`config/rules_v1.yaml`)

**Decision tree structure**:
- Rules evaluated top-to-bottom
- First match wins
- Must end with DEFAULT rule (`logic: ALWAYS`)

**Rule anatomy**:
```yaml
- id: R001                    # Unique identifier
  name: VELOCITY_SPIKE        # Human-readable name
  conditions:                 # List of conditions to check
    - field: transaction_velocity_24h
      operator: ">"
      value: 10
    - field: country_mismatch
      operator: "=="
      value: true
  logic: AND                  # AND | OR | ALWAYS
  outcome:
    risk_score: 85            # 0-100
    decision: REVIEW          # APPROVE | REVIEW | DECLINE
    reason: "Unusual velocity pattern with country mismatch"
```

**Common patterns**:
- High-value crypto → DECLINE
- Velocity spike + country mismatch → REVIEW
- Gambling transactions → REVIEW
- Everything else → DEFAULT (APPROVE/REVIEW based on risk)

## Why This Architecture?

### Problem: LLM Hallucinations in Decision Systems

Traditional approach (bad):
```
Transaction → LLM → Risk Score + Decision
```
**Issue**: LLM can hallucinate scores, misinterpret thresholds, or generate inconsistent decisions.

### Solution: Separation of Concerns

Our approach (good):
```
Transaction → Rule Engine → Decision (deterministic)
                    ↓
            Decision → LLM → Explanation (non-critical)
```

**Benefits**:
1. **Auditability**: Every decision traces to a specific YAML rule
2. **Consistency**: Same transaction always gets same score/decision
3. **Safety**: LLM hallucinations only affect explanation text, not outcomes
4. **Testability**: Rule engine has 100% deterministic unit tests
5. **Regulatory compliance**: Can prove decision logic to auditors

### What Could Go Wrong?

**If LLM made decisions**:
- "This $5000 transaction seems fine" → APPROVE (missed fraud)
- "I'm 87.3% confident" → Where did 87.3% come from?
- Same transaction, different scores on retry → Inconsistent

**With our architecture**:
- Rule engine: $5000 crypto → 95/100 risk → DECLINE (always)
- LLM: "This was declined because..." → If hallucinated, reviewer sees it's wrong
- Retries produce identical decisions, possibly different explanation wording

## Example Execution

**Input transaction**:
```json
{
  "transaction_id": "abc123",
  "transaction_amount": 15000,
  "merchant_category": "crypto",
  "transaction_velocity_24h": 2,
  "country_mismatch": false
}
```

**Step 1: Rule Engine** evaluates rules, matches HIGH_VALUE_CRYPTO:
```python
RuleResult(
    transaction_id="abc123",
    matched_rule_id="R003",
    matched_rule_name="HIGH_VALUE_CRYPTO",
    risk_score=95,
    decision=Decision.DECLINE,
    rule_reason="High-value crypto transaction exceeds risk threshold"
)
```

**Step 2: LLM Explainer** receives transaction + RuleResult, generates:
```python
LLMExplanation(
    human_readable_explanation="This $15,000 cryptocurrency purchase was automatically declined due to the high transaction amount in a high-risk merchant category. Crypto transactions above $10,000 require additional verification.",
    confidence=Confidence.HIGH,
    needs_human_review=False,
    clarifying_questions=[],
    additional_context=None
)
```

**Step 3: Final Output** combines both:
```python
FinalDecisionOutput(
    transaction_id="abc123",
    risk_score=95,
    decision=Decision.DECLINE,
    rule_matched="HIGH_VALUE_CRYPTO",
    rule_reason="High-value crypto transaction exceeds risk threshold",
    llm_explanation="This $15,000 cryptocurrency purchase was...",
    confidence=Confidence.HIGH,
    needs_human_review=False,
    clarifying_questions=[]
)
```

## Anti-Hallucination Checklist

- ✅ Rule engine never calls LLM
- ✅ LLM receives pre-computed decision as input
- ✅ Pydantic validates all LLM outputs
- ✅ Enums prevent arbitrary decision values
- ✅ Confidence assesses explanation quality, not transaction risk
- ✅ Same transaction always produces same risk_score + decision
- ✅ LLM hallucinations only affect explanation text (non-critical)
- ✅ Human reviewers see both rule reason + LLM explanation (can spot discrepancies)

## Extending the System

### Adding new rules
1. Edit `config/rules_v1.yaml`
2. Add rule with conditions/logic/outcome
3. Place before DEFAULT rule
4. No code changes needed

### Modifying LLM prompt
1. Edit `src/llm_explainer.py` → `generate_explanation()`
2. Update prompt string
3. Keep "You do NOT make decisions" instruction
4. Maintain JSON output structure

### Adding new data fields
1. Update `src/data_generator.py` to include field
2. Add field to transaction dictionaries
3. Reference field in YAML rule conditions
4. No model changes needed (dicts are flexible)

### Testing
```bash
# Test rule engine (no API calls)
python -c "from src.rule_engine import RuleEngine; print(RuleEngine('config/rules_v1.yaml').evaluate({'transaction_amount': 500, 'merchant_category': 'retail'}))"

# Test full pipeline (requires API key)
jupyter nbconvert --to notebook --execute decision_engine.ipynb
```
