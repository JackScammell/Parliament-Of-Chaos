"""
Structured schemas for Parliament of Chaos deliberation system.
All agents MUST output strict JSON matching these predefined schemas.
"""

from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field, field_validator


class DebateStatement(BaseModel):
    """Schema for agent debate statements."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    position: str = Field(..., description="Agent's stance on the topic")
    argument: str = Field(..., description="Supporting reasoning and evidence")
    amendment: Optional[str] = Field(None, description="Proposed modification to policy")
    references: List[str] = Field(default_factory=list, description="Citations or supporting sources")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0-1)")

    @field_validator('confidence', mode='before')
    @classmethod
    def clamp_confidence(cls, v):
        """Ensure confidence is clamped between 0 and 1."""
        return max(0.0, min(1.0, float(v)))


class Vote(BaseModel):
    """Schema for agent voting."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    vote: Literal["approve", "reject", "abstain"] = Field(..., description="Vote decision")
    reasoning: str = Field(..., description="Explanation for vote")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in vote (0-1)")

    @field_validator('confidence', mode='before')
    @classmethod
    def clamp_confidence(cls, v):
        """Ensure confidence is clamped between 0 and 1."""
        return max(0.0, min(1.0, float(v)))


class RoundSummary(BaseModel):
    """Schema for round summary after each debate round."""
    core_positions: List[str] = Field(default_factory=list, description="Key positions from round")
    major_conflicts: List[str] = Field(default_factory=list, description="Significant disagreements")
    amendments: List[str] = Field(default_factory=list, description="Proposed changes")
    consensus_level: float = Field(..., ge=0.0, le=1.0, description="Degree of consensus (0-1)")

    @field_validator('consensus_level', mode='before')
    @classmethod
    def clamp_consensus(cls, v):
        """Ensure consensus level is clamped between 0 and 1."""
        return max(0.0, min(1.0, float(v)))


class AgentAlignment(BaseModel):
    """Schema for agent ideological alignment."""
    economic: float = Field(..., ge=-1.0, le=1.0, description="Economic alignment (-1 to 1)")
    social: float = Field(..., ge=-1.0, le=1.0, description="Social alignment (-1 to 1)")
    risk_tolerance: float = Field(..., ge=-1.0, le=1.0, description="Risk tolerance (-1 to 1)")

    @field_validator('economic', 'social', 'risk_tolerance', mode='before')
    @classmethod
    def clamp_alignment(cls, v):
        """Ensure alignment values are clamped between -1 and 1."""
        return max(-1.0, min(1.0, float(v)))


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

    @field_validator('novelty_score', 'argument_overlap', 'convergence_trend', mode='before')
    @classmethod
    def clamp_scores(cls, v):
        """Ensure scores are clamped between 0 and 1."""
        return max(0.0, min(1.0, float(v)))


class DeliberationConfig(BaseModel):
    """Configuration schema for debate runtime."""
    mode: Literal["fast", "adversarial", "consensus", "deep_deliberation", "team_debate"] = Field(
        "consensus", description="Deliberation mode"
    )
    max_rounds: int = Field(5, ge=1, description="Maximum number of rounds")
    max_tokens_per_agent: int = Field(300, ge=50, description="Token limit per agent response")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    convergence_threshold: float = Field(0.85, ge=0.0, le=1.0, description="Consensus threshold")
    novelty_threshold: float = Field(0.1, ge=0.0, le=1.0, description="Minimum novelty to continue")
    voting_system: Literal["majority", "supermajority", "quadratic", "influence_weighted", "delegated", "coalition"] = Field(
        "majority", description="Voting system type"
    )
    use_persistent_memory: bool = Field(False, description="Enable cross-session memory")
    enable_constraints: bool = Field(False, description="Enable user-defined constraints")
    enable_self_improvement: bool = Field(False, description="Enable meta-learning")


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
    # Analytics extensions
    consensus_score: float = Field(0.0, ge=0.0, le=1.0, description="Overall consensus level")
    agent_influence_scores: Dict[str, float] = Field(default_factory=dict, description="Agent influence ratings")
    argument_novelty_scores: List[float] = Field(default_factory=list, description="Novelty by round")
    time_to_convergence: Optional[float] = Field(None, description="Time to reach convergence (seconds)")


class TeamRole(BaseModel):
    """Schema for debate team roles."""
    role: Literal["advocate", "opponent", "moderator", "synthesis"] = Field(..., description="Team role type")
    description: str = Field(..., description="Role description")
    agents: List[str] = Field(default_factory=list, description="Agents assigned to this role")
    priority: int = Field(1, ge=1, le=4, description="Role priority in debate flow")


class DebateTeamsConfig(BaseModel):
    """Configuration for structured debate teams."""
    enable_teams: bool = Field(False, description="Enable team-based debate mode")
    teams: List[TeamRole] = Field(default_factory=list, description="Debate teams")
    team_coordination_mode: Literal["sequential", "parallel", "hybrid"] = Field(
        "parallel", description="How teams interact"
    )


class AgentSkillTree(BaseModel):
    """Hierarchical skill tree for specialist agents."""
    agent_id: str = Field(..., description="Agent identifier")
    primary_domain: str = Field(..., description="Main area of expertise")
    skills: Dict[str, List[str]] = Field(default_factory=dict, description="Hierarchical skills")
    skill_level: Dict[str, int] = Field(default_factory=dict, description="Proficiency per skill (1-5)")


class MemoryEntry(BaseModel):
    """Schema for persistent memory entries."""
    session_id: str = Field(..., description="Debate session identifier")
    topic: str = Field(..., description="Debate topic")
    timestamp: str = Field(..., description="ISO timestamp")
    outcome: Dict = Field(default_factory=dict, description="Debate outcome")
    key_learnings: List[str] = Field(default_factory=list, description="Lessons learned")
    patterns: List[str] = Field(default_factory=list, description="Identified patterns")
    embeddings: Optional[List[float]] = Field(None, description="Vector embedding for semantic search")


class ConstraintDefinition(BaseModel):
    """User-defined constraints for debates."""
    max_rounds: Optional[int] = Field(None, description="Override max rounds")
    disallowed_patterns: List[str] = Field(default_factory=list, description="Patterns to avoid")
    required_validators: List[str] = Field(default_factory=list, description="Must-pass validation rules")
    custom_rules: Dict[str, str] = Field(default_factory=dict, description="Custom constraint rules")


class SessionState(BaseModel):
    """State for multi-session debate chaining."""
    session_id: str = Field(..., description="Current session ID")
    previous_sessions: List[str] = Field(default_factory=list, description="Linked previous sessions")
    carried_forward_context: Dict = Field(default_factory=dict, description="Context from previous sessions")
    unresolved_conflicts: List[str] = Field(default_factory=list, description="Conflicts needing resolution")
    session_summaries: Dict[str, str] = Field(default_factory=dict, description="Summaries by session")


class MetaLearning(BaseModel):
    """Meta-learning data for self-improvement."""
    strategy_id: str = Field(..., description="Strategy identifier")
    performance_history: List[float] = Field(default_factory=list, description="Performance scores")
    adaptation_count: int = Field(0, description="Number of adaptations")
    successful_patterns: List[str] = Field(default_factory=list, description="Winning patterns")
    failed_patterns: List[str] = Field(default_factory=list, description="Patterns to avoid")
