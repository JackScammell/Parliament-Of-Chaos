"""
Unit tests for Context Manager.
"""

import unittest
from reference.deliberation.core.context_manager import (
    ContextManager, ImmediateContext, HistoricalContext, ReferenceContext
)
from reference.deliberation.models.schemas import (
    DebateStatement, RoundSummary, AgentPosition
)


class TestImmediateContext(unittest.TestCase):
    """Test ImmediateContext functionality."""
    
    def test_create_immediate_context(self):
        """Test creating immediate context for a round."""
        ctx = ImmediateContext(round_number=1)
        self.assertEqual(ctx.round_number, 1)
        self.assertEqual(len(ctx.agent_statements), 0)
    
    def test_add_statement(self):
        """Test adding statements to immediate context."""
        ctx = ImmediateContext(round_number=1)
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="This is a good idea",
            confidence=0.8
        )
        ctx.add_statement(statement)
        self.assertEqual(len(ctx.agent_statements), 1)
        self.assertEqual(ctx.agent_statements[0].agent_id, "agent-1")
    
    def test_to_structured_json(self):
        """Test conversion to structured JSON."""
        ctx = ImmediateContext(round_number=1)
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="This is a good idea",
            confidence=0.8
        )
        ctx.add_statement(statement)
        json_data = ctx.to_structured_json()
        
        self.assertEqual(json_data["round_number"], 1)
        self.assertEqual(len(json_data["agent_statements"]), 1)
        self.assertEqual(json_data["agent_statements"][0]["agent_id"], "agent-1")
    
    def test_summarize_long_argument(self):
        """Test that long arguments are summarized."""
        ctx = ImmediateContext(round_number=1)
        long_argument = " ".join(["word"] * 100)  # 100 words
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument=long_argument,
            confidence=0.8
        )
        ctx.add_statement(statement)
        json_data = ctx.to_structured_json()
        
        # Should be summarized to ~50 words
        summarized = json_data["agent_statements"][0]["argument"]
        self.assertTrue(len(summarized) < len(long_argument))
        self.assertTrue(summarized.endswith("..."))
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        ctx = ImmediateContext(round_number=1)
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="This is a good idea",
            confidence=0.8
        )
        ctx.add_statement(statement)
        tokens = ctx.estimate_tokens()
        self.assertGreater(tokens, 0)


class TestHistoricalContext(unittest.TestCase):
    """Test HistoricalContext functionality."""
    
    def test_create_historical_context(self):
        """Test creating historical context."""
        ctx = HistoricalContext()
        self.assertEqual(len(ctx.summaries), 0)
        self.assertEqual(len(ctx.unresolved_conflicts), 0)
    
    def test_add_round_summary(self):
        """Test adding round summaries."""
        ctx = HistoricalContext()
        summary = RoundSummary(
            core_positions=["Pro", "Con"],
            major_conflicts=["Budget"],
            amendments=["Amendment-A"],
            consensus_level=0.6
        )
        ctx.add_round_summary(0, summary)
        
        self.assertEqual(len(ctx.summaries), 1)
        self.assertIn("round_0", ctx.summaries)
        self.assertEqual(len(ctx.consensus_trend), 1)
    
    def test_get_compressed_history(self):
        """Test getting compressed history."""
        ctx = HistoricalContext()
        
        # Add multiple round summaries
        for i in range(5):
            summary = RoundSummary(
                core_positions=[f"Position-{i}"],
                major_conflicts=[f"Conflict-{i}"],
                amendments=[f"Amendment-{i}"],
                consensus_level=0.5 + i * 0.1
            )
            ctx.add_round_summary(i, summary)
        
        # Get compressed history (max 3 rounds)
        compressed = ctx.get_compressed_history(max_rounds=3)
        
        self.assertIn("recent_summaries", compressed)
        self.assertIn("aggregated", compressed)
        # Should only have last 3 rounds
        self.assertEqual(len(compressed["recent_summaries"]), 3)
    
    def test_estimate_tokens(self):
        """Test token estimation for historical context."""
        ctx = HistoricalContext()
        summary = RoundSummary(
            core_positions=["Pro", "Con"],
            major_conflicts=["Budget"],
            amendments=["Amendment-A"],
            consensus_level=0.6
        )
        ctx.add_round_summary(0, summary)
        
        tokens = ctx.estimate_tokens()
        self.assertGreater(tokens, 0)


class TestReferenceContext(unittest.TestCase):
    """Test ReferenceContext functionality."""
    
    def test_create_reference_context(self):
        """Test creating reference context."""
        ctx = ReferenceContext()
        self.assertEqual(len(ctx.rules), 0)
        self.assertEqual(len(ctx.constraints), 0)
    
    def test_add_rule(self):
        """Test adding rules."""
        ctx = ReferenceContext()
        ctx.add_rule("Rule 1")
        ctx.add_rule("Rule 2")
        self.assertEqual(len(ctx.rules), 2)
    
    def test_add_constraint(self):
        """Test adding constraints."""
        ctx = ReferenceContext()
        ctx.add_constraint("Constraint 1")
        self.assertEqual(len(ctx.constraints), 1)
    
    def test_add_semantic_result(self):
        """Test adding semantic retrieval results."""
        ctx = ReferenceContext()
        result = {"text": "Similar argument", "score": 0.9}
        ctx.add_semantic_result(result)
        self.assertEqual(len(ctx.semantic_results), 1)
    
    def test_to_structured_json_limits(self):
        """Test that structured JSON limits items to top 3."""
        ctx = ReferenceContext()
        for i in range(10):
            ctx.add_rule(f"Rule {i}")
            ctx.add_constraint(f"Constraint {i}")
            ctx.add_semantic_result({"text": f"Result {i}"})
        
        json_data = ctx.to_structured_json()
        # Should limit to 3 items each
        self.assertEqual(len(json_data["rules"]), 3)
        self.assertEqual(len(json_data["constraints"]), 3)
        self.assertEqual(len(json_data["relevant_arguments"]), 3)


class TestContextManager(unittest.TestCase):
    """Test ContextManager functionality."""
    
    def test_create_context_manager(self):
        """Test creating context manager."""
        manager = ContextManager()
        self.assertIsNone(manager.immediate_context)
        self.assertIsNotNone(manager.historical_context)
    
    def test_start_new_round(self):
        """Test starting a new round."""
        manager = ContextManager()
        manager.start_new_round(1)
        
        self.assertIsNotNone(manager.immediate_context)
        self.assertEqual(manager.immediate_context.round_number, 1)
    
    def test_add_statement(self):
        """Test adding statement to current round."""
        manager = ContextManager()
        manager.start_new_round(1)
        
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="Good idea",
            confidence=0.8
        )
        manager.add_statement(statement)
        
        self.assertEqual(len(manager.immediate_context.agent_statements), 1)
    
    def test_add_statement_without_round_fails(self):
        """Test that adding statement without starting round fails."""
        manager = ContextManager()
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="Good idea",
            confidence=0.8
        )
        
        with self.assertRaises(RuntimeError):
            manager.add_statement(statement)
    
    def test_compress_round(self):
        """Test compressing a round."""
        manager = ContextManager()
        manager.start_new_round(0)
        
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="Good idea",
            confidence=0.8
        )
        manager.add_statement(statement)
        
        summary = RoundSummary(
            core_positions=["Support"],
            major_conflicts=[],
            amendments=[],
            consensus_level=0.9
        )
        
        manager.compress_round(summary)
        
        # Immediate context should be cleared
        self.assertIsNone(manager.immediate_context)
        # Historical context should have the summary
        self.assertEqual(len(manager.historical_context.summaries), 1)
    
    def test_build_agent_context(self):
        """Test building context for an agent."""
        manager = ContextManager()
        manager.start_new_round(1)
        
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="Good idea",
            confidence=0.8
        )
        manager.add_statement(statement)
        
        position = AgentPosition(
            stance="Pro",
            confidence=0.85,
            influence_score=1.0,
            stability_index=1.0
        )
        
        context = manager.build_agent_context(
            agent_id="agent-2",
            agent_position=position,
            topic="Test Topic"
        )
        
        self.assertIn("round", context)
        self.assertIn("topic", context)
        self.assertIn("immediate_context", context)
        self.assertIn("historical_summary", context)
        self.assertIn("your_position", context)
    
    def test_build_prompt_with_context(self):
        """Test building optimized prompt with context."""
        manager = ContextManager()
        manager.start_new_round(1)
        
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="Good idea",
            confidence=0.8
        )
        manager.add_statement(statement)
        
        prompt = manager.build_prompt_with_context(
            agent_id="agent-2",
            role="Debater",
            objective="Provide your position",
            topic="Test Topic",
            max_tokens=500
        )
        
        self.assertIn("ROLE: Debater", prompt)
        self.assertIn("OBJECTIVE: Provide your position", prompt)
        self.assertIn("ROUND: 1", prompt)
        self.assertIn("IMMEDIATE CONTEXT:", prompt)
        self.assertIn("HISTORICAL SUMMARY:", prompt)
    
    def test_estimate_context_tokens(self):
        """Test estimating context tokens."""
        manager = ContextManager()
        manager.start_new_round(1)
        
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="Good idea",
            confidence=0.8
        )
        manager.add_statement(statement)
        
        stats = manager.estimate_context_tokens("agent-2")
        
        self.assertIn("immediate", stats)
        self.assertIn("historical", stats)
        self.assertIn("reference", stats)
        self.assertIn("total", stats)
        self.assertGreater(stats["total"], 0)
    
    def test_track_token_usage(self):
        """Test tracking token usage over time."""
        manager = ContextManager()
        manager.start_new_round(1)
        
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="Good idea",
            confidence=0.8
        )
        manager.add_statement(statement)
        
        manager.track_token_usage("agent-1")
        manager.track_token_usage("agent-2")
        
        stats = manager.get_token_statistics()
        
        self.assertIn("average_total", stats)
        self.assertIn("calls_tracked", stats)
        self.assertEqual(stats["calls_tracked"], 2)
    
    def test_add_semantic_retrieval_result(self):
        """Test adding semantic retrieval results."""
        manager = ContextManager()
        results = [
            {"text": "Result 1", "score": 0.9},
            {"text": "Result 2", "score": 0.8},
            {"text": "Result 3", "score": 0.7},
            {"text": "Result 4", "score": 0.6}
        ]
        
        manager.add_semantic_retrieval_result("test query", results, top_k=3)
        
        # Should only add top 3
        self.assertEqual(len(manager.reference_context.semantic_results), 3)
    
    def test_reset(self):
        """Test resetting context manager."""
        manager = ContextManager()
        manager.start_new_round(1)
        
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support",
            argument="Good idea",
            confidence=0.8
        )
        manager.add_statement(statement)
        
        manager.reset()
        
        self.assertIsNone(manager.immediate_context)
        self.assertEqual(len(manager.historical_context.summaries), 0)
        self.assertEqual(manager._current_round, 0)


class TestTokenReduction(unittest.TestCase):
    """Test token reduction effectiveness."""
    
    def test_token_reduction_with_multiple_rounds(self):
        """Test that token usage stays bounded with multiple rounds."""
        manager = ContextManager(max_historical_rounds=3)
        
        # Simulate 10 rounds
        for round_num in range(10):
            manager.start_new_round(round_num)
            
            # Add multiple statements
            for i in range(5):
                statement = DebateStatement(
                    agent_id=f"agent-{i}",
                    position=f"Position {round_num}-{i}",
                    argument=f"Argument for position {round_num}-{i}",
                    confidence=0.7 + i * 0.05
                )
                manager.add_statement(statement)
            
            # Compress round
            summary = RoundSummary(
                core_positions=[f"Position-{round_num}"],
                major_conflicts=[],
                amendments=[],
                consensus_level=0.6 + round_num * 0.03
            )
            manager.compress_round(summary)
        
        # Start new round and check tokens
        manager.start_new_round(10)
        stats = manager.estimate_context_tokens("agent-1")
        
        # Historical context should be bounded (only last 3 rounds)
        # Even though we had 10 rounds
        historical_tokens = stats["historical"]
        
        # Historical tokens should be reasonable (not growing unbounded)
        # This is a rough check - actual values depend on compression
        self.assertLess(historical_tokens, 500)  # Should be well under 500 tokens


if __name__ == "__main__":
    unittest.main()
