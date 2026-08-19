"""
Coalition builder for agent alignment and group formation.
"""

from typing import List, Dict, Set, Tuple
from ..models.schemas import AgentPosition, AgentAlignment


class CoalitionBuilder:
    """
    Build and manage agent coalitions based on alignment.
    """
    
    def __init__(self):
        """Initialize coalition builder."""
        pass
    
    def form_coalitions(self, positions: Dict[str, AgentPosition]) -> Dict[str, List[str]]:
        """
        Form coalitions based on agent positions and alignment.
        
        Args:
            positions: Agent positions with alignment data
            
        Returns:
            Dictionary mapping coalition names to agent lists
        """
        coalitions = {}
        assigned = set()
        
        for agent_id, position in positions.items():
            if agent_id in assigned:
                continue
            
            # Find similar agents
            coalition_members = [agent_id]
            assigned.add(agent_id)
            
            for other_id, other_position in positions.items():
                if other_id in assigned:
                    continue
                
                if self._are_aligned(position, other_position):
                    coalition_members.append(other_id)
                    assigned.add(other_id)
            
            # Name coalition by size and first member
            coalition_name = f"coalition_{len(coalitions)+1}_{len(coalition_members)}_agents"
            coalitions[coalition_name] = coalition_members
        
        return coalitions
    
    def _are_aligned(self, pos1: AgentPosition, pos2: AgentPosition, 
                     threshold: float = 0.3) -> bool:
        """
        Check if two agents are aligned.
        
        Args:
            pos1: First agent position
            pos2: Second agent position
            threshold: Alignment threshold
            
        Returns:
            True if aligned
        """
        # Check if both have alignment data
        if not pos1.alignment or not pos2.alignment:
            # Fall back to stance similarity
            return self._similar_stance(pos1.stance, pos2.stance)
        
        # Calculate alignment distance
        econ_diff = abs(pos1.alignment.economic - pos2.alignment.economic)
        social_diff = abs(pos1.alignment.social - pos2.alignment.social)
        risk_diff = abs(pos1.alignment.risk_tolerance - pos2.alignment.risk_tolerance)
        
        avg_diff = (econ_diff + social_diff + risk_diff) / 3
        
        return avg_diff <= threshold
    
    def _similar_stance(self, stance1: str, stance2: str) -> bool:
        """
        Check if two stances are similar.
        
        Args:
            stance1: First stance
            stance2: Second stance
            
        Returns:
            True if similar
        """
        # Simple keyword overlap check
        words1 = set(stance1.lower().split())
        words2 = set(stance2.lower().split())
        
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        
        if total == 0:
            return False
        
        similarity = overlap / total
        return similarity >= 0.3
    
    def analyze_coalition_strength(self, coalition: List[str], 
                                  positions: Dict[str, AgentPosition]) -> Dict:
        """
        Analyze the strength of a coalition.
        
        Args:
            coalition: List of agent IDs in coalition
            positions: Agent positions
            
        Returns:
            Coalition analysis
        """
        if not coalition:
            return {"size": 0, "strength": 0.0, "avg_confidence": 0.0}
        
        total_confidence = 0.0
        total_influence = 0.0
        
        for agent_id in coalition:
            position = positions.get(agent_id)
            if position:
                total_confidence += position.confidence
                total_influence += position.influence_score
        
        size = len(coalition)
        
        return {
            "size": size,
            "avg_confidence": total_confidence / size,
            "total_influence": total_influence,
            "strength": (size * total_confidence / size) * (1 + total_influence / size)
        }
    
    def recommend_coalition_strategy(self, coalitions: Dict[str, List[str]], 
                                    positions: Dict[str, AgentPosition]) -> str:
        """
        Recommend a strategy based on coalition analysis.
        
        Args:
            coalitions: Formed coalitions
            positions: Agent positions
            
        Returns:
            Strategy recommendation
        """
        if not coalitions:
            return "No coalitions formed. Agents operate independently."
        
        # Analyze each coalition
        analyses = {}
        for name, members in coalitions.items():
            analyses[name] = self.analyze_coalition_strength(members, positions)
        
        # Find strongest coalition
        strongest = max(analyses.items(), key=lambda x: x[1]["strength"])
        
        if strongest[1]["size"] >= len(positions) * 0.5:
            return f"Majority coalition {strongest[0]} likely to prevail (strength: {strongest[1]['strength']:.2f})"
        else:
            return f"Fragmented coalitions. Negotiation and compromise recommended."
