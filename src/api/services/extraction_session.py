"""
Extraction session management for storing extracted claims and reference data.

This service manages the storage of extraction results so that metrics can be
calculated without resending the text data.
"""

import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from threading import Lock

logger = logging.getLogger(__name__)

@dataclass
class ExtractionData:
    """Container for extraction data"""
    session_id: str
    extracted_claims: List[str]
    reference_claims: List[str]
    model_combinations: List[str]  # Model + prompt style combinations
    metadata: Dict[str, Any]
    created_at: float
    last_accessed: float

class ExtractionSessionManager:
    """
    Manages extraction sessions and stores claim data for metric calculations.
    
    This allows metric calculations to reference stored data by session ID
    instead of resending the extracted and reference claims.
    """
    
    def __init__(self, max_sessions: int = 1000, session_ttl: int = 3600):
        """
        Initialize the session manager.
        
        Args:
            max_sessions: Maximum number of sessions to store
            session_ttl: Session time-to-live in seconds
        """
        self._sessions: Dict[str, ExtractionData] = {}
        self._lock = Lock()
        self.max_sessions = max_sessions
        self.session_ttl = session_ttl
        logger.info(f"ExtractionSessionManager initialized (max_sessions={max_sessions}, ttl={session_ttl}s)")
    
    def store_extraction_data(
        self,
        session_id: str,
        extracted_claims: List[str],
        reference_claims: List[str],
        model_combinations: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store extraction data for a session.
        
        Args:
            session_id: Unique session identifier
            extracted_claims: Claims extracted by the models
            reference_claims: Ground truth claims from dataset
            model_combinations: List of model+prompt combinations used
            metadata: Additional metadata about the extraction
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            with self._lock:
                # Clean up old sessions before storing
                self._cleanup_expired_sessions()
                
                # If we're at capacity, remove oldest session
                if len(self._sessions) >= self.max_sessions:
                    self._remove_oldest_session()
                
                current_time = time.time()
                extraction_data = ExtractionData(
                    session_id=session_id,
                    extracted_claims=extracted_claims,
                    reference_claims=reference_claims,
                    model_combinations=model_combinations or [],
                    metadata=metadata or {},
                    created_at=current_time,
                    last_accessed=current_time
                )
                
                self._sessions[session_id] = extraction_data
                
                logger.info(f"Stored extraction data for session {session_id}: "
                          f"{len(extracted_claims)} extracted claims, {len(reference_claims)} reference claims")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store extraction data for session {session_id}: {str(e)}")
            return False
    
    def get_extraction_data(self, session_id: str) -> Optional[ExtractionData]:
        """
        Retrieve extraction data for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ExtractionData if found, None otherwise
        """
        try:
            with self._lock:
                if session_id in self._sessions:
                    ext_data = self._sessions[session_id]
                    ext_data.last_accessed = time.time()  # Update access time
                    return ext_data
                else:
                    logger.warning(f"Session {session_id} not found")
                    return None
        except Exception as e:
            logger.error(f"Failed to retrieve extraction data for session {session_id}: {str(e)}")
            return None
    
    def get_claims_for_metrics(self, session_id: str) -> Optional[tuple[List[str], List[str]]]:
        """
        Get extracted and reference claims for metric calculation.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Tuple of (extracted_claims, reference_claims) if found, None otherwise
        """
        ext_data = self.get_extraction_data(session_id)
        if ext_data:
            return ext_data.extracted_claims, ext_data.reference_claims
        return None
    
    def update_session_metadata(self, session_id: str, metadata_update: Dict[str, Any]) -> bool:
        """
        Update metadata for a session.
        
        Args:
            session_id: Session identifier
            metadata_update: Metadata fields to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            with self._lock:
                if session_id in self._sessions:
                    self._sessions[session_id].metadata.update(metadata_update)
                    self._sessions[session_id].last_accessed = time.time()
                    return True
                else:
                    logger.warning(f"Cannot update metadata: session {session_id} not found")
                    return False
        except Exception as e:
            logger.error(f"Failed to update metadata for session {session_id}: {str(e)}")
            return False
    
    def remove_session(self, session_id: str) -> bool:
        """
        Remove a session from storage.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if removed successfully, False if not found
        """
        try:
            with self._lock:
                if session_id in self._sessions:
                    del self._sessions[session_id]
                    logger.info(f"Removed session {session_id}")
                    return True
                else:
                    logger.warning(f"Cannot remove: session {session_id} not found")
                    return False
        except Exception as e:
            logger.error(f"Failed to remove session {session_id}: {str(e)}")
            return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active sessions with basic info.
        
        Returns:
            List of session information dictionaries
        """
        try:
            with self._lock:
                session_list = []
                for session_id, ext_data in self._sessions.items():
                    session_info = {
                        "session_id": session_id,
                        "extracted_claims_count": len(ext_data.extracted_claims),
                        "reference_claims_count": len(ext_data.reference_claims),
                        "model_combinations": ext_data.model_combinations,
                        "created_at": ext_data.created_at,
                        "last_accessed": ext_data.last_accessed,
                        "age_seconds": time.time() - ext_data.created_at
                    }
                    session_list.append(session_info)
                return session_list
        except Exception as e:
            logger.error(f"Failed to list sessions: {str(e)}")
            return []
    
    def _cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (called with lock held)"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, ext_data in self._sessions.items():
            if current_time - ext_data.last_accessed > self.session_ttl:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def _remove_oldest_session(self) -> None:
        """Remove the oldest session to make room (called with lock held)"""
        if not self._sessions:
            return
        
        oldest_session = min(self._sessions.items(), key=lambda x: x[1].created_at)
        session_id = oldest_session[0]
        del self._sessions[session_id]
        logger.info(f"Removed oldest session {session_id} to make room")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored sessions.
        
        Returns:
            Dictionary with session statistics
        """
        try:
            with self._lock:
                if not self._sessions:
                    return {
                        "total_sessions": 0,
                        "max_sessions": self.max_sessions,
                        "session_ttl": self.session_ttl,
                        "current_sessions": []
                    }
                
                current_time = time.time()
                total_sessions = len(self._sessions)
                current_sessions_info = [
                    {"session_id": sid, "age": time.time() - data.created_at}
                    for sid, data in self._sessions.items()
                ]
                
                return {
                    "total_sessions": total_sessions,
                    "max_sessions": self.max_sessions,
                    "session_ttl": self.session_ttl,
                    "current_sessions": current_sessions_info
                }
        except Exception as e:
            logger.error(f"Failed to get session stats: {str(e)}")
            return {"error": str(e)}

# Global session manager instance
extraction_session_manager = ExtractionSessionManager() 