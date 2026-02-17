"""
Main debate controller for Parliament of Chaos.
Orchestrates all components for structured multi-agent deliberation.
"""

import asyncio
from typing import List, Dict, Optional
import logging

from ..models.schemas import (
    DeliberationConfig, DebateState, DebateStatement, 
    Vote, RoundSummary, MetaAnalysis
)
from ..core.state_engine import StateEngine
from ..core.model_tier import ModelCaller, get_registry
from ..core.meta_observer import MetaObserver, Summariser
from ..core.metrics import MetricsCollector
from ..agents.agent_runtime import AgentRuntime
from ..utils.validation import Validator

logger = logging.getLogger(__name__)


class DebateController:
    """
    Central controller for structured deliberation.
    
    Architecture:
    DebateController
    ├── AgentRuntime (parallel)
    ├── StateEngine (structured memory)
    ├── MetaObserver
    ├── Validator
    ├── Summariser
    └── MetricsCollector
    
    Agents must not directly communicate.
    All interaction flows through DebateController.
    """
    
    def __init__(self, config: DeliberationConfig, 
                 model_caller: Optional[ModelCaller] = None):
        self.config = config
        
        # Initialize components
        self.model_caller = model_caller or ModelCaller(get_registry())
        self.validator = Validator(max_retries=1)
        self.state_engine = StateEngine()
        self.meta_observer = MetaObserver(
            self.model_caller,
            convergence_threshold=config.convergence_threshold,
            novelty_threshold=config.novelty_threshold
        )
        self.summariser = Summariser(self.model_caller)
        self.metrics = MetricsCollector()
        self.agent_runtime = AgentRuntime(
            self.model_caller, self.validator, config
        )
        
        self._debate_active = False
    
    async def run_deliberation(
        self, topic: str, agents: List[str], 
        initial_context: Optional[Dict] = None
    ) -> Dict:
        """
        Run complete deliberation session.
        
        Args:
            topic: Debate topic
            agents: List of agent IDs to participate
            initial_context: Optional initial context
            
        Returns:
            Dictionary with final state, metrics, and outcome
        """
        if self._debate_active:
            raise RuntimeError("Debate already in progress")
        
        self._debate_active = True
        self.metrics.start_debate()
        
        logger.info(
            f"Starting deliberation: topic='{topic}', "
            f"agents={len(agents)}, mode={self.config.mode}"
        )
        
        try:
            # Run debate rounds
            for round_num in range(self.config.max_rounds):
                logger.info(f"=== Round {round_num + 1}/{self.config.max_rounds} ===")
                
                # Execute round
                continue_debate = await self._execute_round(
                    topic, agents, initial_context or {}
                )
                
                if not continue_debate:
                    logger.info("Debate terminated early (convergence or low novelty)")
                    break
            
            # Final voting phase
            final_proposal = await self._generate_final_proposal(topic)
            votes = await self._execute_voting(agents, topic, final_proposal)
            
            # Calculate outcome
            outcome = self._determine_outcome(votes)
            
        finally:
            self._debate_active = False
            self.metrics.end_debate()
        
        # Return results
        return {
            "topic": topic,
            "outcome": outcome,
            "final_state": self.state_engine.export_state(),
            "metrics": self.metrics.export_metrics(),
            "config": self.config.model_dump()
        }
    
    async def _execute_round(
        self, topic: str, agents: List[str], context: Dict
    ) -> bool:
        """
        Execute a single debate round.
        
        Returns:
            True if debate should continue, False to terminate
        """
        self.metrics.start_round()
        round_tokens = 0
        
        # Get current state
        state = self.state_engine.get_current_state()
        
        # Agents make statements in parallel
        if state.round == 0:
            # Opening statements
            results = await self.agent_runtime.execute_parallel([
                self.agent_runtime._create_opening_statement_prompt(
                    agent_id, topic, self.state_engine.get_agent_context(agent_id)
                )
                for agent_id in agents
            ])
        else:
            # Rebuttals based on previous round
            prev_summary_key = f"round_{state.round - 1}"
            prev_summary = state.history_summary.get(prev_summary_key)
            results = await self.agent_runtime.execute_parallel([
                self.agent_runtime._create_rebuttal_prompt(
                    agent_id, topic, 
                    self.state_engine.get_agent_context(agent_id),
                    prev_summary
                )
                for agent_id in agents
            ])
        
        # Extract valid statements
        statements: List[DebateStatement] = []
        for result in results:
            if result.success and result.data:
                statements.append(result.data)
                # Estimate tokens (rough)
                round_tokens += len(str(result.data.model_dump())) // 4
        
        # Update state with statements
        for statement in statements:
            self.state_engine.update_agent_position(statement.agent_id, statement)
            if statement.amendment:
                self.state_engine.add_amendment(statement.amendment)
            
            # Add to temporary transcript
            self.state_engine.add_to_transcript(
                state.round,
                f"{statement.agent_id}: {statement.position}"
            )
        
        # Meta-analysis
        analysis = self.meta_observer.analyze_round(statements, state)
        
        # Generate round summary (rolling compression)
        summary = await self.summariser.generate_summary_async(statements, state)
        
        # Compress round (discard transcript, keep summary)
        self.state_engine.compress_round(state.round, summary)
        
        # Update metrics
        self.metrics.end_round(round_tokens)
        self.metrics.calculate_position_entropy(self.state_engine.get_current_state())
        
        # Check for convergence
        if summary.consensus_level >= self.config.convergence_threshold:
            self.metrics.record_convergence(state.round)
        
        # Decide if debate should continue
        return self.meta_observer.should_continue(analysis)
    
    async def _generate_final_proposal(self, topic: str) -> str:
        """
        Generate final proposal based on debate state.
        Uses chair model tier.
        """
        state = self.state_engine.get_current_state()
        
        # Build proposal prompt
        positions_summary = "\n".join([
            f"- {agent_id}: {pos.stance}"
            for agent_id, pos in state.agent_positions.items()
        ])
        
        prompt = f"""ROLE: Chair/Arbiter

OBJECTIVE: Synthesize final proposal from debate

TOPIC: {topic}

AGENT POSITIONS:
{positions_summary}

OPEN AMENDMENTS:
{chr(10).join(['- ' + a for a in state.open_amendments[:5]])}

Generate a clear, actionable final proposal that reflects the debate consensus.
Maximum 200 words."""
        
        proposal = await self.model_caller.call_model_async(
            role="chair",
            prompt=prompt,
            temperature=0.7
        )
        
        logger.info(f"Generated final proposal: {proposal[:100]}...")
        return proposal
    
    async def _execute_voting(
        self, agents: List[str], topic: str, final_proposal: str
    ) -> List[Vote]:
        """Execute parallel voting on final proposal."""
        # Build voting prompts
        prompts = []
        for agent_id in agents:
            context = self.state_engine.get_agent_context(agent_id)
            prompt_text = self.agent_runtime._build_voting_prompt(
                agent_id, topic, context, final_proposal
            )
            prompts.append(self.agent_runtime.AgentPrompt(
                agent_id=agent_id,
                role="agent",
                prompt=prompt_text,
                expected_schema=Vote
            ))
        
        # Execute voting in parallel
        results = await self.agent_runtime.execute_parallel(prompts)
        
        # Extract valid votes
        votes = [result.data for result in results if result.success and result.data]
        
        logger.info(
            f"Voting complete: "
            f"{len([v for v in votes if v.vote == 'approve'])} approve, "
            f"{len([v for v in votes if v.vote == 'reject'])} reject, "
            f"{len([v for v in votes if v.vote == 'abstain'])} abstain"
        )
        
        return votes
    
    def _determine_outcome(self, votes: List[Vote]) -> Dict:
        """
        Determine debate outcome based on votes and voting system.
        
        Returns:
            Dictionary with outcome details
        """
        if not votes:
            return {"result": "no_quorum", "approved": False}
        
        approve_count = len([v for v in votes if v.vote == "approve"])
        reject_count = len([v for v in votes if v.vote == "reject"])
        abstain_count = len([v for v in votes if v.vote == "abstain"])
        
        total_votes = len(votes)
        participating_votes = approve_count + reject_count
        
        # Apply voting system
        if self.config.voting_system == "majority":
            threshold = participating_votes / 2
            approved = approve_count > threshold
        
        elif self.config.voting_system == "supermajority":
            threshold = participating_votes * 0.66
            approved = approve_count >= threshold
        
        elif self.config.voting_system == "influence_weighted":
            # Weight votes by influence score
            state = self.state_engine.get_current_state()
            weighted_approve = sum([
                state.agent_positions.get(v.agent_id, AgentPosition(
                    stance="", confidence=0, influence_score=1.0
                )).influence_score
                for v in votes if v.vote == "approve"
            ])
            weighted_reject = sum([
                state.agent_positions.get(v.agent_id, AgentPosition(
                    stance="", confidence=0, influence_score=1.0
                )).influence_score
                for v in votes if v.vote == "reject"
            ])
            approved = weighted_approve > weighted_reject
        
        else:  # quadratic or default to majority
            threshold = participating_votes / 2
            approved = approve_count > threshold
        
        return {
            "result": "approved" if approved else "rejected",
            "approved": approved,
            "votes": {
                "approve": approve_count,
                "reject": reject_count,
                "abstain": abstain_count,
                "total": total_votes
            },
            "voting_system": self.config.voting_system
        }
    
    def get_state(self) -> DebateState:
        """Get current debate state."""
        return self.state_engine.get_current_state()
    
    def get_metrics(self) -> Dict:
        """Get current performance metrics."""
        return self.metrics.get_metrics().model_dump()
    
    def reset(self):
        """Reset controller for new debate."""
        self.state_engine.reset()
        self.meta_observer.reset()
        self.metrics.reset()
        self._debate_active = False
        logger.info("Debate controller reset")
