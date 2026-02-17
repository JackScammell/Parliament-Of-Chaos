"""
Multi-session debate chaining and state persistence.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from ..models.schemas import SessionState


class SessionManager:
    """
    Manage multi-session debate chains.
    """
    
    def __init__(self, session_path: str = ".parliament-sessions"):
        """
        Initialize session manager.
        
        Args:
            session_path: Path for session storage
        """
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[SessionState] = None
    
    def create_session(self, session_id: str, 
                      previous_sessions: Optional[List[str]] = None) -> SessionState:
        """
        Create a new debate session.
        
        Args:
            session_id: New session identifier
            previous_sessions: IDs of previous linked sessions
            
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
            Session summary
        """
        if not self.current_session:
            return {}
        
        return {
            "session_id": self.current_session.session_id,
            "previous_sessions": len(self.current_session.previous_sessions),
            "context_keys": list(self.current_session.carried_forward_context.keys()),
            "unresolved_conflicts": len(self.current_session.unresolved_conflicts),
            "total_sessions": len(self.current_session.session_summaries)
        }
