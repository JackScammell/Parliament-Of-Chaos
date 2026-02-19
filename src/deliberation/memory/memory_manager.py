"""
Memory manager for cross-session learning.
"""

from typing import List, Dict, Optional
from datetime import datetime, timezone
import logging

from .memory_store import MemoryStore
from ..models.schemas import MemoryEntry

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Manages persistent memory and cross-session learning.
    """
    
    def __init__(self, storage_path: str = ".parliament-memory"):
        """
        Initialize memory manager.
        
        Args:
            storage_path: Path for memory storage
        """
        self.store = MemoryStore(storage_path)
        logger.info(f"Memory manager initialized with storage at {storage_path}")
    
    def save_debate(self, session_id: str, topic: str, 
                    outcome: Dict, key_learnings: List[str]) -> str:
        """
        Save a debate session to memory.
        
        Args:
            session_id: Session identifier
            topic: Debate topic
            outcome: Debate outcome dictionary
            key_learnings: List of lessons learned
            
        Returns:
            Entry ID
        """
        entry = MemoryEntry(
            session_id=session_id,
            topic=topic,
            timestamp=datetime.now(timezone.utc).isoformat(),
            outcome=outcome,
            key_learnings=key_learnings,
            patterns=self._extract_patterns(outcome, key_learnings)
        )
        
        entry_id = self.store.store(entry)
        logger.info(f"Saved debate session {session_id} to memory")
        
        return entry_id
    
    def recall_similar_debates(self, topic: str, limit: int = 3) -> List[MemoryEntry]:
        """
        Recall similar past debates.
        
        Args:
            topic: Current debate topic
            limit: Maximum results
            
        Returns:
            List of similar debate memories
        """
        results = self.store.search(topic, limit)
        logger.info(f"Recalled {len(results)} similar debates for topic '{topic}'")
        return results
    
    def get_past_patterns(self, topic: str) -> List[str]:
        """
        Get patterns from past debates on similar topics.
        
        Args:
            topic: Current topic
            
        Returns:
            List of identified patterns
        """
        similar = self.recall_similar_debates(topic, limit=5)
        patterns = []
        
        for entry in similar:
            patterns.extend(entry.patterns)
        
        # Deduplicate
        return list(set(patterns))
    
    def _extract_patterns(self, outcome: Dict, learnings: List[str]) -> List[str]:
        """
        Extract reusable patterns from debate outcome.
        
        Args:
            outcome: Debate outcome
            learnings: Key learnings
            
        Returns:
            List of patterns
        """
        patterns = []
        
        # Pattern: outcome type
        if outcome.get("approved"):
            patterns.append("consensus_achieved")
        else:
            patterns.append("no_consensus")
        
        # Pattern: voting behavior
        votes = outcome.get("votes", {})
        if votes.get("approve", 0) > votes.get("reject", 0) * 2:
            patterns.append("strong_approval")
        elif votes.get("reject", 0) > votes.get("approve", 0) * 2:
            patterns.append("strong_rejection")
        else:
            patterns.append("divided_opinion")
        
        # Pattern: learning-based
        for learning in learnings:
            if "security" in learning.lower():
                patterns.append("security_concern")
            if "performance" in learning.lower():
                patterns.append("performance_concern")
            if "scalability" in learning.lower():
                patterns.append("scalability_concern")
        
        return patterns
    
    def get_memory_context(self, topic: str) -> Dict:
        """
        Get memory context for a new debate.
        
        Args:
            topic: Debate topic
            
        Returns:
            Context dictionary with relevant memories
        """
        similar = self.recall_similar_debates(topic, limit=3)
        patterns = self.get_past_patterns(topic)
        
        return {
            "similar_debates_count": len(similar),
            "past_patterns": patterns,
            "recent_outcomes": [
                {
                    "topic": entry.topic,
                    "approved": entry.outcome.get("approved", False),
                    "timestamp": entry.timestamp
                }
                for entry in similar
            ]
        }
