import anthropic
import json
from .models import RuleResult, LLMExplanation, Confidence

class LLMExplainer:
    def __init__(self, api_key: str = None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    def generate_explanation(
        self, 
        record: dict, 
        rule_result: RuleResult
    ) -> LLMExplanation:
        """Generate human-readable explanation for a decision"""
        
        prompt = f"""You are a fraud analyst assistant. Your job is to explain 
fraud detection decisions to human reviewers in clear, professional language.

IMPORTANT: You do NOT make decisions. The decision has already been made by 
deterministic rules. You only EXPLAIN the decision.

## Transaction Data
```json
{json.dumps(record, indent=2, default=str)}
```

## Rule Engine Decision
- Rule Matched: {rule_result.matched_rule_name} ({rule_result.matched_rule_id})
- Risk Score: {rule_result.risk_score}/100
- Decision: {rule_result.decision.value}
- Rule Reason: {rule_result.rule_reason}

## Your Task
1. Explain this decision in 2-3 sentences a non-technical reviewer can understand
2. Assess your confidence in the EXPLANATION (not the decision):
   - HIGH: The rule clearly applies, explanation is straightforward
   - MEDIUM: Some ambiguity in the data or edge case
   - LOW: Missing data, conflicting signals, or unusual pattern
3. If confidence is MEDIUM or LOW, suggest 1-3 clarifying questions 
   that a human reviewer should investigate

Respond in this exact JSON format:
{{
    "human_readable_explanation": "string",
    "confidence": "HIGH" | "MEDIUM" | "LOW",
    "needs_human_review": boolean,
    "clarifying_questions": ["string"] or [],
    "additional_context": "string or null"
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse structured output
        response_text = response.content[0].text
        
        # Handle potential markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        parsed = json.loads(response_text.strip())
        
        # Apply confidence threshold for human review
        confidence = Confidence(parsed['confidence'])
        needs_review = confidence in [Confidence.LOW, Confidence.MEDIUM]
        
        return LLMExplanation(
            human_readable_explanation=parsed['human_readable_explanation'],
            confidence=confidence,
            needs_human_review=needs_review,
            clarifying_questions=parsed.get('clarifying_questions', []),
            additional_context=parsed.get('additional_context')
        )

    def generate_batch(
        self, 
        records: list[dict], 
        rule_results: list[RuleResult]
    ) -> list[LLMExplanation]:
        """Generate explanations for multiple records"""
        return [
            self.generate_explanation(record, result)
            for record, result in zip(records, rule_results)
        ]