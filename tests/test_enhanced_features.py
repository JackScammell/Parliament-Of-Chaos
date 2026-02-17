"""
Unit tests for enhanced Parliament of Chaos features.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path

from src.deliberation.models.schemas import (
    TeamRole, DebateTeamsConfig, AgentSkillTree, MemoryEntry,
    ConstraintDefinition, SessionState, MetaLearning
)
from src.deliberation.memory import MemoryManager, MemoryStore
from src.deliberation.plugins import PluginManager, PluginRegistry
from src.deliberation.analytics import DebateDashboard, AnalyticsEngine
from src.deliberation.constraints import ConstraintValidator, ConstraintLoader
from src.deliberation.governance import VotingSystemManager, CoalitionBuilder
from src.deliberation.agents.skill_trees import SkillTreeManager
from src.deliberation.agents.team_coordinator import TeamCoordinator, create_default_debate_teams
from src.deliberation.core.session_manager import SessionManager
from src.deliberation.core.self_improvement import SelfImprovementEngine


class TestTeamIntegration(unittest.TestCase):
    """Test team-based debate features."""
    
    def test_team_role_creation(self):
        """Test TeamRole schema."""
        role = TeamRole(
            role="advocate",
            description="Present pro arguments",
            agents=["agent1", "agent2"],
            priority=1
        )
        self.assertEqual(role.role, "advocate")
        self.assertEqual(len(role.agents), 2)
    
    def test_debate_teams_config(self):
        """Test DebateTeamsConfig schema."""
        config = DebateTeamsConfig(
            enable_teams=True,
            teams=[
                TeamRole(role="advocate", description="Test", agents=[], priority=1)
            ],
            team_coordination_mode="parallel"
        )
        self.assertTrue(config.enable_teams)
        self.assertEqual(config.team_coordination_mode, "parallel")
    
    def test_create_default_debate_teams(self):
        """Test automatic team creation."""
        agents = ["a1", "a2", "a3", "a4"]
        config = create_default_debate_teams(agents)
        
        self.assertTrue(config.enable_teams)
        self.assertEqual(len(config.teams), 4)
    
    def test_team_coordinator(self):
        """Test TeamCoordinator."""
        config = create_default_debate_teams(["a1", "a2", "a3", "a4"])
        coordinator = TeamCoordinator(config)
        
        assignments = coordinator.assign_agents_to_roles(
            ["a5", "a6", "a7", "a8"],
            auto_balance=True
        )
        
        self.assertIn("advocate", assignments)
        summary = coordinator.get_team_summary()
        self.assertTrue(summary["enabled"])


class TestMemorySystem(unittest.TestCase):
    """Test persistent memory features."""
    
    def setUp(self):
        """Set up temporary storage."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary storage."""
        shutil.rmtree(self.temp_dir)
    
    def test_memory_entry_schema(self):
        """Test MemoryEntry schema."""
        entry = MemoryEntry(
            session_id="test-123",
            topic="Test topic",
            timestamp="2026-02-17T10:00:00",
            outcome={"approved": True},
            key_learnings=["lesson1"],
            patterns=["pattern1"]
        )
        self.assertEqual(entry.session_id, "test-123")
    
    def test_memory_store(self):
        """Test MemoryStore functionality."""
        store = MemoryStore(self.temp_dir)
        
        entry = MemoryEntry(
            session_id="test-456",
            topic="API Design",
            timestamp="2026-02-17T10:00:00",
            outcome={"approved": True},
            key_learnings=["REST is better"],
            patterns=["consensus_achieved"]
        )
        
        # Store entry
        entry_id = store.store(entry)
        self.assertEqual(entry_id, "test-456")
        
        # Retrieve entry
        retrieved = store.retrieve("test-456")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.topic, "API Design")
        
        # Search
        results = store.search("API", limit=5)
        self.assertEqual(len(results), 1)
    
    def test_memory_manager(self):
        """Test MemoryManager functionality."""
        manager = MemoryManager(self.temp_dir)
        
        # Save debate
        entry_id = manager.save_debate(
            session_id="debate-1",
            topic="Security Policy",
            outcome={"approved": True, "votes": {"approve": 5}},
            key_learnings=["Encryption required"]
        )
        
        # Recall similar debates
        similar = manager.recall_similar_debates("Security", limit=3)
        self.assertEqual(len(similar), 1)
        
        # Get patterns
        patterns = manager.get_past_patterns("Security")
        self.assertIn("consensus_achieved", patterns)


class TestPluginSystem(unittest.TestCase):
    """Test plugin marketplace features."""
    
    def setUp(self):
        """Set up temporary storage."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary storage."""
        shutil.rmtree(self.temp_dir)
    
    def test_plugin_manager(self):
        """Test plugin installation and management."""
        manager = PluginManager(self.temp_dir)
        
        # Install plugin
        success = manager.install_plugin(
            name="test-agent",
            version="1.0.0",
            author="Test",
            description="Test agent",
            agent_type="specialist",
            skills=["skill1", "skill2"]
        )
        self.assertTrue(success)
        
        # Get plugin info
        plugin = manager.get_plugin_info("test-agent")
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.version, "1.0.0")
        
        # List plugins
        plugins = manager.list_installed()
        self.assertEqual(len(plugins), 1)


class TestAnalytics(unittest.TestCase):
    """Test analytics and dashboard features."""
    
    def test_analytics_engine(self):
        """Test AnalyticsEngine calculations."""
        engine = AnalyticsEngine()
        
        # Consensus score
        votes = {"approve": 7, "reject": 3, "total": 10}
        consensus = engine.calculate_consensus_score(votes)
        self.assertEqual(consensus, 0.7)
        
        # Agent influence
        from src.deliberation.models.schemas import AgentPosition
        positions = {
            "agent1": AgentPosition(stance="Support", confidence=0.9, influence_score=1.2),
            "agent2": AgentPosition(stance="Oppose", confidence=0.7, influence_score=0.8)
        }
        influence = engine.calculate_agent_influence(positions, [])
        self.assertIn("agent1", influence)
    
    def test_debate_dashboard(self):
        """Test markdown dashboard generation."""
        dashboard = DebateDashboard()
        
        debate_results = {
            "topic": "Test Topic",
            "outcome": {
                "result": "approved",
                "approved": True,
                "votes": {"approve": 7, "reject": 3, "abstain": 0, "total": 10}
            },
            "metrics": {
                "total_tokens": 5000,
                "average_latency": 2.5,
                "rounds_to_convergence": 3,
                "consensus_score": 0.85
            },
            "config": {
                "mode": "consensus",
                "max_rounds": 5,
                "voting_system": "majority"
            }
        }
        
        markdown = dashboard.generate_dashboard(debate_results)
        self.assertIn("Test Topic", markdown)
        self.assertIn("APPROVED", markdown)
        self.assertIn("5,000", markdown)


class TestConstraints(unittest.TestCase):
    """Test constraint validation features."""
    
    def test_constraint_definition(self):
        """Test ConstraintDefinition schema."""
        constraints = ConstraintDefinition(
            max_rounds=5,
            disallowed_patterns=["global state", "eval\\("],
            required_validators=["security_check"],
            custom_rules={"no_profanity": "!bad_word"}
        )
        self.assertEqual(constraints.max_rounds, 5)
        self.assertEqual(len(constraints.disallowed_patterns), 2)
    
    def test_constraint_validator(self):
        """Test constraint validation."""
        constraints = ConstraintDefinition(
            max_rounds=3,
            disallowed_patterns=["global state"],
            required_validators=[],
            custom_rules={}
        )
        
        validator = ConstraintValidator(constraints)
        
        # Valid statement
        is_valid, violations = validator.validate_statement("This is a clean statement")
        self.assertTrue(is_valid)
        
        # Invalid statement
        is_valid, violations = validator.validate_statement("Use global state here")
        self.assertFalse(is_valid)
        self.assertEqual(len(violations), 1)
        
        # Config validation
        is_valid, violations = validator.validate_debate_config(5)
        self.assertFalse(is_valid)  # Exceeds max_rounds


class TestGovernance(unittest.TestCase):
    """Test governance and voting features."""
    
    def test_voting_systems(self):
        """Test different voting systems."""
        from src.deliberation.models.schemas import Vote, AgentPosition
        
        voting = VotingSystemManager()
        
        votes = [
            Vote(agent_id="a1", vote="approve", reasoning="Good", confidence=0.9),
            Vote(agent_id="a2", vote="approve", reasoning="Good", confidence=0.8),
            Vote(agent_id="a3", vote="reject", reasoning="Bad", confidence=0.7)
        ]
        
        positions = {
            "a1": AgentPosition(stance="Support", confidence=0.9, influence_score=1.2),
            "a2": AgentPosition(stance="Support", confidence=0.8, influence_score=1.0),
            "a3": AgentPosition(stance="Oppose", confidence=0.7, influence_score=0.8)
        }
        
        # Majority
        approved, details = voting.calculate_outcome(votes, positions, "majority")
        self.assertTrue(approved)
        
        # Influence weighted
        approved, details = voting.calculate_outcome(votes, positions, "influence_weighted")
        self.assertTrue(approved)
    
    def test_coalition_builder(self):
        """Test coalition formation."""
        from src.deliberation.models.schemas import AgentPosition, AgentAlignment
        
        coalition_builder = CoalitionBuilder()
        
        positions = {
            "a1": AgentPosition(
                stance="Support",
                confidence=0.9,
                alignment=AgentAlignment(economic=0.5, social=0.3, risk_tolerance=0.7)
            ),
            "a2": AgentPosition(
                stance="Support",
                confidence=0.8,
                alignment=AgentAlignment(economic=0.6, social=0.4, risk_tolerance=0.6)
            )
        }
        
        coalitions = coalition_builder.form_coalitions(positions)
        self.assertGreater(len(coalitions), 0)


class TestSkillTrees(unittest.TestCase):
    """Test agent skill tree features."""
    
    def setUp(self):
        """Set up temporary storage."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary storage."""
        shutil.rmtree(self.temp_dir)
    
    def test_agent_skill_tree_schema(self):
        """Test AgentSkillTree schema."""
        tree = AgentSkillTree(
            agent_id="test-agent",
            primary_domain="Testing",
            skills={
                "Unit Testing": ["pytest", "unittest"],
                "Integration Testing": ["selenium", "cypress"]
            },
            skill_level={"Unit Testing": 5, "Integration Testing": 4}
        )
        self.assertEqual(tree.agent_id, "test-agent")
        self.assertEqual(len(tree.skills), 2)
    
    def test_skill_tree_manager(self):
        """Test SkillTreeManager functionality."""
        manager = SkillTreeManager(self.temp_dir)
        
        # Should have default trees loaded
        tree = manager.get_skill_tree("ui-ux-guru")
        self.assertIsNotNone(tree)
        self.assertEqual(tree.primary_domain, "UI/UX Design")
        
        # Get skills for domain
        skills = manager.get_skills_for_domain("ui-ux-guru", "Accessibility")
        self.assertGreater(len(skills), 0)
        
        # Match agent to task
        matches = manager.match_agent_to_task(["accessibility", "wcag"])
        self.assertIn("ui-ux-guru", matches)


class TestSessionManagement(unittest.TestCase):
    """Test multi-session debate chaining."""
    
    def setUp(self):
        """Set up temporary storage."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary storage."""
        shutil.rmtree(self.temp_dir)
    
    def test_session_state_schema(self):
        """Test SessionState schema."""
        state = SessionState(
            session_id="session-1",
            previous_sessions=[],
            carried_forward_context={"key": "value"},
            unresolved_conflicts=["conflict1"],
            session_summaries={"session-1": "Summary"}
        )
        self.assertEqual(state.session_id, "session-1")
    
    def test_session_manager(self):
        """Test SessionManager functionality."""
        manager = SessionManager(self.temp_dir)
        
        # Create session
        session = manager.create_session("session-1")
        self.assertEqual(session.session_id, "session-1")
        
        # Update session
        success = manager.update_session(
            context={"key": "value"},
            conflicts=["unresolved"],
            summary="Session summary"
        )
        self.assertTrue(success)
        
        # Load session
        loaded = manager.load_session("session-1")
        self.assertIsNotNone(loaded)
        
        # Create chained session
        session2 = manager.create_session("session-2", previous_sessions=["session-1"])
        self.assertIn("session-1", session2.previous_sessions)


class TestSelfImprovement(unittest.TestCase):
    """Test self-improvement and meta-learning features."""
    
    def setUp(self):
        """Set up temporary storage."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary storage."""
        shutil.rmtree(self.temp_dir)
    
    def test_meta_learning_schema(self):
        """Test MetaLearning schema."""
        learning = MetaLearning(
            strategy_id="strategy-1",
            performance_history=[0.7, 0.8, 0.85],
            adaptation_count=2,
            successful_patterns=["pattern1"],
            failed_patterns=["pattern2"]
        )
        self.assertEqual(learning.strategy_id, "strategy-1")
        self.assertEqual(len(learning.performance_history), 3)
    
    def test_self_improvement_engine(self):
        """Test SelfImprovementEngine functionality."""
        engine = SelfImprovementEngine(self.temp_dir)
        
        # Record performance
        engine.record_strategy_performance(
            strategy_id="consensus-building",
            performance_score=0.85,
            patterns=["early_compromise", "evidence_based"],
            success=True
        )
        
        # Record more performances
        engine.record_strategy_performance(
            strategy_id="consensus-building",
            performance_score=0.90,
            patterns=["early_compromise"],
            success=True
        )
        
        engine.record_strategy_performance(
            strategy_id="consensus-building",
            performance_score=0.88,
            patterns=["evidence_based"],
            success=True
        )
        
        # Get adaptation suggestion
        suggestion = engine.suggest_adaptation("consensus-building")
        self.assertIn("recommendation", suggestion)
        self.assertGreater(suggestion["avg_performance"], 0.8)
        
        # Adapt strategy
        engine.adapt_strategy("consensus-building")


if __name__ == "__main__":
    unittest.main()
