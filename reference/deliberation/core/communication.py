"""
Communication abstraction layer for Parliament of Chaos.

Provides a unified interface for inter-agent communication that works with
the current Task()-based model today and can swap to Agent Teams when that
feature exits Claude Code's research preview.

Design rationale:
- Task() is the stable, production-ready approach (fire-and-forget subagents)
- Agent Teams (v2.1.32+) enables persistent messaging between agents
- This abstraction shields the orchestration layer from the transport mechanism
- Feature flag: PARLIAMENT_USE_AGENT_TEAMS=1 to opt-in when ready

Usage:
    layer = CommunicationLayer.create()
    response = await layer.send(agent="backend-goblin", message="Analyse perf")
    await layer.broadcast(agents=["reviewer-1", "reviewer-2"], message="Review this")
"""

import asyncio
import os
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Structured message between agents."""
    sender: str
    recipient: str
    content: str
    round_number: int = 0
    message_type: str = "request"  # request, response, broadcast


@dataclass
class AgentResponse:
    """Structured response from an agent."""
    agent: str
    content: str
    success: bool = True
    error: Optional[str] = None
    token_usage: int = 0


class CommunicationLayer(ABC):
    """
    Abstract communication layer for inter-agent messaging.

    Implementations:
    - TaskCommunication: Uses Task() subagent invocations (current, stable)
    - AgentTeamsCommunication: Uses Agent Teams messaging (future, experimental)
    """

    @staticmethod
    def create() -> "CommunicationLayer":
        """Factory method that selects implementation based on feature flags."""
        if os.environ.get("PARLIAMENT_USE_AGENT_TEAMS") == "1":
            logger.info("Using Agent Teams communication layer (experimental)")
            return AgentTeamsCommunication()
        return TaskCommunication()

    @abstractmethod
    async def send(self, agent: str, message: str, **kwargs) -> AgentResponse:
        """Send a message to a single agent and await response."""
        ...

    @abstractmethod
    async def broadcast(
        self, agents: List[str], message: str, **kwargs
    ) -> List[AgentResponse]:
        """Send a message to multiple agents in parallel."""
        ...

    @abstractmethod
    async def is_available(self, agent: str) -> bool:
        """Check if an agent is available for communication."""
        ...


class TaskCommunication(CommunicationLayer):
    """
    Communication via Task() subagent invocations.

    This is the current stable approach. Each send() creates a new Task()
    invocation. Broadcast uses parallel Task() calls.

    Limitations:
    - Fire-and-forget: no persistent message channel
    - No mid-task interruption or follow-up without new invocation
    - Each invocation starts a fresh agent context

    Strengths:
    - Stable and well-tested
    - Works with all Claude Code versions
    - Simple error model
    """

    async def send(self, agent: str, message: str, **kwargs) -> AgentResponse:
        """
        Send message via Task() invocation.

        In the actual plugin, this maps to the Agent tool's Task(agent_type)
        mechanism used by senior-council and deliberation-conductor.
        """
        logger.debug(f"TaskCommunication.send -> {agent}")
        return AgentResponse(
            agent=agent,
            content="",  # Populated by actual Task() invocation
            success=True,
        )

    async def broadcast(
        self, agents: List[str], message: str, **kwargs
    ) -> List[AgentResponse]:
        """
        Broadcast via parallel Task() invocations.

        Maps to launching multiple Agent tool calls in a single message
        for parallel execution.
        """
        logger.debug(f"TaskCommunication.broadcast -> {agents}")
        tasks = [self.send(agent, message, **kwargs) for agent in agents]
        return await asyncio.gather(*tasks)

    async def is_available(self, agent: str) -> bool:
        """Agents are always available in Task() model (new instance per call)."""
        return True


class AgentTeamsCommunication(CommunicationLayer):
    """
    Communication via Agent Teams messaging (experimental).

    Requires: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
    Available: Claude Code v2.1.32+
    Status: Research preview — do NOT use for production orchestration.

    Enables:
    - Persistent message channels between agents
    - Mid-task follow-up and interruption
    - TeammateIdle and TaskCompleted event handling
    - Shared context across message exchanges

    Go/no-go gate: Agent Teams must exit research preview before this
    implementation is used in production orchestration flows.
    """

    def __init__(self) -> None:
        logger.warning(
            "AgentTeamsCommunication is experimental. "
            "Set PARLIAMENT_USE_AGENT_TEAMS=0 to revert to stable Task() model."
        )

    async def send(self, agent: str, message: str, **kwargs) -> AgentResponse:
        """
        Send message via Agent Teams persistent channel.

        When Agent Teams exits research preview, this will use the
        SendMessage mechanism to communicate with persistent agent instances.
        """
        # Placeholder: will integrate with Agent Teams API when stable
        return AgentResponse(
            agent=agent,
            content="",
            success=False,
            error="Agent Teams integration not yet implemented. Awaiting stable release.",
        )

    async def broadcast(
        self, agents: List[str], message: str, **kwargs
    ) -> List[AgentResponse]:
        """Broadcast via Agent Teams persistent channels."""
        tasks = [self.send(agent, message, **kwargs) for agent in agents]
        return await asyncio.gather(*tasks)

    async def is_available(self, agent: str) -> bool:
        """Check if teammate agent is currently active (not idle)."""
        # Placeholder: will check TeammateIdle state when integrated
        return False
