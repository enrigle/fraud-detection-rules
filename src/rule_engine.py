import yaml
from typing import Any
from .models import RuleResult, Decision

class RuleEngine:
    OPERATORS = {
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        "in": lambda a, b: a in b,
        "not_in": lambda a, b: a not in b,
    }

    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.rules = self.config['rules']
        self.version = self.config['version']

    def evaluate_condition(self, condition: dict, record: dict) -> bool:
        field = condition['field']
        operator = condition['operator']
        expected_value = condition['value']
        actual_value = record.get(field)
        
        if actual_value is None:
            return False
        
        op_func = self.OPERATORS.get(operator)
        if not op_func:
            raise ValueError(f"Unknown operator: {operator}")
        
        return op_func(actual_value, expected_value)

    def evaluate_rule(self, rule: dict, record: dict) -> bool:
        if rule.get('logic') == 'ALWAYS':
            return True
        
        conditions = rule.get('conditions', [])
        if not conditions:
            return False
        
        results = [self.evaluate_condition(c, record) for c in conditions]
        
        if rule.get('logic') == 'AND':
            return all(results)
        elif rule.get('logic') == 'OR':
            return any(results)
        return False

    def evaluate(self, record: dict) -> RuleResult:
        """Evaluate a single record against all rules"""
        transaction_id = record.get('transaction_id', 'unknown')
        
        for rule in self.rules:
            if self.evaluate_rule(rule, record):
                outcome = rule['outcome']
                return RuleResult(
                    transaction_id=transaction_id,
                    matched_rule_id=rule['id'],
                    matched_rule_name=rule['name'],
                    risk_score=outcome['risk_score'],
                    decision=Decision(outcome['decision']),
                    rule_reason=outcome['reason']
                )
        
        # Should never reach here if DEFAULT rule exists
        raise ValueError("No matching rule found and no DEFAULT rule defined")

    def evaluate_batch(self, records: list[dict]) -> list[RuleResult]:
        """Evaluate multiple records"""
        return [self.evaluate(record) for record in records]