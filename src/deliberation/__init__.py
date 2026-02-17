"""
Parliament of Chaos Deliberation System
Main package initialization
"""

__version__ = "0.1.0"

from .models.schemas import (
    DebateStatement,
    Vote,
    RoundSummary,
    DebateState,
    MetaAnalysis,
    DeliberationConfig,
    PerformanceMetrics,
    AgentPosition,
    AgentAlignment
)

from .core.debate_controller import DebateController
from .core.state_engine import StateEngine
from .core.model_tier import ModelRegistry, configure_models
from .utils.validation import Validator

__all__ = [
    "DebateController",
    "StateEngine",
    "ModelRegistry",
    "Validator",
    "configure_models",
    "DebateStatement",
    "Vote",
    "RoundSummary",
    "DebateState",
    "MetaAnalysis",
    "DeliberationConfig",
    "PerformanceMetrics",
    "AgentPosition",
    "AgentAlignment",
]
