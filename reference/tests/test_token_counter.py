"""
Unit tests for token counting and session monitoring.
"""

import unittest
from reference.deliberation.core.token_counter import (
    TokenCounter, SessionTokenMonitor, TokenBudgetEnforcer
)


class TestTokenCounter(unittest.TestCase):
    """Test TokenCounter functionality."""
    
    def test_create_token_counter(self):
        """Test creating token counter."""
        counter = TokenCounter()
        self.assertIsNotNone(counter)
    
    def test_count_tokens_simple(self):
        """Test counting tokens in simple text."""
        counter = TokenCounter()
        text = "Hello world, this is a test."
        tokens = counter.count_tokens(text)
        self.assertGreater(tokens, 0)
        # Should be roughly 7-8 tokens
        self.assertLess(tokens, 20)
    
    def test_count_tokens_empty(self):
        """Test counting tokens in empty text."""
        counter = TokenCounter()
        tokens = counter.count_tokens("")
        self.assertEqual(tokens, 0)
    
    def test_count_tokens_dict(self):
        """Test counting tokens in dictionary."""
        counter = TokenCounter()
        data = {
            "agent_id": "agent-1",
            "position": "Support",
            "argument": "This is a test argument."
        }
        tokens = counter.count_tokens_dict(data)
        self.assertGreater(tokens, 0)


class TestSessionTokenMonitor(unittest.TestCase):
    """Test SessionTokenMonitor functionality."""
    
    def test_create_monitor(self):
        """Test creating session token monitor."""
        monitor = SessionTokenMonitor(max_tokens_per_round=1000)
        self.assertEqual(monitor.max_tokens_per_round, 1000)
    
    def test_track_agent_tokens(self):
        """Test tracking agent token usage."""
        monitor = SessionTokenMonitor(max_tokens_per_round=1000)
        monitor.track_agent_tokens("agent-1", 100)
        monitor.track_agent_tokens("agent-2", 150)
        
        stats = monitor.get_statistics()
        self.assertEqual(stats["current_round_tokens"], 250)
    
    def test_should_compress_below_threshold(self):
        """Test compression check below threshold."""
        monitor = SessionTokenMonitor(
            max_tokens_per_round=1000,
            compression_threshold=0.8
        )
        monitor.track_agent_tokens("agent-1", 500)
        self.assertFalse(monitor.should_compress())
    
    def test_should_compress_above_threshold(self):
        """Test compression check above threshold."""
        monitor = SessionTokenMonitor(
            max_tokens_per_round=1000,
            compression_threshold=0.8
        )
        monitor.track_agent_tokens("agent-1", 900)
        self.assertTrue(monitor.should_compress())
    
    def test_end_round(self):
        """Test ending round resets counter."""
        monitor = SessionTokenMonitor(max_tokens_per_round=1000)
        monitor.track_agent_tokens("agent-1", 500)
        self.assertEqual(monitor._current_round_tokens, 500)
        
        monitor.end_round()
        self.assertEqual(monitor._current_round_tokens, 0)
        self.assertEqual(len(monitor._round_tokens), 1)
    
    def test_get_statistics(self):
        """Test getting comprehensive statistics."""
        monitor = SessionTokenMonitor(max_tokens_per_round=1000)
        monitor.track_agent_tokens("agent-1", 100)
        monitor.track_agent_tokens("agent-2", 150)
        monitor.end_round()
        
        monitor.track_agent_tokens("agent-1", 200)
        
        stats = monitor.get_statistics()
        self.assertEqual(stats["rounds_completed"], 1)
        self.assertEqual(stats["current_round_tokens"], 200)
        self.assertIn("agent-1", stats["agent_statistics"])
        self.assertIn("agent-2", stats["agent_statistics"])


class TestTokenBudgetEnforcer(unittest.TestCase):
    """Test TokenBudgetEnforcer functionality."""
    
    def test_create_enforcer(self):
        """Test creating token budget enforcer."""
        enforcer = TokenBudgetEnforcer(max_tokens_per_agent=500)
        self.assertEqual(enforcer.max_tokens_per_agent, 500)
    
    def test_check_budget_within_limit(self):
        """Test checking budget within limit."""
        enforcer = TokenBudgetEnforcer(max_tokens_per_agent=500)
        context = {"round": 1, "topic": "test"}
        fits, tokens = enforcer.check_budget(context)
        self.assertTrue(fits)
        self.assertGreater(tokens, 0)
    
    def test_check_budget_exceeds_limit(self):
        """Test checking budget that exceeds limit."""
        enforcer = TokenBudgetEnforcer(max_tokens_per_agent=50)
        # Create a large context
        context = {
            "round": 1,
            "topic": "test",
            "immediate_context": {
                "statements": [
                    {
                        "agent_id": f"agent-{i}",
                        "position": "This is a long position statement",
                        "argument": " ".join(["word"] * 50)
                    }
                    for i in range(10)
                ]
            }
        }
        fits, tokens = enforcer.check_budget(context)
        self.assertFalse(fits)
        self.assertGreater(tokens, 50)
    
    def test_compress_if_needed_no_compression(self):
        """Test compression when context fits budget."""
        enforcer = TokenBudgetEnforcer(max_tokens_per_agent=500)
        context = {"round": 1, "topic": "test"}
        compressed = enforcer.compress_if_needed(context)
        self.assertEqual(context, compressed)
    
    def test_compress_if_needed_with_compression(self):
        """Test compression when context exceeds budget."""
        enforcer = TokenBudgetEnforcer(max_tokens_per_agent=50)
        context = {
            "round": 1,
            "historical_summary": {
                "recent_summaries": [
                    {"round": "1", "positions": ["A", "B"]},
                    {"round": "2", "positions": ["C", "D"]},
                    {"round": "3", "positions": ["E", "F"]}
                ]
            },
            "reference": {
                "rules": ["rule1", "rule2"]
            }
        }
        
        compressed = enforcer.compress_if_needed(context)
        
        # Should have reduced summaries
        if "historical_summary" in compressed:
            summaries = compressed["historical_summary"].get("recent_summaries", [])
            self.assertLessEqual(len(summaries), 1)
        
        # Reference should be removed
        self.assertNotIn("reference", compressed)
    
    def test_get_enforcement_stats(self):
        """Test getting enforcement statistics."""
        enforcer = TokenBudgetEnforcer(max_tokens_per_agent=50)
        stats = enforcer.get_enforcement_stats()
        self.assertEqual(stats["max_tokens_per_agent"], 50)
        self.assertEqual(stats["enforcement_count"], 0)


if __name__ == "__main__":
    unittest.main()
