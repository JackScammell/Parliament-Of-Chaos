"""
Memory storage backend for debate history.
Supports semantic search and pattern matching.
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from ..models.schemas import MemoryEntry


class MemoryStore:
    """
    Storage backend for persistent memory.
    Uses JSON files with optional vector search support.
    """
    
    def __init__(self, storage_path: str = ".parliament-memory"):
        """
        Initialize memory store.
        
        Args:
            storage_path: Directory for memory storage
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_path = self.storage_path / "index.json"
        self._load_index()
    
    def _load_index(self):
        """Load memory index."""
        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {"entries": [], "version": "1.0"}
    
    def _save_index(self):
        """Save memory index."""
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def store(self, entry: MemoryEntry) -> str:
        """
        Store a memory entry.
        
        Args:
            entry: Memory entry to store
            
        Returns:
            Entry ID
        """
        entry_id = entry.session_id
        entry_path = self.storage_path / f"{entry_id}.json"
        
        # Save entry
        with open(entry_path, 'w') as f:
            json.dump(entry.model_dump(), f, indent=2)
        
        # Update index
        self.index["entries"].append({
            "id": entry_id,
            "topic": entry.topic,
            "timestamp": entry.timestamp,
            "path": str(entry_path)
        })
        self._save_index()
        
        return entry_id
    
    def retrieve(self, session_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a memory entry by session ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Memory entry or None
        """
        entry_path = self.storage_path / f"{session_id}.json"
        
        if not entry_path.exists():
            return None
        
        with open(entry_path, 'r') as f:
            data = json.load(f)
        
        return MemoryEntry(**data)
    
    def search(self, topic: str, limit: int = 5) -> List[MemoryEntry]:
        """
        Search for related memory entries by topic.
        
        Args:
            topic: Topic to search for
            limit: Maximum results to return
            
        Returns:
            List of matching memory entries
        """
        results = []
        topic_lower = topic.lower()
        
        for entry_info in self.index["entries"]:
            if topic_lower in entry_info["topic"].lower():
                entry = self.retrieve(entry_info["id"])
                if entry:
                    results.append(entry)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def list_recent(self, limit: int = 10) -> List[MemoryEntry]:
        """
        List recent memory entries.
        
        Args:
            limit: Maximum results to return
            
        Returns:
            List of recent entries
        """
        recent_entries = sorted(
            self.index["entries"],
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]
        
        return [
            self.retrieve(entry["id"])
            for entry in recent_entries
            if self.retrieve(entry["id"]) is not None
        ]
    
    def get_statistics(self) -> Dict:
        """
        Get memory storage statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "total_entries": len(self.index["entries"]),
            "storage_path": str(self.storage_path),
            "index_version": self.index.get("version", "unknown")
        }
