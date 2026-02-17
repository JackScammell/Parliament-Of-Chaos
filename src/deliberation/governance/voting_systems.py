"""
Advanced voting systems with confidence weighting and delegation.
"""

from typing import List, Dict, Tuple
from ..models.schemas import Vote, AgentPosition


class VotingSystemManager:
    """
    Manage various voting systems for debate outcomes.
    """
    
    def __init__(self):
        """Initialize voting system manager."""
        pass
    
    def calculate_outcome(self, votes: List[Vote], positions: Dict[str, AgentPosition],
                         system: str = "majority") -> Tuple[bool, Dict]:
        """
        Calculate voting outcome based on system.
        
        Args:
            votes: List of votes
            positions: Agent positions for influence calculation
            system: Voting system to use
            
        Returns:
            Tuple of (approved, details)
        """
        if system == "majority":
            return self._majority_vote(votes)
        elif system == "supermajority":
            return self._supermajority_vote(votes)
        elif system == "influence_weighted":
            return self._influence_weighted_vote(votes, positions)
        elif system == "quadratic":
            return self._quadratic_vote(votes)
        elif system == "delegated":
            return self._delegated_vote(votes, positions)
        elif system == "coalition":
            return self._coalition_vote(votes, positions)
        else:
            return self._majority_vote(votes)
    
    def _majority_vote(self, votes: List[Vote]) -> Tuple[bool, Dict]:
        """Simple majority voting."""
        approve = len([v for v in votes if v.vote == "approve"])
        reject = len([v for v in votes if v.vote == "reject"])
        
        approved = approve > reject
        
        return approved, {
            "approve": approve,
            "reject": reject,
            "abstain": len(votes) - approve - reject,
            "threshold": "50%",
            "system": "majority"
        }
    
    def _supermajority_vote(self, votes: List[Vote]) -> Tuple[bool, Dict]:
        """Supermajority (2/3) voting."""
        approve = len([v for v in votes if v.vote == "approve"])
        reject = len([v for v in votes if v.vote == "reject"])
        total_participating = approve + reject
        
        threshold = total_participating * 2 / 3
        approved = approve >= threshold
        
        return approved, {
            "approve": approve,
            "reject": reject,
            "abstain": len(votes) - approve - reject,
            "threshold": "66.7%",
            "required": threshold,
            "system": "supermajority"
        }
    
    def _influence_weighted_vote(self, votes: List[Vote], 
                                 positions: Dict[str, AgentPosition]) -> Tuple[bool, Dict]:
        """Votes weighted by agent influence scores."""
        weighted_approve = 0.0
        weighted_reject = 0.0
        
        for vote in votes:
            position = positions.get(vote.agent_id)
            if position:
                weight = position.influence_score * vote.confidence
            else:
                weight = vote.confidence
            
            if vote.vote == "approve":
                weighted_approve += weight
            elif vote.vote == "reject":
                weighted_reject += weight
        
        approved = weighted_approve > weighted_reject
        
        return approved, {
            "weighted_approve": round(weighted_approve, 3),
            "weighted_reject": round(weighted_reject, 3),
            "system": "influence_weighted"
        }
    
    def _quadratic_vote(self, votes: List[Vote]) -> Tuple[bool, Dict]:
        """Quadratic voting with confidence as vote strength."""
        import math
        
        quadratic_approve = 0.0
        quadratic_reject = 0.0
        
        for vote in votes:
            # Square root to prevent vote concentration
            strength = math.sqrt(vote.confidence)
            
            if vote.vote == "approve":
                quadratic_approve += strength
            elif vote.vote == "reject":
                quadratic_reject += strength
        
        approved = quadratic_approve > quadratic_reject
        
        return approved, {
            "quadratic_approve": round(quadratic_approve, 3),
            "quadratic_reject": round(quadratic_reject, 3),
            "system": "quadratic"
        }
    
    def _delegated_vote(self, votes: List[Vote], 
                       positions: Dict[str, AgentPosition]) -> Tuple[bool, Dict]:
        """Delegated voting where high-confidence agents have more weight."""
        total_confidence_approve = 0.0
        total_confidence_reject = 0.0
        delegated_votes = 0
        
        for vote in votes:
            if vote.confidence >= 0.8:  # High confidence = delegate receives weight
                weight = 2.0
                delegated_votes += 1
            else:
                weight = 1.0
            
            if vote.vote == "approve":
                total_confidence_approve += weight
            elif vote.vote == "reject":
                total_confidence_reject += weight
        
        approved = total_confidence_approve > total_confidence_reject
        
        return approved, {
            "weighted_approve": round(total_confidence_approve, 3),
            "weighted_reject": round(total_confidence_reject, 3),
            "delegated_votes": delegated_votes,
            "system": "delegated"
        }
    
    def _coalition_vote(self, votes: List[Vote], 
                       positions: Dict[str, AgentPosition]) -> Tuple[bool, Dict]:
        """Coalition-based voting where aligned agents amplify each other."""
        # Group by vote type
        approve_coalition = [v for v in votes if v.vote == "approve"]
        reject_coalition = [v for v in votes if v.vote == "reject"]
        
        # Calculate coalition strength (members * average confidence)
        def coalition_strength(coalition):
            if not coalition:
                return 0.0
            avg_confidence = sum(v.confidence for v in coalition) / len(coalition)
            return len(coalition) * avg_confidence
        
        approve_strength = coalition_strength(approve_coalition)
        reject_strength = coalition_strength(reject_coalition)
        
        approved = approve_strength > reject_strength
        
        return approved, {
            "approve_coalition_size": len(approve_coalition),
            "reject_coalition_size": len(reject_coalition),
            "approve_strength": round(approve_strength, 3),
            "reject_strength": round(reject_strength, 3),
            "system": "coalition"
        }
