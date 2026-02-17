"""
Meta-agent observer for convergence detection and debate monitoring.
"""

from typing import List, Dict
import logging
from collections import Counter

from ..models.schemas import MetaAnalysis, DebateStatement, DebateState, RoundSummary
from ..core.model_tier import ModelCaller

logger = logging.getLogger(__name__)


class MetaObserver:
    """
    Monitoring agent that tracks debate health and convergence.
    System halts early if convergence exceeds threshold or novelty drops.
    """
    
    def __init__(self, model_caller: ModelCaller, 
                 convergence_threshold: float = 0.85,
                 novelty_threshold: float = 0.1):
        self.model_caller = model_caller
        self.convergence_threshold = convergence_threshold
        self.novelty_threshold = novelty_threshold
        self._previous_positions: Dict[str, str] = {}
        self._argument_history: List[str] = []
    
    def analyze_round(
        self, 
        statements: List[DebateStatement],
        state: DebateState
    ) -> MetaAnalysis:
        """
        Analyze current round for convergence, novelty, and overlap.
        
        Args:
            statements: Debate statements from current round
            state: Current debate state
            
        Returns:
            MetaAnalysis with recommendations
        """
        novelty = self._calculate_novelty(statements)
        overlap = self._calculate_argument_overlap(statements)
        convergence = self._calculate_convergence_trend(statements, state)
        
        should_terminate = (
            convergence >= self.convergence_threshold or
            novelty <= self.novelty_threshold
        )
        
        analysis = MetaAnalysis(
            novelty_score=novelty,
            argument_overlap=overlap,
            convergence_trend=convergence,
            recommend_terminate=should_terminate
        )
        
        # Update history for next round
        for stmt in statements:
            self._previous_positions[stmt.agent_id] = stmt.position
            self._argument_history.append(stmt.argument.lower())
        
        logger.info(
            f"Meta-analysis: novelty={novelty:.2f}, overlap={overlap:.2f}, "
            f"convergence={convergence:.2f}, terminate={should_terminate}"
        )
        
        return analysis
    
    def _calculate_novelty(self, statements: List[DebateStatement]) -> float:
        """
        Calculate novelty score based on new arguments vs history.
        Returns value between 0 (no novelty) and 1 (all new).
        """
        if not statements:
            return 0.0
        
        if not self._argument_history:
            # First round - all arguments are novel
            return 1.0
        
        # Simple novelty: check how many arguments introduce new terms
        new_arguments = 0
        for stmt in statements:
            argument_lower = stmt.argument.lower()
            # Check if argument contains terms not in history
            words = set(argument_lower.split())
            history_words = set(' '.join(self._argument_history).split())
            
            new_words = words - history_words
            if len(new_words) > 3:  # At least 3 new terms
                new_arguments += 1
        
        novelty = new_arguments / len(statements)
        return novelty
    
    def _calculate_argument_overlap(self, statements: List[DebateStatement]) -> float:
        """
        Calculate degree of redundancy in arguments.
        Returns value between 0 (no overlap) and 1 (complete redundancy).
        """
        if len(statements) < 2:
            return 0.0
        
        # Compare arguments pairwise for similarity
        arguments = [stmt.argument.lower() for stmt in statements]
        total_comparisons = 0
        overlapping_comparisons = 0
        
        for i in range(len(arguments)):
            for j in range(i + 1, len(arguments)):
                total_comparisons += 1
                
                # Simple word overlap check
                words_i = set(arguments[i].split())
                words_j = set(arguments[j].split())
                
                if not words_i or not words_j:
                    continue
                
                overlap_size = len(words_i & words_j)
                min_size = min(len(words_i), len(words_j))
                
                if min_size > 0 and overlap_size / min_size > 0.5:
                    overlapping_comparisons += 1
        
        if total_comparisons == 0:
            return 0.0
        
        return overlapping_comparisons / total_comparisons
    
    def _calculate_convergence_trend(
        self, statements: List[DebateStatement], state: DebateState
    ) -> float:
        """
        Calculate trend toward consensus.
        Returns value between 0 (diverging) and 1 (converging).
        """
        if not statements:
            return 0.0
        
        # Group positions by similarity
        positions = [stmt.position.lower().strip() for stmt in statements]
        position_counts = Counter(positions)
        
        if not position_counts:
            return 0.0
        
        # Convergence is the proportion in the most common position
        most_common_count = position_counts.most_common(1)[0][1]
        convergence = most_common_count / len(statements)
        
        return convergence
    
    def should_continue(self, analysis: MetaAnalysis) -> bool:
        """
        Determine if debate should continue based on analysis.
        
        Args:
            analysis: MetaAnalysis from current round
            
        Returns:
            True if debate should continue, False if it should terminate
        """
        return not analysis.recommend_terminate
    
    def reset(self):
        """Reset observer state for new debate."""
        self._previous_positions.clear()
        self._argument_history.clear()
        logger.info("Meta-observer reset")


class Summariser:
    """
    Generates structured round summaries for rolling memory compression.
    Uses small/fast model tier.
    """
    
    def __init__(self, model_caller: ModelCaller):
        self.model_caller = model_caller
    
    async def generate_summary_async(
        self, 
        statements: List[DebateStatement],
        state: DebateState
    ) -> RoundSummary:
        """
        Generate structured summary of debate round.
        
        Args:
            statements: Statements from the round
            state: Current debate state
            
        Returns:
            RoundSummary with key information
        """
        prompt = self._build_summary_prompt(statements, state)
        
        # Use summariser model tier (small/fast)
        raw_output = await self.model_caller.call_model_async(
            role="summariser",
            prompt=prompt,
            temperature=0.5
        )
        
        # Parse and validate (simplified for now)
        summary = self._parse_summary(raw_output, statements, state)
        
        logger.info(f"Generated summary for round {state.round}")
        return summary
    
    def _build_summary_prompt(
        self, statements: List[DebateStatement], state: DebateState
    ) -> str:
        """Build prompt for generating round summary."""
        statements_text = "\n".join([
            f"- {s.agent_id}: {s.position} | {s.argument[:100]}..."
            for s in statements
        ])
        
        return f"""ROLE: Summariser

OBJECTIVE: Generate structured summary of debate round

CONSTRAINTS:
- Extract core positions (not all details)
- Identify major conflicts
- List proposed amendments
- Assess consensus level (0-1)
- Output strict JSON matching RoundSummary schema

ROUND {state.round} STATEMENTS:
{statements_text}

OUTPUT FORMAT:
{{
  "core_positions": ["position1", "position2"],
  "major_conflicts": ["conflict1", "conflict2"],
  "amendments": ["amendment1"],
  "consensus_level": 0.0-1.0
}}

Respond with ONLY valid JSON matching the schema above."""
    
    def _parse_summary(
        self, raw_output: str, statements: List[DebateStatement], state: DebateState
    ) -> RoundSummary:
        """
        Parse summary output into RoundSummary schema.
        Fallback to basic extraction if parsing fails.
        """
        try:
            import json
            data = json.loads(raw_output)
            return RoundSummary(**data)
        except Exception as e:
            logger.warning(f"Failed to parse summary, using fallback: {str(e)}")
            
            # Fallback: extract basic information
            positions = list(set([s.position for s in statements]))
            amendments = [s.amendment for s in statements if s.amendment]
            
            # Calculate basic consensus
            from collections import Counter
            position_counts = Counter([s.position for s in statements])
            if statements:
                consensus = position_counts.most_common(1)[0][1] / len(statements)
            else:
                consensus = 0.0
            
            return RoundSummary(
                core_positions=positions[:5],  # Top 5
                major_conflicts=[],
                amendments=amendments[:3],  # Top 3
                consensus_level=consensus
            )
