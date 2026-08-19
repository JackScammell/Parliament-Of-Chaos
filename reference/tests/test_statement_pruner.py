"""
Unit tests for statement deduplication and pruning.
"""

import unittest
from reference.deliberation.core.statement_pruner import (
    StatementDeduplicator, ContextPruner
)
from reference.deliberation.models.schemas import DebateStatement


class TestStatementDeduplicator(unittest.TestCase):
    """Test StatementDeduplicator functionality."""
    
    def test_create_deduplicator(self):
        """Test creating statement deduplicator."""
        dedup = StatementDeduplicator()
        self.assertIsNotNone(dedup)
    
    def test_is_duplicate_first_statement(self):
        """Test first statement is never duplicate."""
        dedup = StatementDeduplicator()
        stmt = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="This is a test argument",
            confidence=0.8
        )
        self.assertFalse(dedup.is_duplicate(stmt))
    
    def test_is_duplicate_different_statement(self):
        """Test different statement is not duplicate."""
        dedup = StatementDeduplicator()
        stmt1 = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="This is a test argument",
            confidence=0.8
        )
        stmt2 = DebateStatement(
            agent_id="agent-1",
            position="Oppose",
            argument="This is completely different content",
            confidence=0.7
        )
        dedup.is_duplicate(stmt1)
        self.assertFalse(dedup.is_duplicate(stmt2))
    
    def test_is_duplicate_similar_statement(self):
        """Test similar statement is detected as duplicate."""
        dedup = StatementDeduplicator(similarity_threshold=0.7)  # Lower threshold
        stmt1 = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="We need to reduce carbon emissions immediately",
            confidence=0.8
        )
        stmt2 = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="We need to reduce carbon emissions immediately",  # Exact same
            confidence=0.9
        )
        dedup.is_duplicate(stmt1)
        # Exact same - should be duplicate
        is_dup = dedup.is_duplicate(stmt2)
        self.assertTrue(is_dup)
    
    def test_different_agents_not_duplicate(self):
        """Test statements from different agents are independent."""
        dedup = StatementDeduplicator()
        stmt1 = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="This is a test argument",
            confidence=0.8
        )
        stmt2 = DebateStatement(
            agent_id="agent-2",
            position="Support",
            argument="This is a test argument",
            confidence=0.8
        )
        dedup.is_duplicate(stmt1)
        # Different agent, so not duplicate
        self.assertFalse(dedup.is_duplicate(stmt2))
    
    def test_reset(self):
        """Test reset clears seen statements."""
        dedup = StatementDeduplicator()
        stmt = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="This is a test argument",
            confidence=0.8
        )
        dedup.is_duplicate(stmt)
        dedup.reset()
        # After reset, same statement should not be duplicate
        self.assertFalse(dedup.is_duplicate(stmt))


class TestContextPruner(unittest.TestCase):
    """Test ContextPruner functionality."""
    
    def test_create_pruner(self):
        """Test creating context pruner."""
        pruner = ContextPruner()
        self.assertIsNotNone(pruner)
    
    def test_prune_statements_empty(self):
        """Test pruning empty list."""
        pruner = ContextPruner()
        pruned = pruner.prune_statements([])
        self.assertEqual(len(pruned), 0)
    
    def test_prune_statements_high_confidence(self):
        """Test high confidence statements are kept."""
        pruner = ContextPruner(min_confidence=0.5)
        statements = [
            DebateStatement(
                agent_id="agent-1",
                position="Support",
                argument="High confidence argument",
                confidence=0.9
            ),
            DebateStatement(
                agent_id="agent-2",
                position="Oppose",
                argument="Another high confidence argument",
                confidence=0.8
            )
        ]
        pruned = pruner.prune_statements(statements)
        self.assertEqual(len(pruned), 2)
    
    def test_prune_statements_low_confidence(self):
        """Test low confidence statements are pruned."""
        pruner = ContextPruner(min_confidence=0.5)
        statements = [
            DebateStatement(
                agent_id="agent-1",
                position="Support",
                argument="High confidence argument",
                confidence=0.9
            ),
            DebateStatement(
                agent_id="agent-2",
                position="Oppose",
                argument="Low confidence argument",
                confidence=0.3
            )
        ]
        pruned = pruner.prune_statements(statements)
        self.assertEqual(len(pruned), 1)
        self.assertEqual(pruned[0].agent_id, "agent-1")
    
    def test_prune_statements_high_influence(self):
        """Test high influence agents kept even with low confidence."""
        pruner = ContextPruner(min_confidence=0.5, keep_high_influence=True)
        statements = [
            DebateStatement(
                agent_id="agent-1",
                position="Support",
                argument="High influence but low confidence",
                confidence=0.3
            )
        ]
        agent_influence = {"agent-1": 0.9}  # High influence
        pruned = pruner.prune_statements(statements, agent_influence=agent_influence)
        # Should be kept due to high influence
        self.assertEqual(len(pruned), 1)
    
    def test_should_prune_conflict_resolved(self):
        """Test resolved conflicts are identified."""
        pruner = ContextPruner()
        conflict = "Budget allocation disagreement"
        resolved = {"budget allocation"}
        should_prune = pruner.should_prune_conflict(conflict, resolved)
        self.assertTrue(should_prune)
    
    def test_should_prune_conflict_unresolved(self):
        """Test unresolved conflicts are not pruned."""
        pruner = ContextPruner()
        conflict = "Timeline disagreement"
        resolved = {"budget allocation"}
        should_prune = pruner.should_prune_conflict(conflict, resolved)
        self.assertFalse(should_prune)
    
    def test_get_pruning_stats(self):
        """Test getting pruning statistics."""
        pruner = ContextPruner(min_confidence=0.5)
        statements = [
            DebateStatement(
                agent_id="agent-1",
                position="Support",
                argument="High confidence",
                confidence=0.9
            ),
            DebateStatement(
                agent_id="agent-2",
                position="Oppose",
                argument="Low confidence",
                confidence=0.3
            )
        ]
        pruner.prune_statements(statements)
        stats = pruner.get_pruning_stats()
        self.assertEqual(stats["statements_pruned"], 1)


if __name__ == "__main__":
    unittest.main()
