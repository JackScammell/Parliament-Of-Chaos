"""
Analytics engine for debate metrics and insights.
"""

from typing import Dict, List
from datetime import datetime


class AnalyticsEngine:
    """
    Compute advanced analytics on debate data.
    """
    
    def __init__(self):
        """Initialize analytics engine."""
        pass
    
    def calculate_consensus_score(self, votes: Dict) -> float:
        """
        Calculate consensus score from voting data.
        
        Args:
            votes: Voting results
            
        Returns:
            Consensus score (0-1)
        """
        total = votes.get("total", 0)
        if total == 0:
            return 0.0
        
        approve = votes.get("approve", 0)
        reject = votes.get("reject", 0)
        
        # Higher score = more consensus
        max_votes = max(approve, reject)
        return max_votes / total
    
    def calculate_agent_influence(self, positions: Dict, votes: List) -> Dict[str, float]:
        """
        Calculate influence score for each agent.
        
        Args:
            positions: Agent positions
            votes: List of votes
            
        Returns:
            Dictionary of agent influence scores
        """
        influence_scores = {}
        
        for agent_id, position in positions.items():
            # Base influence on confidence and consistency
            confidence = position.confidence if hasattr(position, 'confidence') else 0.5
            stability = position.stability_index if hasattr(position, 'stability_index') else 0.5
            
            influence_scores[agent_id] = (confidence + stability) / 2.0
        
        return influence_scores
    
    def calculate_novelty_scores(self, rounds_data: List[Dict]) -> List[float]:
        """
        Calculate argument novelty for each round.
        
        Args:
            rounds_data: Data from each debate round
            
        Returns:
            List of novelty scores by round
        """
        novelty_scores = []
        seen_topics = set()
        
        for round_data in rounds_data:
            if isinstance(round_data, dict):
                positions = round_data.get("core_positions", [])
            else:
                positions = round_data.core_positions if hasattr(round_data, "core_positions") else []
            
            # Calculate novelty based on unique topics
            new_topics = set()
            for pos in positions:
                # Extract keywords from position
                words = set(pos.lower().split())
                new_topics.update(words - seen_topics)
            
            if len(positions) > 0:
                novelty = len(new_topics) / (len(positions) * 5)  # Normalize
            else:
                novelty = 0.0
            
            novelty_scores.append(min(1.0, novelty))
            seen_topics.update(new_topics)
        
        return novelty_scores
    
    def calculate_time_to_convergence(self, start_time: str, 
                                     rounds_to_convergence: int,
                                     average_latency: float) -> float:
        """
        Calculate time to reach convergence.
        
        Args:
            start_time: Debate start timestamp
            rounds_to_convergence: Rounds needed
            average_latency: Average round latency
            
        Returns:
            Time to convergence in seconds
        """
        if rounds_to_convergence is None:
            return 0.0
        
        return rounds_to_convergence * average_latency
