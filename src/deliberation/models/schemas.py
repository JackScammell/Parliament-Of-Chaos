"""
Structured schemas for Parliament of Chaos deliberation system.
All agents MUST output strict JSON matching these predefined schemas.
"""

from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field, validator


class DebateStatement(BaseModel):
    """Schema for agent debate statements."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    position: str = Field(..., description="Agent's stance on the topic")
    argument: str = Field(..., description="Supporting reasoning and evidence")
    amendment: Optional[str] = Field(None, description="Proposed modification to policy")
    references: List[str] = Field(default_factory=list, description="Citations or supporting sources")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0-1)")

    @validator('confidence')
    def clamp_confidence(cls, v):
        """Ensure confidence is clamped between 0 and 1."""
        return max(0.0, min(1.0, v))


class Vote(BaseModel):
    """Schema for agent voting."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    vote: Literal["approve", "reject", "abstain"] = Field(..., description="Vote decision")
    reasoning: str = Field(..., description="Explanation for vote")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in vote (0-1)")

    @validator('confidence')
    def clamp_confidence(cls, v):
        """Ensure confidence is clamped between 0 and 1."""
        return max(0.0, min(1.0, v))


class RoundSummary(BaseModel):
    """Schema for round summary after each debate round."""
    core_positions: List[str] = Field(default_factory=list, description="Key positions from round")
    major_conflicts: List[str] = Field(default_factory=list, description="Significant disagreements")
    amendments: List[str] = Field(default_factory=list, description="Proposed changes")
    consensus_level: float = Field(..., ge=0.0, le=1.0, description="Degree of consensus (0-1)")

    @validator('consensus_level')
    def clamp_consensus(cls, v):
        """Ensure consensus level is clamped between 0 and 1."""
        return max(0.0, min(1.0, v))


class AgentAlignment(BaseModel):
    """Schema for agent ideological alignment."""
    economic: float = Field(..., ge=-1.0, le=1.0, description="Economic alignment (-1 to 1)")
    social: float = Field(..., ge=-1.0, le=1.0, description="Social alignment (-1 to 1)")
    risk_tolerance: float = Field(..., ge=-1.0, le=1.0, description="Risk tolerance (-1 to 1)")

    @validator('economic', 'social', 'risk_tolerance')
    def clamp_alignment(cls, v):
        """Ensure alignment values are clamped between -1 and 1."""
        return max(-1.0, min(1.0, v))


class AgentPosition(BaseModel):
    """Schema for agent's current position in debate."""
    stance: str = Field(..., description="Current position on the topic")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in stance")
    influence_score: float = Field(0.0, ge=0.0, description="Agent's influence weight")
    stability_index: float = Field(0.0, ge=0.0, le=1.0, description="Consistency of position")
    alignment: Optional[AgentAlignment] = Field(None, description="Ideological alignment")


class DebateState(BaseModel):
    """Structured debate state - the single source of truth."""
    round: int = Field(0, ge=0, description="Current round number")
    policy_vector: Dict[str, float] = Field(default_factory=dict, description="Policy position vectors")
    agent_positions: Dict[str, AgentPosition] = Field(default_factory=dict, description="Agent stances")
    open_amendments: List[str] = Field(default_factory=list, description="Active amendments")
    conflict_map: List[Dict[str, str]] = Field(default_factory=list, description="Tracked conflicts")
    history_summary: Dict[str, RoundSummary] = Field(default_factory=dict, description="Compressed history")


class MetaAnalysis(BaseModel):
    """Schema for meta-agent observer analysis."""
    novelty_score: float = Field(..., ge=0.0, le=1.0, description="Novelty of arguments")
    argument_overlap: float = Field(..., ge=0.0, le=1.0, description="Degree of redundancy")
    convergence_trend: float = Field(..., ge=0.0, le=1.0, description="Trend toward consensus")
    recommend_terminate: bool = Field(False, description="Should debate end early")

    @validator('novelty_score', 'argument_overlap', 'convergence_trend')
    def clamp_scores(cls, v):
        """Ensure scores are clamped between 0 and 1."""
        return max(0.0, min(1.0, v))


class DeliberationConfig(BaseModel):
    """Configuration schema for debate runtime."""
    mode: Literal["fast", "adversarial", "consensus", "deep_deliberation"] = Field(
        "consensus", description="Deliberation mode"
    )
    max_rounds: int = Field(5, ge=1, description="Maximum number of rounds")
    max_tokens_per_agent: int = Field(300, ge=50, description="Token limit per agent response")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    convergence_threshold: float = Field(0.85, ge=0.0, le=1.0, description="Consensus threshold")
    novelty_threshold: float = Field(0.1, ge=0.0, le=1.0, description="Minimum novelty to continue")
    voting_system: Literal["majority", "supermajority", "quadratic", "influence_weighted"] = Field(
        "majority", description="Voting system type"
    )


class PerformanceMetrics(BaseModel):
    """Schema for tracking debate performance metrics."""
    total_tokens: int = Field(0, ge=0, description="Total tokens used")
    tokens_per_round: List[int] = Field(default_factory=list, description="Token usage by round")
    average_latency: float = Field(0.0, ge=0.0, description="Average response latency (seconds)")
    rounds_to_convergence: Optional[int] = Field(None, description="Rounds needed to reach consensus")
    position_entropy: float = Field(0.0, ge=0.0, description="Entropy of agent positions")
    argument_redundancy_score: float = Field(0.0, ge=0.0, le=1.0, description="Redundancy measure")
    start_time: Optional[str] = Field(None, description="Debate start timestamp")
    end_time: Optional[str] = Field(None, description="Debate end timestamp")
