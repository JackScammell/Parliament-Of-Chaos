"""
Multi-session debate chaining and state persistence.
Enhanced with ContextManager integration for token-efficient cross-session context.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from ..models.schemas import SessionState
from .context_manager import ContextManager


class SessionManager:
    """
    Manage multi-session debate chains.
    Now integrated with ContextManager for token-efficient context handling.
    """
    
    def __init__(self, session_path: str = ".parliament-sessions", 
                 use_context_optimization: bool = True):
        """
        Initialize session manager.
        
        Args:
            session_path: Path for session storage
            use_context_optimization: Enable context optimization for cross-session data
        """
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[SessionState] = None
        self.use_context_optimization = use_context_optimization
        self.context_manager: Optional[ContextManager] = None
    
    def create_session(self, session_id: str, 
                      previous_sessions: Optional[List[str]] = None,
                      context_manager: Optional[ContextManager] = None) -> SessionState:
        """
        Create a new debate session.
        
        Args:
            session_id: New session identifier
            previous_sessions: IDs of previous linked sessions
            context_manager: Optional ContextManager to persist
            
        Returns:
            New session state
        """
        session = SessionState(
            session_id=session_id,
            previous_sessions=previous_sessions or [],
            carried_forward_context={},
            unresolved_conflicts=[],
            session_summaries={}
        )
        
        # Store context manager reference
        if context_manager:
            self.context_manager = context_manager
        
        # Load context from previous sessions
        if previous_sessions:
            for prev_id in previous_sessions:
                prev_session = self.load_session(prev_id)
                if prev_session:
                    session.carried_forward_context.update(
                        prev_session.carried_forward_context
                    )
                    session.unresolved_conflicts.extend(
                        prev_session.unresolved_conflicts
                    )
                    session.session_summaries.update(
                        prev_session.session_summaries
                    )
                    
                    # Load previous context manager state if available
                    if self.use_context_optimization:
                        self._load_context_manager_state(prev_id)
        
        self.current_session = session
        self._save_session(session)
        
        return session
    
    def update_session(self, context: Dict, conflicts: List[str], 
                      summary: str) -> bool:
        """
        Update current session with new data.
        
        Args:
            context: New context to add
            conflicts: Unresolved conflicts
            summary: Session summary
            
        Returns:
            True if updated successfully
        """
        if not self.current_session:
            return False
        
        self.current_session.carried_forward_context.update(context)
        self.current_session.unresolved_conflicts.extend(conflicts)
        self.current_session.session_summaries[
            self.current_session.session_id
        ] = summary
        
        self._save_session(self.current_session)
        return True
    
    def load_session(self, session_id: str) -> Optional[SessionState]:
        """
        Load a session from storage.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session state or None
        """
        session_file = self.session_path / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        return SessionState(**data)
    
    def _save_session(self, session: SessionState):
        """
        Save session to storage.
        
        Args:
            session: Session state to save
        """
        session_file = self.session_path / f"{session.session_id}.json"
        
        with open(session_file, 'w') as f:
            json.dump(session.model_dump(), f, indent=2)
        
        # Save context manager state if available
        if self.use_context_optimization and self.context_manager:
            self._save_context_manager_state(session.session_id)
    
    def _save_context_manager_state(self, session_id: str):
        """
        Save ContextManager state for cross-session persistence.
        
        Args:
            session_id: Session identifier
        """
        if not self.context_manager:
            return
        
        context_file = self.session_path / f"{session_id}_context.json"
        
        # Export relevant context data
        context_data = {
            "historical_summaries": {
                key: summary.model_dump() 
                for key, summary in self.context_manager.historical_context.summaries.items()
            },
            "unresolved_conflicts": self.context_manager.historical_context.unresolved_conflicts,
            "consensus_trend": self.context_manager.historical_context.consensus_trend,
            "entropy_trend": self.context_manager.historical_context.entropy_trend,
            "token_stats": self.context_manager._token_stats,
            "current_round": self.context_manager._current_round
        }
        
        with open(context_file, 'w') as f:
            json.dump(context_data, f, indent=2)
    
    def _load_context_manager_state(self, session_id: str):
        """
        Load ContextManager state from previous session.
        
        Args:
            session_id: Session identifier to load from
        """
        context_file = self.session_path / f"{session_id}_context.json"
        
        if not context_file.exists():
            return
        
        # Create context manager if not exists
        if not self.context_manager:
            self.context_manager = ContextManager()
        
        with open(context_file, 'r') as f:
            context_data = json.load(f)
        
        # Restore historical summaries
        from ..models.schemas import RoundSummary
        for key, summary_data in context_data.get("historical_summaries", {}).items():
            summary = RoundSummary(**summary_data)
            self.context_manager.historical_context.summaries[key] = summary
        
        # Restore other state
        self.context_manager.historical_context.unresolved_conflicts = context_data.get(
            "unresolved_conflicts", []
        )
        self.context_manager.historical_context.consensus_trend = context_data.get(
            "consensus_trend", []
        )
        self.context_manager.historical_context.entropy_trend = context_data.get(
            "entropy_trend", []
        )
        self.context_manager._token_stats = context_data.get(
            "token_stats", 
            {
                "immediate_tokens": [],
                "historical_tokens": [],
                "reference_tokens": [],
                "total_tokens": []
            }
        )
        self.context_manager._current_round = context_data.get("current_round", 0)
    
    def get_session_chain(self, session_id: str) -> List[str]:
        """
        Get complete chain of linked sessions.
        
        Args:
            session_id: Current session ID
            
        Returns:
            List of session IDs in chain
        """
        session = self.load_session(session_id)
        if not session:
            return [session_id]
        
        chain = session.previous_sessions.copy()
        chain.append(session_id)
        
        return chain
    
    def resolve_conflict(self, conflict: str) -> bool:
        """
        Mark a conflict as resolved.
        
        Args:
            conflict: Conflict description
            
        Returns:
            True if resolved
        """
        if not self.current_session:
            return False
        
        if conflict in self.current_session.unresolved_conflicts:
            self.current_session.unresolved_conflicts.remove(conflict)
            self._save_session(self.current_session)
            return True
        
        return False
    
    def get_session_summary(self) -> Dict:
        """
        Get summary of current session.
        
        Returns:
            Session summary with context optimization stats
        """
        if not self.current_session:
            return {}
        
        summary = {
            "session_id": self.current_session.session_id,
            "previous_sessions": len(self.current_session.previous_sessions),
            "context_keys": list(self.current_session.carried_forward_context.keys()),
            "unresolved_conflicts": len(self.current_session.unresolved_conflicts),
            "total_sessions": len(self.current_session.session_summaries)
        }
        
        # Add context optimization stats if available
        if self.use_context_optimization and self.context_manager:
            context_stats = self.context_manager.get_token_statistics()
            summary["context_optimization"] = context_stats
        
        return summary
    
    def get_cross_session_context(self) -> Dict:
        """
        Get aggregated context from all sessions in the chain.
        Uses ContextManager for token-efficient aggregation.
        
        Returns:
            Aggregated cross-session context
        """
        if not self.current_session:
            return {}
        
        # Get session chain
        chain = self.get_session_chain(self.current_session.session_id)
        
        # Aggregate data
        aggregated = {
            "session_count": len(chain),
            "all_conflicts": [],
            "all_summaries": {},
            "context_keys": set()
        }
        
        for session_id in chain:
            session = self.load_session(session_id)
            if session:
                aggregated["all_conflicts"].extend(session.unresolved_conflicts)
                aggregated["all_summaries"].update(session.session_summaries)
                aggregated["context_keys"].update(session.carried_forward_context.keys())
        
        # Deduplicate conflicts
        aggregated["all_conflicts"] = list(set(aggregated["all_conflicts"]))
        aggregated["context_keys"] = list(aggregated["context_keys"])
        
        return aggregated
