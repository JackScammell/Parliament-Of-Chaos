"""
Vector memory storage interface for Parliament of Chaos.
Provides on-demand retrieval of relevant past arguments using embeddings.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Check if sentence-transformers is available for embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not available - vector memory will use fallback")


class VectorMemoryStore:
    """
    Simple in-memory vector store for debate arguments.
    Supports semantic retrieval of relevant past arguments.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize vector memory store.
        
        Args:
            model_name: Sentence transformer model name for embeddings
        """
        self.model_name = model_name
        self.model = None
        self.entries: List[Dict] = []
        self._entry_counter = 0
        
        if EMBEDDINGS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"VectorMemoryStore initialized with {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
                self.model = None
        else:
            logger.info("VectorMemoryStore initialized in fallback mode (no embeddings)")
    
    def add_entry(
        self, 
        content: str, 
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add an entry to vector memory.
        
        Args:
            content: Text content to store
            metadata: Optional metadata dict (agent_id, round, etc.)
            
        Returns:
            Entry ID
        """
        entry_id = f"entry_{self._entry_counter}"
        self._entry_counter += 1
        
        embedding = None
        if self.model and content:
            try:
                embedding = self.model.encode(content).tolist()
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
        
        entry = {
            "entry_id": entry_id,
            "content": content,
            "metadata": metadata or {},
            "embedding": embedding,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.entries.append(entry)
        logger.debug(f"Added entry {entry_id} to vector memory")
        
        return entry_id
    
    def retrieve_similar(
        self, 
        query: str, 
        top_k: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Retrieve most similar entries to query.
        
        Args:
            query: Query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of similar entries with similarity scores
        """
        if not self.entries:
            return []
        
        if not self.model:
            # Fallback: return most recent entries
            logger.debug("Using fallback retrieval (no embeddings)")
            filtered = self._filter_entries(filter_metadata)
            return filtered[-top_k:] if filtered else []
        
        try:
            query_embedding = self.model.encode(query)
        except Exception as e:
            logger.warning(f"Failed to encode query: {e}")
            return []
        
        # Calculate similarities
        results = []
        for entry in self.entries:
            if entry["embedding"] is None:
                continue
            
            # Apply metadata filters if provided
            if filter_metadata and not self._matches_filter(entry, filter_metadata):
                continue
            
            similarity = self._cosine_similarity(query_embedding, entry["embedding"])
            results.append({
                **entry,
                "similarity": similarity
            })
        
        # Sort by similarity and return top-k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def _filter_entries(self, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """Filter entries by metadata."""
        if not filter_metadata:
            return self.entries
        
        filtered = []
        for entry in self.entries:
            if self._matches_filter(entry, filter_metadata):
                filtered.append(entry)
        
        return filtered
    
    def _matches_filter(self, entry: Dict, filter_metadata: Dict) -> bool:
        """Check if entry matches metadata filter."""
        entry_meta = entry.get("metadata", {})
        for key, value in filter_metadata.items():
            if entry_meta.get(key) != value:
                return False
        return True
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            import numpy as np
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.warning(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def get_statistics(self) -> Dict:
        """Get vector memory statistics."""
        return {
            "total_entries": len(self.entries),
            "model_name": self.model_name,
            "embeddings_enabled": self.model is not None
        }
    
    def clear(self):
        """Clear all entries."""
        self.entries.clear()
        self._entry_counter = 0
        logger.info("Vector memory cleared")
