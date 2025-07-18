"""
DeepEval Session Manager

Handles session-based authentication and cleanup for DeepEval operations.
Manages CONFIDENT_API_KEY storage and .deepeval file cleanup to prevent
persistent authentication from interfering with local evaluations.
"""

import os
import logging
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class DeepEvalSessionManager:
    """
    Manages DeepEval authentication state per session to prevent cross-contamination
    between local and cloud evaluations. Also stores all API keys for the session.
    """
    
    def __init__(self):
        """Initialize the session manager."""
        self._session_api_keys: Dict[str, Optional[str]] = {}  # DeepEval API keys
        self._session_model_api_keys: Dict[str, Dict[str, Optional[str]]] = {}  # Model API keys per session
        self._session_file_hashes: Dict[str, str] = {}  # Track file hashes per session
        self._session_dataset_info: Dict[str, Dict[str, Any]] = {}  # Track dataset info per session
        self._deepeval_auth_file = os.path.join(os.getcwd(), ".deepeval", ".deepeval")
    
    def set_session_api_key(self, session_id: str, confident_api_key: Optional[str]) -> None:
        """
        Store the Confident AI API key for a session.
        
        Args:
            session_id: Unique session identifier
            confident_api_key: Confident AI API key (None for local evaluations)
        """
        self._session_api_keys[session_id] = confident_api_key
        logger.info(f"Set DeepEval API key for session {session_id}: {'cloud' if confident_api_key else 'local'}")
    
    def get_session_api_key(self, session_id: str) -> Optional[str]:
        """
        Get the stored Confident AI API key for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Confident AI API key or None
        """
        return self._session_api_keys.get(session_id)
    
    def set_session_model_api_keys(self, session_id: str, openai_api_key: Optional[str] = None,
                                  anthropic_api_key: Optional[str] = None, gemini_api_key: Optional[str] = None,
                                  grok_api_key: Optional[str] = None) -> None:
        """
        Store model API keys for a session.
        
        Args:
            session_id: Unique session identifier
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
            gemini_api_key: Gemini API key  
            grok_api_key: Grok API key
        """
        if session_id not in self._session_model_api_keys:
            self._session_model_api_keys[session_id] = {}
        
        if openai_api_key is not None:
            self._session_model_api_keys[session_id]['openai'] = openai_api_key
        if anthropic_api_key is not None:
            self._session_model_api_keys[session_id]['anthropic'] = anthropic_api_key
        if gemini_api_key is not None:
            self._session_model_api_keys[session_id]['gemini'] = gemini_api_key
        if grok_api_key is not None:
            self._session_model_api_keys[session_id]['grok'] = grok_api_key
            
        logger.info(f"Updated model API keys for session {session_id}")
    
    def get_session_model_api_keys(self, session_id: str) -> Dict[str, Optional[str]]:
        """
        Get all stored model API keys for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dictionary with keys: openai, anthropic, gemini, grok
        """
        session_keys = self._session_model_api_keys.get(session_id, {})
        return {
            'openai': session_keys.get('openai'),
            'anthropic': session_keys.get('anthropic'),
            'gemini': session_keys.get('gemini'),
            'grok': session_keys.get('grok')
        }
    
    def get_session_model_api_key(self, session_id: str, provider: str) -> Optional[str]:
        """
        Get a specific model API key for a session.
        
        Args:
            session_id: Unique session identifier
            provider: Provider name (openai, anthropic, gemini, grok)
            
        Returns:
            API key or None if not found
        """
        session_keys = self._session_model_api_keys.get(session_id, {})
        return session_keys.get(provider.lower())
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear all stored data for a session.
        
        Args:
            session_id: Unique session identifier
        """
        if session_id in self._session_api_keys:
            del self._session_api_keys[session_id]
        if session_id in self._session_model_api_keys:
            del self._session_model_api_keys[session_id]
        if session_id in self._session_file_hashes:
            del self._session_file_hashes[session_id]
        if session_id in self._session_dataset_info:
            del self._session_dataset_info[session_id]
        logger.info(f"Cleared all data for session {session_id}")
    
    def prepare_for_evaluation(self, session_id: str, is_cloud_evaluation: bool) -> bool:
        """
        Prepare the environment for evaluation based on the type (local/cloud).
        
        Args:
            session_id: Unique session identifier
            is_cloud_evaluation: True for cloud evaluation, False for local
            
        Returns:
            True if preparation was successful, False otherwise
        """
        if is_cloud_evaluation:
            # For cloud evaluation, ensure we have the API key and authenticate
            api_key = self.get_session_api_key(session_id)
            if not api_key:
                logger.error(f"No API key found for cloud evaluation in session {session_id}")
                return False
            
            # Set environment variable for DeepEval
            os.environ['CONFIDENT_API_KEY'] = api_key
            logger.info(f"Prepared cloud evaluation for session {session_id}")
            return True
        else:
            # For local evaluation, clear any existing authentication
            self._clear_deepeval_auth()
            
            # Clear environment variable
            if 'CONFIDENT_API_KEY' in os.environ:
                del os.environ['CONFIDENT_API_KEY']
            
            logger.info(f"Prepared local evaluation for session {session_id}")
            return True
    
    def _clear_deepeval_auth(self) -> None:
        """
        Clear the DeepEval authentication file to force logout.
        This prevents persistent authentication from affecting local evaluations.
        """
        try:
            if os.path.exists(self._deepeval_auth_file):
                os.remove(self._deepeval_auth_file)
                logger.info("Cleared DeepEval authentication file")
            
            # Also clear the cache file which might contain auth data
            cache_file = os.path.join(os.path.dirname(self._deepeval_auth_file), ".deepeval-cache.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
                logger.info("Cleared DeepEval cache file")
                
        except Exception as e:
            logger.warning(f"Failed to clear DeepEval authentication files: {str(e)}")
    
    def is_session_authenticated(self, session_id: str) -> bool:
        """
        Check if a session has cloud authentication configured.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if session has cloud API key, False otherwise
        """
        api_key = self.get_session_api_key(session_id)
        return api_key is not None and api_key.strip() != ""
    
    def get_all_sessions(self) -> Dict[str, bool]:
        """
        Get all active sessions and their authentication status.
        
        Returns:
            Dictionary mapping session_id to authentication status
        """
        return {
            session_id: (api_key is not None and api_key.strip() != "")
            for session_id, api_key in self._session_api_keys.items()
        }
    
    def cleanup_old_sessions(self, active_session_ids: list[str]) -> None:
        """
        Clean up data for sessions that are no longer active.
        
        Args:
            active_session_ids: List of currently active session IDs
        """
        sessions_to_remove = [
            session_id for session_id in self._session_api_keys.keys()
            if session_id not in active_session_ids
        ]
        
        # Also check model API keys for sessions to remove
        model_sessions_to_remove = [
            session_id for session_id in self._session_model_api_keys.keys()
            if session_id not in active_session_ids
        ]
        
        # Combine both lists
        all_sessions_to_remove = list(set(sessions_to_remove + model_sessions_to_remove))
        
        for session_id in all_sessions_to_remove:
            if session_id in self._session_api_keys:
                del self._session_api_keys[session_id]
            if session_id in self._session_model_api_keys:
                del self._session_model_api_keys[session_id]
            if session_id in self._session_file_hashes:
                del self._session_file_hashes[session_id]
            if session_id in self._session_dataset_info:
                del self._session_dataset_info[session_id]
            logger.info(f"Cleaned up inactive session: {session_id}")
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """
        Calculate SHA256 hash of file content.
        
        Args:
            file_content: File content as bytes
            
        Returns:
            SHA256 hash as hex string
        """
        return hashlib.sha256(file_content).hexdigest()
    
    def set_session_file_hash(self, session_id: str, file_hash: str) -> None:
        """
        Store the file hash for a session.
        
        Args:
            session_id: Unique session identifier
            file_hash: SHA256 hash of the file content
        """
        self._session_file_hashes[session_id] = file_hash
        logger.info(f"Set file hash for session {session_id}: {file_hash[:12]}...")
    
    def get_session_file_hash(self, session_id: str) -> Optional[str]:
        """
        Get the stored file hash for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            File hash or None if not found
        """
        return self._session_file_hashes.get(session_id)
    
    def has_file_changed(self, session_id: str, new_file_hash: str) -> bool:
        """
        Check if the file has changed for a session.
        
        Args:
            session_id: Unique session identifier
            new_file_hash: Hash of the new file content
            
        Returns:
            True if file has changed or no previous hash exists, False otherwise
        """
        previous_hash = self.get_session_file_hash(session_id)
        if previous_hash is None:
            return True  # No previous file, consider as changed
        return previous_hash != new_file_hash
    
    def set_session_dataset_info(self, session_id: str, dataset_alias: str, 
                                dataset_location: str, test_case_count: int) -> None:
        """
        Store dataset information for a session.
        
        Args:
            session_id: Unique session identifier
            dataset_alias: Dataset alias used
            dataset_location: Where the dataset was saved
            test_case_count: Number of test cases in the dataset
        """
        self._session_dataset_info[session_id] = {
            'alias': dataset_alias,
            'location': dataset_location,
            'test_case_count': test_case_count,
            'created_at': __import__('datetime').datetime.now().isoformat()
        }
        logger.info(f"Stored dataset info for session {session_id}: {dataset_alias}")
    
    def get_session_dataset_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get stored dataset information for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dataset info dictionary or None if not found
        """
        return self._session_dataset_info.get(session_id)
    
    def should_recreate_dataset(self, session_id: str, new_file_hash: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Determine if dataset should be recreated based on file changes.
        
        Args:
            session_id: Unique session identifier
            new_file_hash: Hash of the new file content
            
        Returns:
            Tuple of (should_recreate, existing_dataset_info)
        """
        existing_info = self.get_session_dataset_info(session_id)
        file_changed = self.has_file_changed(session_id, new_file_hash)
        
        if existing_info is None:
            # No existing dataset info, need to create
            return True, None
        
        if file_changed:
            # File has changed, need to recreate
            logger.info(f"File changed for session {session_id}, will recreate dataset")
            return True, existing_info
        
        # Check if dataset files still exist on disk (for local datasets)
        if existing_info and not existing_info.get('location', '').startswith('cloud:'):
            dataset_location = existing_info.get('location', '')
            if dataset_location and not self._check_local_dataset_exists(dataset_location, session_id):
                logger.info(f"Local dataset files missing for session {session_id}, will recreate")
                return True, existing_info
        
        # File hasn't changed and dataset exists, can reuse
        logger.info(f"File unchanged for session {session_id}, reusing existing dataset")
        return False, existing_info
    
    def _check_local_dataset_exists(self, dataset_location: str, session_id: str) -> bool:
        """
        Check if local dataset files exist.
        
        Args:
            dataset_location: Local directory path
            session_id: Session identifier
            
        Returns:
            True if dataset files exist, False otherwise
        """
        try:
            import glob
            
            # Look for CSV files that might contain the session data
            search_patterns = [
                os.path.join(dataset_location, "*.csv"),
                os.path.join(dataset_location, f"*{session_id}*.csv"),
                f"./data/inference_results_{session_id}.csv",
                "./data/inference_results.csv"
            ]
            
            for pattern in search_patterns:
                if glob.glob(pattern):
                    logger.debug(f"Found dataset files matching pattern: {pattern}")
                    return True
            
            logger.debug(f"No dataset files found for session {session_id}")
            return False
            
        except Exception as e:
            logger.warning(f"Error checking local dataset existence: {str(e)}")
            return False  # Assume doesn't exist if we can't check

# Global instance
deepeval_session_manager = DeepEvalSessionManager() 