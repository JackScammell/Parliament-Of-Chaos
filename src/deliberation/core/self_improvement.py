"""
Self-improving agent framework with meta-learning.
"""

import json
from typing import Dict, List
from pathlib import Path
from datetime import datetime
from ..models.schemas import MetaLearning


class SelfImprovementEngine:
    """
    Meta-learning engine for agent self-improvement.
    """
    
    def __init__(self, learning_path: str = ".parliament-learning"):
        """
        Initialize self-improvement engine.
        
        Args:
            learning_path: Path for learning data storage
        """
        self.learning_path = Path(learning_path)
        self.learning_path.mkdir(parents=True, exist_ok=True)
        self.strategies: Dict[str, MetaLearning] = {}
        self._load_strategies()
    
    def _load_strategies(self):
        """Load existing meta-learning strategies."""
        for strategy_file in self.learning_path.glob("*.json"):
            with open(strategy_file, 'r') as f:
                data = json.load(f)
                strategy = MetaLearning(**data)
                self.strategies[strategy.strategy_id] = strategy
    
    def record_strategy_performance(self, strategy_id: str, 
                                   performance_score: float,
                                   patterns: List[str],
                                   success: bool):
        """
        Record the performance of a debate strategy.
        
        Args:
            strategy_id: Strategy identifier
            performance_score: Performance metric (0-1)
            patterns: Patterns observed
            success: Whether strategy succeeded
        """
        if strategy_id not in self.strategies:
            self.strategies[strategy_id] = MetaLearning(
                strategy_id=strategy_id,
                performance_history=[],
                adaptation_count=0,
                successful_patterns=[],
                failed_patterns=[]
            )
        
        strategy = self.strategies[strategy_id]
        strategy.performance_history.append(performance_score)
        
        if success:
            strategy.successful_patterns.extend(patterns)
        else:
            strategy.failed_patterns.extend(patterns)
        
        # Deduplicate patterns
        strategy.successful_patterns = list(set(strategy.successful_patterns))
        strategy.failed_patterns = list(set(strategy.failed_patterns))
        
        self._save_strategy(strategy)
    
    def suggest_adaptation(self, strategy_id: str) -> Dict:
        """
        Suggest adaptations based on learning history.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Adaptation suggestions
        """
        if strategy_id not in self.strategies:
            return {"recommendation": "No learning history available"}
        
        strategy = self.strategies[strategy_id]
        
        if len(strategy.performance_history) < 3:
            return {"recommendation": "Insufficient data for adaptation"}
        
        # Analyze trend
        recent_performance = strategy.performance_history[-3:]
        avg_performance = sum(recent_performance) / len(recent_performance)
        
        if avg_performance > 0.7:
            recommendation = "Strategy performing well. Continue current approach."
        elif avg_performance > 0.4:
            recommendation = "Mixed results. Consider incorporating successful patterns."
            if strategy.successful_patterns:
                recommendation += f" Focus on: {', '.join(strategy.successful_patterns[:3])}"
        else:
            recommendation = "Strategy underperforming. Major adaptation needed."
            if strategy.failed_patterns:
                recommendation += f" Avoid: {', '.join(strategy.failed_patterns[:3])}"
        
        return {
            "recommendation": recommendation,
            "avg_performance": avg_performance,
            "successful_patterns": strategy.successful_patterns[:5],
            "failed_patterns": strategy.failed_patterns[:5]
        }
    
    def adapt_strategy(self, strategy_id: str):
        """
        Adapt a strategy based on learning.
        
        Args:
            strategy_id: Strategy to adapt
        """
        if strategy_id not in self.strategies:
            return
        
        strategy = self.strategies[strategy_id]
        strategy.adaptation_count += 1
        
        # Clear failed patterns that appeared in successful runs
        strategy.failed_patterns = [
            p for p in strategy.failed_patterns 
            if p not in strategy.successful_patterns
        ]
        
        self._save_strategy(strategy)
    
    def _save_strategy(self, strategy: MetaLearning):
        """
        Save strategy to storage.
        
        Args:
            strategy: Meta-learning strategy
        """
        strategy_file = self.learning_path / f"{strategy.strategy_id}.json"
        with open(strategy_file, 'w') as f:
            json.dump(strategy.model_dump(), f, indent=2)
    
    def get_learning_summary(self) -> Dict:
        """
        Get summary of learning progress.
        
        Returns:
            Learning summary
        """
        total_strategies = len(self.strategies)
        total_adaptations = sum(s.adaptation_count for s in self.strategies.values())
        
        if total_strategies > 0:
            avg_adaptations = total_adaptations / total_strategies
        else:
            avg_adaptations = 0
        
        return {
            "total_strategies": total_strategies,
            "total_adaptations": total_adaptations,
            "average_adaptations_per_strategy": round(avg_adaptations, 2),
            "learning_path": str(self.learning_path)
        }
