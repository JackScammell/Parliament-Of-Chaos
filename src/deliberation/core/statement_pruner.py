"""
Statement deduplication and pruning for Parliament of Chaos.
Detects and removes redundant or low-value statements to reduce tokens.
"""

import logging
from typing import List, Set, Dict, Optional
from ..models.schemas import DebateStatement

logger = logging.getLogger(__name__)


class StatementDeduplicator:
    """
    Detects and removes redundant debate statements.
    Uses simple text similarity to identify duplicates.
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize statement deduplicator.
        
        Args:
            similarity_threshold: Minimum similarity (0-1) to consider duplicate
        """
        self.similarity_threshold = similarity_threshold
        self._seen_statements: Dict[str, List[str]] = {}  # agent_id -> [normalized statements]
        logger.info(f"StatementDeduplicator initialized with threshold={similarity_threshold}")
    
    def is_duplicate(self, statement: DebateStatement) -> bool:
        """
        Check if statement is a duplicate of a previous one.
        
        Args:
            statement: Statement to check
            
        Returns:
            True if statement is likely a duplicate
        """
        normalized = self._normalize_text(statement.argument)
        
        if statement.agent_id not in self._seen_statements:
            self._seen_statements[statement.agent_id] = []
        
        # Check against previous statements from same agent
        for prev_statement in self._seen_statements[statement.agent_id]:
            similarity = self._calculate_similarity(normalized, prev_statement)
            if similarity >= self.similarity_threshold:
                logger.info(
                    f"Duplicate detected for {statement.agent_id}: "
                    f"similarity={similarity:.2f}"
                )
                return True
        
        # Not a duplicate, remember it
        self._seen_statements[statement.agent_id].append(normalized)
        return False
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase and remove extra whitespace
        normalized = " ".join(text.lower().split())
        return normalized
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple word-based similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def reset(self):
        """Reset seen statements."""
        self._seen_statements.clear()
        logger.info("StatementDeduplicator reset")


class ContextPruner:
    """
    Prunes low-value statements from context to reduce tokens.
    Removes statements that are:
    - Low confidence (< threshold)
    - Resolved (conflicts that have been addressed)
    - Redundant (detected as duplicates)
    """
    
    def __init__(
        self, 
        min_confidence: float = 0.5,
        keep_high_influence: bool = True
    ):
        """
        Initialize context pruner.
        
        Args:
            min_confidence: Minimum confidence to keep statements
            keep_high_influence: Whether to keep high-influence agents regardless
        """
        self.min_confidence = min_confidence
        self.keep_high_influence = keep_high_influence
        self._pruned_count = 0
        logger.info(
            f"ContextPruner initialized: "
            f"min_confidence={min_confidence}, "
            f"keep_high_influence={keep_high_influence}"
        )
    
    def prune_statements(
        self, 
        statements: List[DebateStatement],
        resolved_issues: Optional[Set[str]] = None,
        agent_influence: Optional[Dict[str, float]] = None
    ) -> List[DebateStatement]:
        """
        Prune low-value statements from list.
        
        Args:
            statements: List of statements to prune
            resolved_issues: Set of resolved issue keywords
            agent_influence: Optional dict of agent influence scores
            
        Returns:
            Pruned list of statements
        """
        if not statements:
            return statements
        
        resolved_issues = resolved_issues or set()
        agent_influence = agent_influence or {}
        
        pruned = []
        for stmt in statements:
            # Keep if high confidence
            if stmt.confidence >= self.min_confidence:
                pruned.append(stmt)
                continue
            
            # Keep if high influence agent (even with low confidence)
            if self.keep_high_influence:
                influence = agent_influence.get(stmt.agent_id, 0.0)
                if influence >= 0.7:  # High influence threshold
                    pruned.append(stmt)
                    continue
            
            # Otherwise, prune
            self._pruned_count += 1
            logger.debug(
                f"Pruned statement from {stmt.agent_id}: "
                f"confidence={stmt.confidence:.2f}"
            )
        
        pruned_amount = len(statements) - len(pruned)
        if pruned_amount > 0:
            logger.info(f"Pruned {pruned_amount} low-confidence statements")
        
        return pruned
    
    def should_prune_conflict(self, conflict: str, resolved_issues: Set[str]) -> bool:
        """
        Check if a conflict should be pruned (already resolved).
        
        Args:
            conflict: Conflict description
            resolved_issues: Set of resolved issue keywords
            
        Returns:
            True if conflict should be pruned
        """
        conflict_lower = conflict.lower()
        for resolved in resolved_issues:
            if resolved.lower() in conflict_lower:
                return True
        return False
    
    def get_pruning_stats(self) -> Dict:
        """Get pruning statistics."""
        return {
            "statements_pruned": self._pruned_count,
            "min_confidence_threshold": self.min_confidence
        }
