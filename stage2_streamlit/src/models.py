from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum

class Decision(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"

class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RuleResult(BaseModel):
    """Output from rule engine (deterministic)"""
    transaction_id: str
    matched_rule_id: str
    matched_rule_name: str
    risk_score: int = Field(ge=0, le=100)
    decision: Decision
    rule_reason: str

class LLMExplanation(BaseModel):
    """Structured output from LLM"""
    human_readable_explanation: str
    confidence: Confidence
    needs_human_review: bool
    clarifying_questions: list[str] = Field(default_factory=list)
    additional_context: Optional[str] = None

class FinalDecisionOutput(BaseModel):
    """Combined output for each transaction"""
    transaction_id: str
    risk_score: int
    decision: Decision
    rule_matched: str
    rule_reason: str
    llm_explanation: str
    confidence: Confidence
    needs_human_review: bool
    clarifying_questions: list[str]