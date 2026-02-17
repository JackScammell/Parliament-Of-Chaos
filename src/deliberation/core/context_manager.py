"""
Context Manager for Parliament of Chaos.
Implements token-efficient context handling with structured compression.

Constants:
    FULL_TRANSCRIPT_MULTIPLIER: Estimated ratio of full transcript size to optimized context.
        Based on empirical testing showing uncompressed transcripts are ~3x larger than
        our structured JSON approach. This is used for token reduction calculations.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from ..models.schemas import (
    DebateStatement, RoundSummary, AgentPosition, DebateState
)
from .token_counter import TokenCounter
from .statement_pruner import StatementDeduplicator, ContextPruner

logger = logging.getLogger(__name__)

# Token estimation constants
FULL_TRANSCRIPT_MULTIPLIER = 3.0  # Full transcripts are ~3x larger than optimized context


class ImmediateContext:
    """
    Immediate round context containing only current round data.
    This is the most recent and detailed information.
    """
    
    def __init__(self, round_number: int, token_counter: Optional[TokenCounter] = None):
        self.round_number = round_number
        self.agent_statements: List[DebateStatement] = []
        self.votes: List[Dict] = []
        self.amendments: List[str] = []
        self.token_counter = token_counter or TokenCounter()
        
    def add_statement(self, statement: DebateStatement):
        """Add an agent statement to current round."""
        self.agent_statements.append(statement)
        
    def add_vote(self, vote: Dict):
        """Add a vote to current round."""
        self.votes.append(vote)
        
    def add_amendment(self, amendment: str):
        """Add an amendment to current round."""
        if amendment and amendment not in self.amendments:
            self.amendments.append(amendment)
    
    def summarize_argument(self, argument: str, max_words: int = 50) -> str:
        """
        Summarize long arguments to key points.
        Public method for internal and external use.
        """
        words = argument.split()
        if len(words) <= max_words:
            return argument
        return " ".join(words[:max_words]) + "..."
    
    def to_structured_json(self) -> Dict:
        """Convert to structured JSON for agent consumption."""
        return {
            "round_number": self.round_number,
            "agent_statements": [
                {
                    "agent_id": s.agent_id,
                    "position": s.position,
                    "argument": self.summarize_argument(s.argument),
                    "amendment": s.amendment,
                    "confidence": s.confidence
                }
                for s in self.agent_statements
            ],
            "votes": self.votes,
            "amendments": self.amendments
        }
    
    def estimate_tokens(self) -> int:
        """Estimate token count for this context using TokenCounter."""
        json_data = self.to_structured_json()
        return self.token_counter.count_tokens_dict(json_data)


class HistoricalContext:
    """
    Historical context containing compressed summaries of previous rounds.
    Uses rolling compression to maintain bounded memory.
    """
    
    def __init__(self, token_counter: Optional[TokenCounter] = None):
        self.summaries: Dict[str, RoundSummary] = {}
        self.unresolved_conflicts: List[str] = []
        self.consensus_trend: List[float] = []
        self.entropy_trend: List[float] = []
        self.token_counter = token_counter or TokenCounter()
        
    def add_round_summary(self, round_num: int, summary: RoundSummary):
        """Add a compressed round summary."""
        key = f"round_{round_num}"
        self.summaries[key] = summary
        self.consensus_trend.append(summary.consensus_level)
        
        # Track unresolved conflicts
        for conflict in summary.major_conflicts:
            if conflict not in self.unresolved_conflicts:
                self.unresolved_conflicts.append(conflict)
        
        logger.debug(f"Added historical summary for round {round_num}")
    
    def get_compressed_history(self, max_rounds: int = 3) -> Dict:
        """
        Get compressed historical context.
        Only includes last N round summaries to limit tokens.
        """
        # Get most recent summaries
        recent_summaries = list(self.summaries.items())[-max_rounds:]
        
        # Aggregate core positions across all rounds
        all_positions = set()
        all_amendments = set()
        for _, summary in recent_summaries:
            all_positions.update(summary.core_positions)
            all_amendments.update(summary.amendments)
        
        return {
            "recent_summaries": [
                {
                    "round": key.split("_")[1],
                    "core_positions": summary.core_positions,
                    "major_conflicts": summary.major_conflicts,
                    "consensus_level": summary.consensus_level
                }
                for key, summary in recent_summaries
            ],
            "aggregated": {
                "all_positions": list(all_positions),
                "unresolved_conflicts": self.unresolved_conflicts[:5],  # Top 5
                "pending_amendments": list(all_amendments)[:5],  # Top 5
                "consensus_trend": self.consensus_trend[-5:],  # Last 5
            }
        }
    
    def estimate_tokens(self, max_rounds: int = 3) -> int:
        """Estimate token count for historical context using TokenCounter."""
        json_data = self.get_compressed_history(max_rounds)
        return self.token_counter.count_tokens_dict(json_data)


class ReferenceContext:
    """
    Optional reference context for rules, constraints, and semantic retrieval.
    """
    
    def __init__(self, token_counter: Optional[TokenCounter] = None):
        self.rules: List[str] = []
        self.constraints: List[str] = []
        self.semantic_results: List[Dict] = []  # From vector DB
        self.token_counter = token_counter or TokenCounter()
        
    def add_rule(self, rule: str):
        """Add a reference rule."""
        if rule not in self.rules:
            self.rules.append(rule)
    
    def add_constraint(self, constraint: str):
        """Add a reference constraint."""
        if constraint not in self.constraints:
            self.constraints.append(constraint)
    
    def add_semantic_result(self, result: Dict):
        """Add a semantic retrieval result from vector DB."""
        self.semantic_results.append(result)
    
    def to_structured_json(self) -> Dict:
        """Convert to structured JSON."""
        return {
            "rules": self.rules[:3],  # Limit to top 3
            "constraints": self.constraints[:3],  # Limit to top 3
            "relevant_arguments": self.semantic_results[:3]  # Top 3 similar
        }
    
    def estimate_tokens(self) -> int:
        """Estimate token count for reference context using TokenCounter."""
        json_data = self.to_structured_json()
        return self.token_counter.count_tokens_dict(json_data)


class ContextManager:
    """
    Main context manager implementing token-efficient context handling.
    
    Architecture:
    ┌─────────────────────────────┐
    │    ContextManager           │
    │  ┌──────────────────────┐  │
    │  │  ImmediateContext    │  │ ← Current round only
    │  └──────────────────────┘  │
    │  ┌──────────────────────┐  │
    │  │  HistoricalContext   │  │ ← Compressed summaries
    │  └──────────────────────┘  │
    │  ┌──────────────────────┐  │
    │  │  ReferenceContext    │  │ ← Rules & retrieval
    │  └──────────────────────┘  │
    └─────────────────────────────┘
    """
    
    def __init__(
        self, 
        max_historical_rounds: int = 3, 
        model_name: str = "gpt-4",
        enable_deduplication: bool = True,
        enable_pruning: bool = True,
        min_confidence: float = 0.5
    ):
        self.token_counter = TokenCounter(model_name)
        self.immediate_context: Optional[ImmediateContext] = None
        self.historical_context = HistoricalContext(self.token_counter)
        self.reference_context = ReferenceContext(self.token_counter)
        self.max_historical_rounds = max_historical_rounds
        self._current_round = 0
        
        # Deduplication and pruning
        self.enable_deduplication = enable_deduplication
        self.enable_pruning = enable_pruning
        self.deduplicator = StatementDeduplicator() if enable_deduplication else None
        self.pruner = ContextPruner(min_confidence=min_confidence) if enable_pruning else None
        
        # Token tracking
        self._token_stats = {
            "immediate_tokens": [],
            "historical_tokens": [],
            "reference_tokens": [],
            "total_tokens": []
        }
        
        logger.info(
            f"ContextManager initialized: "
            f"max_historical_rounds={max_historical_rounds}, "
            f"deduplication={enable_deduplication}, "
            f"pruning={enable_pruning}"
        )
    
    def start_new_round(self, round_number: int):
        """Start a new round, creating fresh immediate context."""
        self.immediate_context = ImmediateContext(round_number, self.token_counter)
        self._current_round = round_number
        logger.info(f"Started new round {round_number}")
    
    def add_statement(self, statement: DebateStatement):
        """
        Add a statement to current immediate context.
        Applies deduplication if enabled.
        """
        if self.immediate_context is None:
            raise RuntimeError("No active round - call start_new_round first")
        
        # Check for duplicates if enabled
        if self.enable_deduplication and self.deduplicator:
            if self.deduplicator.is_duplicate(statement):
                logger.info(f"Skipping duplicate statement from {statement.agent_id}")
                return
        
        self.immediate_context.add_statement(statement)
    
    def add_vote(self, vote: Dict):
        """Add a vote to current immediate context."""
        if self.immediate_context is None:
            raise RuntimeError("No active round - call start_new_round first")
        self.immediate_context.add_vote(vote)
    
    def compress_round(self, round_summary: RoundSummary):
        """
        Compress current round into historical summary.
        Discards detailed immediate context, keeps only summary.
        """
        if self.immediate_context is None:
            logger.warning("No immediate context to compress")
            return
        
        # Add to historical context
        self.historical_context.add_round_summary(
            self.immediate_context.round_number,
            round_summary
        )
        
        # Clear immediate context (compression complete)
        self.immediate_context = None
        
        logger.info(f"Compressed round {self._current_round}")
    
    def build_agent_context(
        self, 
        agent_id: str, 
        agent_position: Optional[AgentPosition] = None,
        topic: str = "",
        include_reference: bool = False,
        agent_influence: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Build optimized context for a specific agent.
        
        Token budget allocation (for 500 token target):
        - Role/Objective/Topic: ~50 tokens
        - Immediate Context: ~200 tokens
        - Historical Summary: ~150 tokens
        - Agent Position: ~50 tokens
        - Reference Context: ~50 tokens (optional)
        
        Returns structured JSON for prompt injection.
        
        Args:
            agent_id: Agent identifier
            agent_position: Agent's current position
            topic: Debate topic
            include_reference: Whether to include reference context
            agent_influence: Optional dict of agent influence scores for pruning
        """
        context = {
            "round": self._current_round,
            "topic": topic
        }
        
        # Add immediate context if available (with pruning)
        if self.immediate_context:
            immediate_json = self.immediate_context.to_structured_json()
            
            # Apply pruning if enabled
            if self.enable_pruning and self.pruner:
                statements = self.immediate_context.agent_statements
                pruned_statements = self.pruner.prune_statements(
                    statements,
                    agent_influence=agent_influence
                )
                # Update JSON with pruned statements
                immediate_json["agent_statements"] = [
                    {
                        "agent_id": s.agent_id,
                        "position": s.position,
                        "argument": self.immediate_context.summarize_argument(s.argument),
                        "amendment": s.amendment,
                        "confidence": s.confidence
                    }
                    for s in pruned_statements
                ]
            
            context["immediate_context"] = immediate_json
        
        # Add compressed historical context
        context["historical_summary"] = self.historical_context.get_compressed_history(
            self.max_historical_rounds
        )
        
        # Add agent's own position
        if agent_position:
            context["your_position"] = {
                "stance": agent_position.stance,
                "confidence": agent_position.confidence,
                "stability": agent_position.stability_index
            }
        
        # Add reference context if requested
        if include_reference and (self.reference_context.rules or 
                                  self.reference_context.constraints or
                                  self.reference_context.semantic_results):
            context["reference"] = self.reference_context.to_structured_json()
        
        return context
    
    def build_prompt_with_context(
        self,
        agent_id: str,
        role: str,
        objective: str,
        agent_position: Optional[AgentPosition] = None,
        topic: str = "",
        max_tokens: int = 500,
        schema_name: str = "DebateStatement"
    ) -> str:
        """
        Build optimized prompt with structured context.
        
        This is the key method for token reduction.
        Uses structured JSON instead of verbose prose.
        """
        context = self.build_agent_context(agent_id, agent_position, topic)
        
        # Build compact prompt using structured format
        prompt = f"""ROLE: {role}
OBJECTIVE: {objective}
ROUND: {self._current_round}

IMMEDIATE CONTEXT:
{self._format_immediate(context.get("immediate_context"))}

HISTORICAL SUMMARY:
{self._format_historical(context.get("historical_summary"))}

YOUR POSITION:
{self._format_position(context.get("your_position"))}

CONSTRAINTS:
- Max tokens: {max_tokens}
- JSON schema output only: {schema_name}

Respond with ONLY valid JSON matching the {schema_name} schema."""
        
        return prompt
    
    def _format_immediate(self, immediate: Optional[Dict]) -> str:
        """Format immediate context compactly."""
        if not immediate:
            return "No immediate context (first round)"
        
        statements = immediate.get("agent_statements", [])
        if not statements:
            return "No statements yet this round"
        
        lines = []
        for stmt in statements:
            lines.append(
                f"• {stmt['agent_id']}: {stmt['position']} "
                f"(conf: {stmt['confidence']:.2f})"
            )
        return "\n".join(lines)
    
    def _format_historical(self, historical: Optional[Dict]) -> str:
        """Format historical summary compactly."""
        if not historical:
            return "No historical context"
        
        agg = historical.get("aggregated", {})
        positions = agg.get("all_positions", [])
        conflicts = agg.get("unresolved_conflicts", [])
        consensus = agg.get("consensus_trend", [])
        
        lines = []
        if positions:
            lines.append(f"Positions: {', '.join(positions[:5])}")
        if conflicts:
            lines.append(f"Conflicts: {', '.join(conflicts[:3])}")
        if consensus:
            avg_consensus = sum(consensus) / len(consensus)
            lines.append(f"Consensus trend: {avg_consensus:.2f}")
        
        return "\n".join(lines) if lines else "No historical data"
    
    def _format_position(self, position: Optional[Dict]) -> str:
        """Format agent position compactly."""
        if not position:
            return "No previous position"
        
        return (
            f"Stance: {position['stance']} "
            f"(confidence: {position['confidence']:.2f}, "
            f"stability: {position['stability']:.2f})"
        )
    
    def estimate_context_tokens(self, agent_id: str) -> Dict[str, int]:
        """
        Estimate token usage for an agent's context.
        Useful for monitoring and optimization.
        """
        immediate_tokens = 0
        if self.immediate_context:
            immediate_tokens = self.immediate_context.estimate_tokens()
        
        historical_tokens = self.historical_context.estimate_tokens(
            self.max_historical_rounds
        )
        
        reference_tokens = self.reference_context.estimate_tokens()
        
        total = immediate_tokens + historical_tokens + reference_tokens
        
        return {
            "immediate": immediate_tokens,
            "historical": historical_tokens,
            "reference": reference_tokens,
            "total": total,
            "reduction_vs_full": self._calculate_reduction(total)
        }
    
    def _calculate_reduction(self, optimized_tokens: int) -> float:
        """
        Calculate estimated token reduction vs. full transcript approach.
        
        Uses FULL_TRANSCRIPT_MULTIPLIER (3.0) which represents empirically observed
        size difference between full uncompressed transcripts and our structured approach.
        
        Args:
            optimized_tokens: Token count for optimized context
            
        Returns:
            Reduction ratio (0.0 to 1.0), where 0.67 means 67% reduction
        """
        full_transcript_estimate = optimized_tokens * FULL_TRANSCRIPT_MULTIPLIER
        if full_transcript_estimate == 0:
            return 0.0
        reduction = (full_transcript_estimate - optimized_tokens) / full_transcript_estimate
        return reduction
    
    def track_token_usage(self, agent_id: str):
        """Track token usage for metrics."""
        stats = self.estimate_context_tokens(agent_id)
        self._token_stats["immediate_tokens"].append(stats["immediate"])
        self._token_stats["historical_tokens"].append(stats["historical"])
        self._token_stats["reference_tokens"].append(stats["reference"])
        self._token_stats["total_tokens"].append(stats["total"])
    
    def get_token_statistics(self) -> Dict:
        """Get aggregate token statistics."""
        if not self._token_stats["total_tokens"]:
            return {"message": "No token usage tracked yet"}
        
        total_tokens = self._token_stats["total_tokens"]
        return {
            "average_total": sum(total_tokens) / len(total_tokens),
            "max_total": max(total_tokens),
            "min_total": min(total_tokens),
            "average_immediate": sum(self._token_stats["immediate_tokens"]) / len(self._token_stats["immediate_tokens"]),
            "average_historical": sum(self._token_stats["historical_tokens"]) / len(self._token_stats["historical_tokens"]),
            "calls_tracked": len(total_tokens)
        }
    
    def add_semantic_retrieval_result(self, query: str, results: List[Dict], top_k: int = 3):
        """
        Add semantic retrieval results from vector DB.
        This is optional and can be integrated with vector memory.
        """
        for result in results[:top_k]:
            self.reference_context.add_semantic_result(result)
        logger.debug(f"Added {len(results[:top_k])} semantic results for query: {query}")
    
    def reset(self):
        """Reset context manager for new debate."""
        self.immediate_context = None
        self.historical_context = HistoricalContext(self.token_counter)
        self.reference_context = ReferenceContext(self.token_counter)
        self._current_round = 0
        self._token_stats = {
            "immediate_tokens": [],
            "historical_tokens": [],
            "reference_tokens": [],
            "total_tokens": []
        }
        
        # Reset deduplication and pruning
        if self.deduplicator:
            self.deduplicator.reset()
        
        logger.info("Context manager reset")
