import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import shutil

class ConfigManager:
    """Manage rule configurations with versioning and validation"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

    def load_rules(self, version: str = "v1") -> Dict[str, Any]:
        """Load rules from YAML file"""
        config_path = self.config_dir / f"rules_{version}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def save_rules(self, rules_config: Dict[str, Any], version: str = "v1", backup: bool = True) -> None:
        """Save rules to YAML file with optional backup"""
        config_path = self.config_dir / f"rules_{version}.yaml"

        # Create backup if file exists
        if backup and config_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"rules_{version}_{timestamp}.yaml"
            shutil.copy2(config_path, backup_path)

        # Save new config
        with open(config_path, 'w') as f:
            yaml.safe_dump(rules_config, f, default_flow_style=False, sort_keys=False)

    def validate_rule(self, rule: Dict[str, Any]) -> List[str]:
        """Validate a single rule and return list of errors"""
        errors = []

        # Required fields
        required = ['id', 'name', 'logic', 'outcome']
        for field in required:
            if field not in rule:
                errors.append(f"Missing required field: {field}")

        # Validate conditions (except for ALWAYS logic)
        if rule.get('logic') != 'ALWAYS':
            if 'conditions' not in rule or not rule['conditions']:
                errors.append("Non-ALWAYS rules must have at least one condition")
            else:
                for i, cond in enumerate(rule['conditions']):
                    if 'field' not in cond:
                        errors.append(f"Condition {i+1}: missing 'field'")
                    if 'operator' not in cond:
                        errors.append(f"Condition {i+1}: missing 'operator'")
                    if 'value' not in cond:
                        errors.append(f"Condition {i+1}: missing 'value'")

        # Validate logic
        if 'logic' in rule and rule['logic'] not in ['AND', 'OR', 'ALWAYS']:
            errors.append(f"Invalid logic: {rule['logic']}. Must be AND, OR, or ALWAYS")

        # Validate outcome
        if 'outcome' in rule:
            outcome = rule['outcome']

            # Risk score
            if 'risk_score' not in outcome:
                errors.append("Outcome missing 'risk_score'")
            elif not isinstance(outcome['risk_score'], int) or not 0 <= outcome['risk_score'] <= 100:
                errors.append("risk_score must be integer 0-100")

            # Decision
            if 'decision' not in outcome:
                errors.append("Outcome missing 'decision'")
            elif outcome['decision'] not in ['ALLOW', 'REVIEW', 'BLOCK']:
                errors.append(f"Invalid decision: {outcome['decision']}. Must be ALLOW, REVIEW, or BLOCK")

            # Reason
            if 'reason' not in outcome:
                errors.append("Outcome missing 'reason'")

        return errors

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate entire config and return list of errors"""
        errors = []

        # Check required top-level fields
        if 'rules' not in config:
            errors.append("Config missing 'rules' section")
            return errors

        rules = config['rules']
        if not isinstance(rules, list) or len(rules) == 0:
            errors.append("'rules' must be a non-empty list")
            return errors

        # Check for DEFAULT rule at end
        has_default = False
        for i, rule in enumerate(rules):
            if rule.get('logic') == 'ALWAYS':
                if i != len(rules) - 1:
                    errors.append(f"ALWAYS rule '{rule.get('id')}' at position {i+1} should be last")
                has_default = True

        if not has_default:
            errors.append("Config must have a DEFAULT rule with logic: ALWAYS at the end")

        # Check for duplicate IDs
        ids = [r.get('id') for r in rules if 'id' in r]
        duplicates = [id for id in ids if ids.count(id) > 1]
        if duplicates:
            errors.append(f"Duplicate rule IDs found: {set(duplicates)}")

        # Validate each rule
        for i, rule in enumerate(rules):
            rule_errors = self.validate_rule(rule)
            for err in rule_errors:
                errors.append(f"Rule {i+1} ({rule.get('id', 'unknown')}): {err}")

        return errors

    def get_next_rule_id(self, config: Dict[str, Any]) -> str:
        """Generate next available rule ID"""
        rules = config.get('rules', [])
        existing_ids = [r.get('id', '') for r in rules if r.get('id', '').startswith('RULE_')]

        # Extract numbers from RULE_XXX format
        numbers = []
        for rule_id in existing_ids:
            try:
                num = int(rule_id.split('_')[1])
                numbers.append(num)
            except (IndexError, ValueError):
                continue

        # Get next number
        next_num = max(numbers, default=0) + 1
        return f"RULE_{next_num:03d}"

    def add_rule(self, rule: Dict[str, Any], version: str = "v1", position: Optional[int] = None) -> None:
        """Add a new rule to config at specified position (default: before DEFAULT)"""
        config = self.load_rules(version)
        rules = config['rules']

        # Find DEFAULT rule position
        default_idx = len(rules)
        for i, r in enumerate(rules):
            if r.get('logic') == 'ALWAYS':
                default_idx = i
                break

        # Insert at position or before DEFAULT
        insert_pos = position if position is not None else default_idx
        rules.insert(insert_pos, rule)

        config['rules'] = rules
        self.save_rules(config, version)

    def update_rule(self, rule_id: str, updated_rule: Dict[str, Any], version: str = "v1") -> bool:
        """Update an existing rule"""
        config = self.load_rules(version)
        rules = config['rules']

        for i, r in enumerate(rules):
            if r.get('id') == rule_id:
                rules[i] = updated_rule
                config['rules'] = rules
                self.save_rules(config, version)
                return True

        return False

    def delete_rule(self, rule_id: str, version: str = "v1") -> bool:
        """Delete a rule by ID"""
        config = self.load_rules(version)
        rules = config['rules']

        new_rules = [r for r in rules if r.get('id') != rule_id]
        if len(new_rules) < len(rules):
            config['rules'] = new_rules
            self.save_rules(config, version)
            return True

        return False

    def reorder_rules(self, rule_ids: List[str], version: str = "v1") -> None:
        """Reorder rules based on list of IDs"""
        config = self.load_rules(version)
        rules = config['rules']

        # Create mapping of ID to rule
        rule_map = {r.get('id'): r for r in rules}

        # Reorder based on provided IDs
        new_rules = [rule_map[rid] for rid in rule_ids if rid in rule_map]

        config['rules'] = new_rules
        self.save_rules(config, version)
