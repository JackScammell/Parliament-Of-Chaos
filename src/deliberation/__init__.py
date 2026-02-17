"""
Parliament of Chaos Deliberation System
Main package initialization
"""

__version__ = "0.2.0"

from .models.schemas import (
    DebateStatement,
    Vote,
    RoundSummary,
    DebateState,
    MetaAnalysis,
    DeliberationConfig,
    PerformanceMetrics,
    AgentPosition,
    AgentAlignment,
    TeamRole,
    DebateTeamsConfig,
    AgentSkillTree,
    MemoryEntry,
    ConstraintDefinition,
    SessionState,
    MetaLearning
)

from .core.debate_controller import DebateController
from .core.state_engine import StateEngine
from .core.model_tier import ModelRegistry, configure_models
from .core.session_manager import SessionManager
from .core.self_improvement import SelfImprovementEngine
from .utils.validation import Validator

from .memory import MemoryManager, MemoryStore
from .plugins import PluginManager, PluginRegistry
from .analytics import DebateDashboard, AnalyticsEngine
from .constraints import ConstraintValidator, ConstraintLoader
from .governance import VotingSystemManager, CoalitionBuilder
from .agents.skill_trees import SkillTreeManager
from .agents.team_coordinator import TeamCoordinator, create_default_debate_teams

__all__ = [
    # Core
    "DebateController",
    "StateEngine",
    "ModelRegistry",
    "Validator",
    "configure_models",
    "SessionManager",
    "SelfImprovementEngine",
    
    # Schemas
    "DebateStatement",
    "Vote",
    "RoundSummary",
    "DebateState",
    "MetaAnalysis",
    "DeliberationConfig",
    "PerformanceMetrics",
    "AgentPosition",
    "AgentAlignment",
    "TeamRole",
    "DebateTeamsConfig",
    "AgentSkillTree",
    "MemoryEntry",
    "ConstraintDefinition",
    "SessionState",
    "MetaLearning",
    
    # Memory
    "MemoryManager",
    "MemoryStore",
    
    # Plugins
    "PluginManager",
    "PluginRegistry",
    
    # Analytics
    "DebateDashboard",
    "AnalyticsEngine",
    
    # Constraints
    "ConstraintValidator",
    "ConstraintLoader",
    
    # Governance
    "VotingSystemManager",
    "CoalitionBuilder",
    
    # Agents
    "SkillTreeManager",
    "TeamCoordinator",
    "create_default_debate_teams",
]
