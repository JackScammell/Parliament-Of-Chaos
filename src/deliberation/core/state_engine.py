"""
Structured state engine for Parliament of Chaos.
Manages debate state as structured data with rolling memory compression.
"""

from typing import Dict, List, Optional
import json
import logging
from datetime import datetime

from ..models.schemas import (
    DebateState, AgentPosition, RoundSummary, 
    DebateStatement, Vote
)

logger = logging.getLogger(__name__)


class StateEngine:
    """
    Manages structured debate state.
    Agents receive current state, previous summary, and their last position.
    Full transcripts are NOT persisted unless explicitly required.
    """
    
    def __init__(self, initial_state: Optional[DebateState] = None):
        self.state = initial_state or DebateState()
        self._round_transcripts: Dict[int, List[str]] = {}  # Temporary, discarded after compression
        self._metadata: Dict[str, any] = {
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_current_state(self) -> DebateState:
        """Get current structured state."""
        return self.state
    
    def get_agent_context(self, agent_id: str) -> Dict:
        """
        Get context for a specific agent.
        Returns: current state, previous round summary, agent's last position.
        Does NOT include full transcripts.
        """
        context = {
            "round": self.state.round,
            "policy_vector": self.state.policy_vector,
            "open_amendments": self.state.open_amendments,
            "conflict_map": self.state.conflict_map,
            "agent_position": self.state.agent_positions.get(agent_id),
            "previous_summary": None
        }
        
        # Add previous round summary if it exists
        prev_round = self.state.round - 1
        if prev_round >= 0:
            prev_summary_key = f"round_{prev_round}"
            context["previous_summary"] = self.state.history_summary.get(prev_summary_key)
        
        return context
    
    def update_agent_position(self, agent_id: str, statement: DebateStatement):
        """
        Update an agent's position based on their debate statement.
        Mutates state only after validation.
        """
        if agent_id not in self.state.agent_positions:
            self.state.agent_positions[agent_id] = AgentPosition(
                stance=statement.position,
                confidence=statement.confidence,
                influence_score=1.0,  # Default influence
                stability_index=1.0    # First position is stable
            )
        else:
            # Update existing position
            old_position = self.state.agent_positions[agent_id]
            
            # Calculate stability (how much position changed)
            position_changed = old_position.stance != statement.position
            if position_changed:
                # Reduce stability if position changed
                old_position.stability_index *= 0.9
            else:
                # Increase stability if position held
                old_position.stability_index = min(1.0, old_position.stability_index + 0.1)
            
            old_position.stance = statement.position
            old_position.confidence = statement.confidence
        
        self._metadata["last_updated"] = datetime.utcnow().isoformat()
        logger.info(f"Updated position for agent '{agent_id}'")
    
    def add_amendment(self, amendment: str):
        """Add an amendment to open amendments."""
        if amendment and amendment not in self.state.open_amendments:
            self.state.open_amendments.append(amendment)
            logger.info(f"Added amendment: {amendment[:50]}...")
    
    def resolve_amendment(self, amendment: str):
        """Remove an amendment from open amendments (resolved/rejected)."""
        if amendment in self.state.open_amendments:
            self.state.open_amendments.remove(amendment)
            logger.info(f"Resolved amendment: {amendment[:50]}...")
    
    def track_conflict(self, agent_1: str, agent_2: str, issue: str):
        """Track a conflict between two agents."""
        conflict = {
            "agents": [agent_1, agent_2],
            "issue": issue,
            "round": self.state.round
        }
        self.state.conflict_map.append(conflict)
        logger.info(f"Tracked conflict between {agent_1} and {agent_2}")
    
    def add_to_transcript(self, round_num: int, content: str):
        """
        Add content to round transcript (temporary).
        These are discarded after round summary is generated.
        """
        if round_num not in self._round_transcripts:
            self._round_transcripts[round_num] = []
        self._round_transcripts[round_num].append(content)
    
    def compress_round(self, round_num: int, summary: RoundSummary):
        """
        Compress a round using rolling memory compression.
        1. Store structured summary
        2. Discard raw transcript
        3. Advance round counter
        """
        summary_key = f"round_{round_num}"
        self.state.history_summary[summary_key] = summary
        
        # Discard raw transcript
        if round_num in self._round_transcripts:
            transcript_size = len(self._round_transcripts[round_num])
            del self._round_transcripts[round_num]
            logger.info(
                f"Compressed round {round_num}: "
                f"Discarded {transcript_size} transcript entries, stored summary"
            )
        
        # Advance round
        self.state.round += 1
        self._metadata["last_updated"] = datetime.utcnow().isoformat()
    
    def get_round_transcript(self, round_num: int) -> List[str]:
        """
        Get raw transcript for a round (if still available).
        Returns empty list if already compressed.
        """
        return self._round_transcripts.get(round_num, [])
    
    def calculate_consensus_level(self) -> float:
        """
        Calculate current consensus level based on agent positions.
        Returns value between 0 (total disagreement) and 1 (full consensus).
        """
        if not self.state.agent_positions:
            return 0.0
        
        # Group agents by stance
        stance_groups: Dict[str, int] = {}
        for position in self.state.agent_positions.values():
            stance = position.stance.lower().strip()
            stance_groups[stance] = stance_groups.get(stance, 0) + 1
        
        if not stance_groups:
            return 0.0
        
        # Calculate consensus as proportion in largest group
        total_agents = len(self.state.agent_positions)
        largest_group = max(stance_groups.values())
        consensus = largest_group / total_agents
        
        return consensus
    
    def export_state(self) -> Dict:
        """Export current state as dictionary (for persistence)."""
        return {
            "state": self.state.model_dump(),
            "metadata": self._metadata
        }
    
    def import_state(self, data: Dict):
        """Import state from dictionary (for loading)."""
        self.state = DebateState(**data["state"])
        self._metadata = data.get("metadata", self._metadata)
        logger.info(f"Imported state from round {self.state.round}")
    
    def reset(self):
        """Reset to initial state."""
        self.state = DebateState()
        self._round_transcripts.clear()
        self._metadata = {
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }
        logger.info("State engine reset")
