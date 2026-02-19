"""
Agent runtime for Parliament of Chaos.
Handles parallel execution of independent agent calls.
"""

import asyncio
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass
import logging
from datetime import datetime

from ..models.schemas import DebateStatement, Vote, DeliberationConfig
from ..core.model_tier import ModelCaller, ModelRole
from ..utils.validation import Validator, ValidationResult
from ..core.context_manager import ContextManager

logger = logging.getLogger(__name__)


@dataclass
class AgentPrompt:
    """Container for agent prompt configuration."""
    agent_id: str
    role: ModelRole
    prompt: str
    expected_schema: Any


class AgentRuntime:
    """
    Runtime for executing agent calls in parallel.
    All independent agent calls MUST run concurrently.
    
    Supports optimized context management for token reduction.
    """
    
    def __init__(self, model_caller: ModelCaller, validator: Validator,
                 config: DeliberationConfig, context_manager: Optional[ContextManager] = None):
        self.model_caller = model_caller
        self.validator = validator
        self.config = config
        self.context_manager = context_manager  # Optional context optimization
        self._metrics: Dict[str, Any] = {
            "total_calls": 0,
            "parallel_batches": 0,
            "average_latency": 0.0
        }
    
    async def execute_parallel(self, prompts: List[AgentPrompt]) -> List[ValidationResult]:
        """
        Execute multiple agent prompts in parallel.
        
        Args:
            prompts: List of agent prompts to execute
            
        Returns:
            List of validation results (one per prompt)
        """
        if not prompts:
            return []
        
        start_time = datetime.utcnow()
        logger.info(f"Executing {len(prompts)} agent calls in parallel")
        
        # Execute all calls concurrently using asyncio.gather
        tasks = [
            self._execute_single_async(prompt)
            for prompt in prompts
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent {prompts[i].agent_id} failed: {str(result)}")
                processed_results.append(ValidationResult(
                    success=False,
                    errors=[{"type": "runtime", "message": str(result)}]
                ))
            else:
                processed_results.append(result)
        
        # Update metrics
        end_time = datetime.utcnow()
        latency = (end_time - start_time).total_seconds()
        self._metrics["total_calls"] += len(prompts)
        self._metrics["parallel_batches"] += 1
        
        # Update average latency
        old_avg = self._metrics["average_latency"]
        batch_count = self._metrics["parallel_batches"]
        self._metrics["average_latency"] = (old_avg * (batch_count - 1) + latency) / batch_count
        
        logger.info(
            f"Parallel execution completed in {latency:.2f}s "
            f"({len([r for r in processed_results if r.success])} successful)"
        )
        
        return processed_results
    
    async def _execute_single_async(self, prompt: AgentPrompt) -> ValidationResult:
        """
        Execute a single agent prompt asynchronously.
        
        Args:
            prompt: Agent prompt configuration
            
        Returns:
            Validation result for the agent's output
        """
        try:
            # Call model asynchronously
            raw_output = await self.model_caller.call_model_async(
                role=prompt.role,
                prompt=prompt.prompt,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens_per_agent
            )
            
            # Validate output
            result = self.validator.validate(raw_output, prompt.expected_schema)
            
            if not result.success:
                logger.warning(f"Agent {prompt.agent_id} produced invalid output")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing agent {prompt.agent_id}: {str(e)}")
            return ValidationResult(
                success=False,
                errors=[{"type": "execution", "message": str(e)}]
            )
    
    def execute_opening_statements(
        self, agents: List[str], topic: str, context: Dict
    ) -> asyncio.Future:
        """
        Execute opening statements for all agents in parallel.
        
        Args:
            agents: List of agent IDs
            topic: Debate topic
            context: Debate context
            
        Returns:
            Future that resolves to list of DebateStatements
        """
        prompts = []
        for agent_id in agents:
            prompt_text = self._build_opening_statement_prompt(agent_id, topic, context)
            prompts.append(AgentPrompt(
                agent_id=agent_id,
                role="agent",
                prompt=prompt_text,
                expected_schema=DebateStatement
            ))
        
        return asyncio.create_task(self.execute_parallel(prompts))
    
    def execute_rebuttals(
        self, agents: List[str], topic: str, context: Dict, 
        previous_statements: List[DebateStatement]
    ) -> asyncio.Future:
        """
        Execute rebuttals for all agents in parallel.
        
        Args:
            agents: List of agent IDs
            topic: Debate topic
            context: Current debate context
            previous_statements: Statements from previous round
            
        Returns:
            Future that resolves to list of DebateStatements
        """
        prompts = []
        for agent_id in agents:
            prompt_text = self._build_rebuttal_prompt(
                agent_id, topic, context, previous_statements
            )
            prompts.append(AgentPrompt(
                agent_id=agent_id,
                role="agent",
                prompt=prompt_text,
                expected_schema=DebateStatement
            ))
        
        return asyncio.create_task(self.execute_parallel(prompts))
    
    def execute_voting(
        self, agents: List[str], topic: str, context: Dict, 
        final_proposal: str
    ) -> asyncio.Future:
        """
        Execute voting for all agents in parallel.
        
        Args:
            agents: List of agent IDs
            topic: Debate topic
            context: Current debate context
            final_proposal: Proposal to vote on
            
        Returns:
            Future that resolves to list of Votes
        """
        prompts = []
        for agent_id in agents:
            prompt_text = self._build_voting_prompt(
                agent_id, topic, context, final_proposal
            )
            prompts.append(AgentPrompt(
                agent_id=agent_id,
                role="agent",
                prompt=prompt_text,
                expected_schema=Vote
            ))
        
        return asyncio.create_task(self.execute_parallel(prompts))
    
    def _build_opening_statement_prompt(
        self, agent_id: str, topic: str, context: Dict
    ) -> str:
        """
        Build standardized prompt for opening statement.
        Uses optimized context if available.
        """
        if self.context_manager:
            # Use optimized context manager
            from ..models.schemas import AgentPosition
            agent_position = context.get("agent_position")
            if isinstance(agent_position, dict):
                # Convert dict to AgentPosition if needed
                agent_position = AgentPosition(**agent_position) if agent_position else None
            
            return self.context_manager.build_prompt_with_context(
                agent_id=agent_id,
                role=f"Debate Agent ({agent_id})",
                objective="Provide opening position on debate topic",
                agent_position=agent_position,
                topic=topic,
                max_tokens=self.config.max_tokens_per_agent,
                schema_name="DebateStatement"
            )
        
        # Legacy prompt building (more verbose)
        return f"""ROLE: Debate Agent ({agent_id})

OBJECTIVE: Provide opening position on debate topic

CONSTRAINTS:
- Maximum {self.config.max_tokens_per_agent} tokens
- Must output strict JSON matching DebateStatement schema
- No free-form prose outside schema

DEBATE TOPIC: {topic}

CONTEXT: {context}

OUTPUT FORMAT:
{{
  "agent_id": "{agent_id}",
  "position": "your stance",
  "argument": "supporting reasoning",
  "amendment": "proposed modification or null",
  "references": ["source1", "source2"],
  "confidence": 0.0-1.0
}}

Respond with ONLY valid JSON matching the schema above."""
    
    def _build_rebuttal_prompt(
        self, agent_id: str, topic: str, context: Dict, 
        previous_statements: List[DebateStatement]
    ) -> str:
        """Build standardized prompt for rebuttal."""
        previous_summary = "\n".join([
            f"- {s.agent_id}: {s.position} (confidence: {s.confidence})"
            for s in previous_statements
        ])
        
        return f"""ROLE: Debate Agent ({agent_id})

OBJECTIVE: Respond to previous statements and refine position

CONSTRAINTS:
- Maximum {self.config.max_tokens_per_agent} tokens
- Must output strict JSON matching DebateStatement schema
- No free-form prose outside schema

DEBATE TOPIC: {topic}

PREVIOUS STATEMENTS:
{previous_summary}

CONTEXT: {context}

OUTPUT FORMAT:
{{
  "agent_id": "{agent_id}",
  "position": "your stance",
  "argument": "supporting reasoning addressing previous points",
  "amendment": "proposed modification or null",
  "references": ["source1", "source2"],
  "confidence": 0.0-1.0
}}

Respond with ONLY valid JSON matching the schema above."""
    
    def _build_voting_prompt(
        self, agent_id: str, topic: str, context: Dict, final_proposal: str
    ) -> str:
        """Build standardized prompt for voting."""
        return f"""ROLE: Debate Agent ({agent_id})

OBJECTIVE: Cast vote on final proposal

CONSTRAINTS:
- Must output strict JSON matching Vote schema
- No free-form prose outside schema

DEBATE TOPIC: {topic}

FINAL PROPOSAL: {final_proposal}

CONTEXT: {context}

OUTPUT FORMAT:
{{
  "agent_id": "{agent_id}",
  "vote": "approve|reject|abstain",
  "reasoning": "explanation for vote",
  "confidence": 0.0-1.0
}}

Respond with ONLY valid JSON matching the schema above."""
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get runtime performance metrics."""
        return self._metrics.copy()
