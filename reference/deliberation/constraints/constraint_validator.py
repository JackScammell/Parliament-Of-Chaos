"""
Validate debate content against user-defined constraints.
"""

import re
from typing import List, Dict, Tuple
from ..models.schemas import ConstraintDefinition


class ConstraintValidator:
    """
    Validate debate content against constraints.
    """
    
    def __init__(self, constraints: ConstraintDefinition):
        """
        Initialize constraint validator.
        
        Args:
            constraints: Constraint definition
        """
        self.constraints = constraints
    
    def validate_statement(self, content: str) -> Tuple[bool, List[str]]:
        """
        Validate a debate statement against constraints.
        
        Args:
            content: Statement content
            
        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []
        
        # Check disallowed patterns
        for pattern in self.constraints.disallowed_patterns:
            if self._matches_pattern(content, pattern):
                violations.append(f"Contains disallowed pattern: {pattern}")
        
        # Check custom rules
        for rule_name, rule_pattern in self.constraints.custom_rules.items():
            if self._violates_custom_rule(content, rule_pattern):
                violations.append(f"Violates custom rule: {rule_name}")
        
        return len(violations) == 0, violations
    
    def validate_debate_config(self, rounds: int) -> Tuple[bool, List[str]]:
        """
        Validate debate configuration.
        
        Args:
            rounds: Number of rounds
            
        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []
        
        if self.constraints.max_rounds and rounds > self.constraints.max_rounds:
            violations.append(
                f"Rounds ({rounds}) exceed maximum ({self.constraints.max_rounds})"
            )
        
        return len(violations) == 0, violations
    
    def _matches_pattern(self, content: str, pattern: str) -> bool:
        """
        Check if content matches a disallowed pattern.
        
        Args:
            content: Content to check
            pattern: Pattern to match
            
        Returns:
            True if pattern matches
        """
        # Support both literal and regex patterns
        try:
            return bool(re.search(pattern, content, re.IGNORECASE))
        except re.error:
            # Fallback to literal match
            return pattern.lower() in content.lower()
    
    def _violates_custom_rule(self, content: str, rule: str) -> bool:
        """
        Check if content violates a custom rule.
        
        Args:
            content: Content to check
            rule: Rule pattern
            
        Returns:
            True if rule is violated
        """
        # Simple rule evaluation (can be extended)
        if rule.startswith("!"):
            # Negation: must NOT contain
            pattern = rule[1:]
            return self._matches_pattern(content, pattern)
        else:
            # Must contain
            return not self._matches_pattern(content, rule)
    
    def get_constraint_summary(self) -> Dict:
        """
        Get a summary of active constraints.
        
        Returns:
            Constraint summary dictionary
        """
        return {
            "max_rounds": self.constraints.max_rounds,
            "disallowed_patterns_count": len(self.constraints.disallowed_patterns),
            "custom_rules_count": len(self.constraints.custom_rules),
            "required_validators": self.constraints.required_validators
        }
