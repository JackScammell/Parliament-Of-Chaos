"""
Token counting and session monitoring for Parliament of Chaos.
Provides accurate token counting using tiktoken and automatic budget enforcement.
"""

import logging
from typing import Dict, Optional, List, Any, Tuple
import json

logger = logging.getLogger(__name__)

# Try to import tiktoken, fallback to estimation if not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning("tiktoken not available - using character-based estimation")


class TokenCounter:
    """
    Accurate token counting using tiktoken.
    Falls back to character-based estimation if tiktoken is unavailable.
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize token counter.
        
        Args:
            model_name: Model name for tiktoken encoding (default: gpt-4)
        """
        self.model_name = model_name
        self.encoding = None
        
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.encoding_for_model(model_name)
                logger.info(f"TokenCounter initialized with tiktoken for {model_name}")
            except Exception as e:
                logger.warning(f"Failed to get tiktoken encoding for {model_name}: {e}")
                self.encoding = None
        
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Token count (accurate with tiktoken, estimated without)
        """
        if not text:
            return 0
            
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception as e:
                logger.warning(f"tiktoken encoding failed: {e}, falling back to estimation")
                return self._estimate_tokens(text)
        else:
            return self._estimate_tokens(text)
    
    def count_tokens_dict(self, data: Dict) -> int:
        """
        Count tokens in a dictionary (converts to JSON first).
        
        Args:
            data: Dictionary to count tokens for
            
        Returns:
            Token count
        """
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            return self.count_tokens(json_str)
        except Exception as e:
            logger.warning(f"Failed to count tokens in dict: {e}")
            return 0
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Fallback estimation: ~4 characters per token.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        return len(text) // 4


class SessionTokenMonitor:
    """
    Monitors token usage during a debate session.
    Automatically triggers compression when approaching budget limits.
    """
    
    def __init__(
        self, 
        max_tokens_per_round: int = 10000,
        compression_threshold: float = 0.8,
        model_name: str = "gpt-4"
    ):
        """
        Initialize session token monitor.
        
        Args:
            max_tokens_per_round: Maximum tokens allowed per round
            compression_threshold: Trigger compression at this % of budget (0-1)
            model_name: Model name for token counting
        """
        self.max_tokens_per_round = max_tokens_per_round
        self.compression_threshold = compression_threshold
        self.counter = TokenCounter(model_name)
        
        # Tracking
        self._round_tokens: List[int] = []
        self._current_round_tokens = 0
        self._agent_tokens: Dict[str, List[int]] = {}
        self._compression_triggered_count = 0
        self._warnings_issued = 0
        
        logger.info(
            f"SessionTokenMonitor initialized: "
            f"max_tokens={max_tokens_per_round}, "
            f"threshold={compression_threshold:.1%}"
        )
    
    def track_agent_tokens(self, agent_id: str, tokens: int):
        """
        Track token usage for an agent.
        
        Args:
            agent_id: Agent identifier
            tokens: Number of tokens used
        """
        if agent_id not in self._agent_tokens:
            self._agent_tokens[agent_id] = []
        
        self._agent_tokens[agent_id].append(tokens)
        self._current_round_tokens += tokens
        
        # Check if approaching budget limit
        usage_ratio = self._current_round_tokens / self.max_tokens_per_round
        if usage_ratio >= self.compression_threshold:
            logger.warning(
                f"Token budget at {usage_ratio:.1%} - compression recommended"
            )
            self._warnings_issued += 1
    
    def should_compress(self) -> bool:
        """
        Check if compression should be triggered.
        
        Returns:
            True if current round tokens exceed compression threshold
        """
        usage_ratio = self._current_round_tokens / self.max_tokens_per_round
        return usage_ratio >= self.compression_threshold
    
    def end_round(self):
        """Mark the end of current round and reset counter."""
        self._round_tokens.append(self._current_round_tokens)
        logger.info(f"Round ended with {self._current_round_tokens} tokens")
        self._current_round_tokens = 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive token usage statistics.
        
        Returns:
            Dictionary with token usage metrics
        """
        total_tokens = sum(self._round_tokens) + self._current_round_tokens
        
        stats = {
            "total_tokens": total_tokens,
            "rounds_completed": len(self._round_tokens),
            "current_round_tokens": self._current_round_tokens,
            "average_tokens_per_round": 0,
            "max_round_tokens": 0,
            "min_round_tokens": 0,
            "compression_triggered": self._compression_triggered_count,
            "warnings_issued": self._warnings_issued,
            "budget_utilization": 0,
            "agent_statistics": {}
        }
        
        if self._round_tokens:
            stats["average_tokens_per_round"] = sum(self._round_tokens) / len(self._round_tokens)
            stats["max_round_tokens"] = max(self._round_tokens)
            stats["min_round_tokens"] = min(self._round_tokens)
        
        if self.max_tokens_per_round > 0:
            stats["budget_utilization"] = total_tokens / (
                self.max_tokens_per_round * (len(self._round_tokens) + 1)
            )
        
        # Agent statistics
        for agent_id, tokens_list in self._agent_tokens.items():
            if tokens_list:
                stats["agent_statistics"][agent_id] = {
                    "total_tokens": sum(tokens_list),
                    "average_tokens": sum(tokens_list) / len(tokens_list),
                    "calls": len(tokens_list)
                }
        
        return stats
    
    def reset(self):
        """Reset all tracking for new session."""
        self._round_tokens.clear()
        self._current_round_tokens = 0
        self._agent_tokens.clear()
        self._compression_triggered_count = 0
        self._warnings_issued = 0
        logger.info("SessionTokenMonitor reset")


class TokenBudgetEnforcer:
    """
    Enforces token budgets per agent call.
    Compresses context if it exceeds the budget.
    """
    
    def __init__(self, max_tokens_per_agent: int = 500):
        """
        Initialize token budget enforcer.
        
        Args:
            max_tokens_per_agent: Maximum tokens per agent call
        """
        self.max_tokens_per_agent = max_tokens_per_agent
        self.counter = TokenCounter()
        self._enforcement_count = 0
        logger.info(f"TokenBudgetEnforcer initialized with budget={max_tokens_per_agent}")
    
    def check_budget(self, context: Dict) -> Tuple[bool, int]:
        """
        Check if context fits within token budget.
        
        Args:
            context: Context dictionary to check
            
        Returns:
            Tuple of (fits_budget: bool, token_count: int)
        """
        token_count = self.counter.count_tokens_dict(context)
        fits_budget = token_count <= self.max_tokens_per_agent
        
        if not fits_budget:
            logger.warning(
                f"Context exceeds budget: {token_count} > {self.max_tokens_per_agent}"
            )
        
        return fits_budget, token_count
    
    def compress_if_needed(
        self, 
        context: Dict,
        compress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Compress context if it exceeds token budget.
        
        Args:
            context: Context dictionary to check and compress
            compress_callback: Optional callback function to perform compression
            
        Returns:
            Compressed context (or original if within budget)
        """
        fits_budget, token_count = self.check_budget(context)
        
        if fits_budget:
            return context
        
        self._enforcement_count += 1
        
        # If callback provided, use it for custom compression
        if compress_callback:
            compressed = compress_callback(context, self.max_tokens_per_agent)
            logger.info(f"Custom compression applied (enforcement #{self._enforcement_count})")
            return compressed
        
        # Default compression: reduce historical context depth
        compressed = context.copy()
        
        # Reduce historical summaries
        if "historical_summary" in compressed:
            hist = compressed["historical_summary"]
            if "recent_summaries" in hist and len(hist["recent_summaries"]) > 1:
                # Keep only most recent summary
                hist["recent_summaries"] = hist["recent_summaries"][-1:]
                logger.info("Compressed historical context to 1 recent summary")
        
        # Trim aggregated data
        if "historical_summary" in compressed and "aggregated" in compressed["historical_summary"]:
            agg = compressed["historical_summary"]["aggregated"]
            for key in agg:
                if isinstance(agg[key], list) and len(agg[key]) > 3:
                    agg[key] = agg[key][:3]
        
        # Remove reference context if present
        if "reference" in compressed:
            del compressed["reference"]
            logger.info("Removed reference context to fit budget")
        
        return compressed
    
    def get_enforcement_stats(self) -> Dict:
        """Get statistics on budget enforcement."""
        return {
            "max_tokens_per_agent": self.max_tokens_per_agent,
            "enforcement_count": self._enforcement_count
        }
