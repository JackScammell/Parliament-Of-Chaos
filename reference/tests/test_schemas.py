"""
Unit tests for Parliament of Chaos deliberation system schemas.
"""

import unittest
from reference.deliberation.models.schemas import (
    DebateStatement, Vote, RoundSummary, DebateState,
    MetaAnalysis, DeliberationConfig, AgentAlignment, AgentPosition
)


class TestSchemas(unittest.TestCase):
    """Test all schema definitions and validation."""
    
    def test_debate_statement_valid(self):
        """Test valid DebateStatement creation."""
        statement = DebateStatement(
            agent_id="agent-1",
            position="Support the proposal",
            argument="This is beneficial because...",
            amendment=None,
            references=["source1", "source2"],
            confidence=0.85
        )
        self.assertEqual(statement.agent_id, "agent-1")
        self.assertEqual(statement.confidence, 0.85)
    
    def test_debate_statement_confidence_clamping(self):
        """Test that confidence values are clamped to [0, 1]."""
        statement = DebateStatement(
            agent_id="agent-1",
            position="Test",
            argument="Test argument",
            confidence=1.5  # Should be clamped to 1.0
        )
        self.assertEqual(statement.confidence, 1.0)
        
        statement = DebateStatement(
            agent_id="agent-1",
            position="Test",
            argument="Test argument",
            confidence=-0.5  # Should be clamped to 0.0
        )
        self.assertEqual(statement.confidence, 0.0)
    
    def test_vote_valid(self):
        """Test valid Vote creation."""
        vote = Vote(
            agent_id="agent-1",
            vote="approve",
            reasoning="I support this proposal",
            confidence=0.9
        )
        self.assertEqual(vote.vote, "approve")
        self.assertEqual(vote.confidence, 0.9)
    
    def test_vote_invalid_type(self):
        """Test that invalid vote types are rejected."""
        with self.assertRaises(Exception):
            Vote(
                agent_id="agent-1",
                vote="maybe",  # Invalid - must be approve/reject/abstain
                reasoning="Test",
                confidence=0.5
            )
    
    def test_round_summary_valid(self):
        """Test valid RoundSummary creation."""
        summary = RoundSummary(
            core_positions=["Position A", "Position B"],
            major_conflicts=["Conflict over X"],
            amendments=["Amendment 1"],
            consensus_level=0.7
        )
        self.assertEqual(len(summary.core_positions), 2)
        self.assertEqual(summary.consensus_level, 0.7)
    
    def test_agent_alignment_valid(self):
        """Test valid AgentAlignment creation."""
        alignment = AgentAlignment(
            economic=0.5,
            social=-0.3,
            risk_tolerance=0.8
        )
        self.assertEqual(alignment.economic, 0.5)
        self.assertEqual(alignment.social, -0.3)
    
    def test_agent_alignment_clamping(self):
        """Test that alignment values are clamped to [-1, 1]."""
        alignment = AgentAlignment(
            economic=2.0,  # Should be clamped to 1.0
            social=-1.5,   # Should be clamped to -1.0
            risk_tolerance=0.5
        )
        self.assertEqual(alignment.economic, 1.0)
        self.assertEqual(alignment.social, -1.0)
    
    def test_agent_position_valid(self):
        """Test valid AgentPosition creation."""
        position = AgentPosition(
            stance="Support",
            confidence=0.8,
            influence_score=1.2,
            stability_index=0.9
        )
        self.assertEqual(position.stance, "Support")
        self.assertEqual(position.influence_score, 1.2)
    
    def test_debate_state_initial(self):
        """Test DebateState initialization."""
        state = DebateState()
        self.assertEqual(state.round, 0)
        self.assertEqual(len(state.agent_positions), 0)
        self.assertEqual(len(state.open_amendments), 0)
    
    def test_meta_analysis_valid(self):
        """Test valid MetaAnalysis creation."""
        analysis = MetaAnalysis(
            novelty_score=0.7,
            argument_overlap=0.3,
            convergence_trend=0.8,
            recommend_terminate=False
        )
        self.assertEqual(analysis.novelty_score, 0.7)
        self.assertFalse(analysis.recommend_terminate)
    
    def test_deliberation_config_valid(self):
        """Test valid DeliberationConfig creation."""
        config = DeliberationConfig(
            mode="consensus",
            max_rounds=5,
            max_tokens_per_agent=300,
            temperature=0.7,
            convergence_threshold=0.85,
            novelty_threshold=0.1,
            voting_system="majority"
        )
        self.assertEqual(config.mode, "consensus")
        self.assertEqual(config.max_rounds, 5)
        self.assertEqual(config.voting_system, "majority")
    
    def test_deliberation_config_modes(self):
        """Test different deliberation modes."""
        modes = ["fast", "adversarial", "consensus", "deep_deliberation"]
        for mode in modes:
            config = DeliberationConfig(mode=mode)
            self.assertEqual(config.mode, mode)
    
    def test_deliberation_config_voting_systems(self):
        """Test different voting systems."""
        systems = ["majority", "supermajority", "quadratic", "influence_weighted"]
        for system in systems:
            config = DeliberationConfig(voting_system=system)
            self.assertEqual(config.voting_system, system)


class TestValidation(unittest.TestCase):
    """Test validation layer."""
    
    def test_validator_import(self):
        """Test that validator can be imported."""
        from reference.deliberation.utils.validation import Validator
        validator = Validator(max_retries=1)
        self.assertIsNotNone(validator)
    
    def test_clamp_confidence_values(self):
        """Test confidence value clamping utility."""
        from reference.deliberation.utils.validation import clamp_confidence_values
        
        data = {"confidence": 1.5, "nested": {"confidence": -0.3}}
        result = clamp_confidence_values(data)
        
        self.assertEqual(result["confidence"], 1.0)
        self.assertEqual(result["nested"]["confidence"], 0.0)


class TestStateEngine(unittest.TestCase):
    """Test StateEngine functionality."""
    
    def test_state_engine_initialization(self):
        """Test StateEngine initialization."""
        from reference.deliberation.core.state_engine import StateEngine
        engine = StateEngine()
        state = engine.get_current_state()
        self.assertEqual(state.round, 0)
    
    def test_agent_context_retrieval(self):
        """Test getting agent context."""
        from reference.deliberation.core.state_engine import StateEngine
        engine = StateEngine()
        context = engine.get_agent_context("agent-1")
        
        self.assertIn("round", context)
        self.assertIn("policy_vector", context)
        self.assertIn("agent_position", context)
    
    def test_amendment_management(self):
        """Test adding and resolving amendments."""
        from reference.deliberation.core.state_engine import StateEngine
        engine = StateEngine()
        
        engine.add_amendment("Amendment 1")
        self.assertEqual(len(engine.state.open_amendments), 1)
        
        engine.resolve_amendment("Amendment 1")
        self.assertEqual(len(engine.state.open_amendments), 0)


class TestMetrics(unittest.TestCase):
    """Test MetricsCollector functionality."""
    
    def test_metrics_initialization(self):
        """Test MetricsCollector initialization."""
        from reference.deliberation.core.metrics import MetricsCollector
        metrics = MetricsCollector()
        self.assertEqual(metrics.metrics.total_tokens, 0)
    
    def test_debate_lifecycle(self):
        """Test debate start/end tracking."""
        from reference.deliberation.core.metrics import MetricsCollector
        metrics = MetricsCollector()
        
        metrics.start_debate()
        self.assertIsNotNone(metrics.metrics.start_time)
        
        metrics.end_debate()
        self.assertIsNotNone(metrics.metrics.end_time)


if __name__ == "__main__":
    unittest.main()
