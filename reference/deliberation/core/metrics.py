"""
Performance metrics collector for Parliament of Chaos.
Tracks token usage, latency, convergence, and redundancy.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..models.schemas import PerformanceMetrics, DebateState
import math

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Tracks and persists debate performance metrics.
    """
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self._round_start_times: List[datetime] = []
        self._latencies: List[float] = []
    
    def start_debate(self):
        """Mark debate start time."""
        self.metrics.start_time = datetime.utcnow().isoformat()
        logger.info("Metrics collection started")
    
    def end_debate(self):
        """Mark debate end time."""
        self.metrics.end_time = datetime.utcnow().isoformat()
        
        # Calculate average latency
        if self._latencies:
            self.metrics.average_latency = sum(self._latencies) / len(self._latencies)
        
        logger.info(
            f"Metrics collection ended: "
            f"total_tokens={self.metrics.total_tokens}, "
            f"rounds={len(self.metrics.tokens_per_round)}, "
            f"avg_latency={self.metrics.average_latency:.2f}s"
        )
    
    def start_round(self):
        """Mark round start time."""
        self._round_start_times.append(datetime.utcnow())
    
    def end_round(self, tokens_used: int):
        """
        Mark round end and record tokens used.
        
        Args:
            tokens_used: Number of tokens consumed in this round
        """
        if not self._round_start_times:
            logger.warning("end_round called without start_round")
            return
        
        start_time = self._round_start_times.pop()
        end_time = datetime.utcnow()
        latency = (end_time - start_time).total_seconds()
        
        self._latencies.append(latency)
        self.metrics.tokens_per_round.append(tokens_used)
        self.metrics.total_tokens += tokens_used
        
        logger.info(f"Round completed: tokens={tokens_used}, latency={latency:.2f}s")
    
    def record_convergence(self, round_num: int):
        """
        Record the round at which convergence was reached.
        
        Args:
            round_num: Round number when convergence occurred
        """
        if self.metrics.rounds_to_convergence is None:
            self.metrics.rounds_to_convergence = round_num
            logger.info(f"Convergence reached at round {round_num}")
    
    def calculate_position_entropy(self, state: DebateState) -> float:
        """
        Calculate entropy of agent positions.
        Higher entropy = more diverse positions.
        
        Args:
            state: Current debate state
            
        Returns:
            Entropy value (0 = consensus, higher = more diversity)
        """
        if not state.agent_positions:
            return 0.0
        
        # Count positions
        from collections import Counter
        positions = [pos.stance for pos in state.agent_positions.values()]
        position_counts = Counter(positions)
        
        total = len(positions)
        entropy = 0.0
        
        for count in position_counts.values():
            if count > 0:
                probability = count / total
                entropy -= probability * math.log2(probability)
        
        self.metrics.position_entropy = entropy
        return entropy
    
    def calculate_argument_redundancy(self, arguments: List[str]) -> float:
        """
        Calculate redundancy score for arguments.
        
        Args:
            arguments: List of argument texts
            
        Returns:
            Redundancy score (0 = no overlap, 1 = complete redundancy)
        """
        if len(arguments) < 2:
            return 0.0
        
        # Simple word-based redundancy calculation
        total_comparisons = 0
        redundant_comparisons = 0
        
        for i in range(len(arguments)):
            for j in range(i + 1, len(arguments)):
                total_comparisons += 1
                
                words_i = set(arguments[i].lower().split())
                words_j = set(arguments[j].lower().split())
                
                if not words_i or not words_j:
                    continue
                
                overlap = len(words_i & words_j)
                min_size = min(len(words_i), len(words_j))
                
                if min_size > 0 and overlap / min_size > 0.6:
                    redundant_comparisons += 1
        
        if total_comparisons == 0:
            return 0.0
        
        redundancy = redundant_comparisons / total_comparisons
        self.metrics.argument_redundancy_score = redundancy
        return redundancy
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get current metrics snapshot."""
        return self.metrics.model_copy()
    
    def export_metrics(self) -> Dict:
        """Export metrics as dictionary for persistence."""
        return self.metrics.model_dump()
    
    def get_summary(self) -> str:
        """Get human-readable metrics summary."""
        lines = [
            "=== Debate Performance Metrics ===",
            f"Total Tokens: {self.metrics.total_tokens:,}",
            f"Rounds: {len(self.metrics.tokens_per_round)}",
            f"Avg Tokens/Round: {sum(self.metrics.tokens_per_round) / max(1, len(self.metrics.tokens_per_round)):.0f}",
            f"Avg Latency: {self.metrics.average_latency:.2f}s",
        ]
        
        if self.metrics.rounds_to_convergence is not None:
            lines.append(f"Rounds to Convergence: {self.metrics.rounds_to_convergence}")
        
        lines.extend([
            f"Position Entropy: {self.metrics.position_entropy:.2f}",
            f"Argument Redundancy: {self.metrics.argument_redundancy_score:.2f}",
        ])
        
        return "\n".join(lines)
    
    def reset(self):
        """Reset metrics for new debate."""
        self.metrics = PerformanceMetrics()
        self._round_start_times.clear()
        self._latencies.clear()
        logger.info("Metrics collector reset")
