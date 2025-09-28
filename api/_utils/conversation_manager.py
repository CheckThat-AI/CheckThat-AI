"""
Conversation History Management for Multi-Turn Chat

Handles conversation retrieval, token counting, and API-specific formatting
for OpenAI, Anthropic, and Gemini APIs.
"""

import os
import logging
import tiktoken
from typing import List, Dict, Any, Optional, Tuple
from supabase import create_client, Client


logger = logging.getLogger(__name__)

# Supabase client for conversation retrieval
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY) if SUPABASE_URL and SUPABASE_SERVICE_KEY else None

ChatMessage = {
    "role": str,
    "content": str,
    "timestamp": Optional[str]
}

class ConversationManager:
    """Manages conversation history for multi-turn chat"""
    
    def __init__(self):
        # Token counting for different models
        self.encoders = {
            'gpt-4': 'cl100k_base',
            'gpt-3.5': 'cl100k_base', 
            'claude': 'cl100k_base',  # Approximation for Claude
            'gemini': 'cl100k_base'   # Approximation for Gemini
        }
    
    async def get_conversation_history(self, conversation_id: str, max_tokens: int = 4000) -> List[ChatMessage]:
        """
        Retrieve conversation history from Supabase with token-based pruning
        
        Args:
            conversation_id: The conversation ID to retrieve
            max_tokens: Maximum tokens to include in history
            
        Returns:
            List of ChatMessage objects, pruned to fit token limit
        """
        if not supabase or not conversation_id:
            return []
            
        try:
            # Fetch conversation from Supabase
            result = supabase.table('conversations').select('messages').eq('id', conversation_id).execute()
            
            if not result.data:
                logger.warning(f"No conversation found with id: {conversation_id}")
                return []
            
            messages_data = result.data[0]['messages']
            if not messages_data:
                return []
            
            # Convert to ChatMessage objects (excluding system messages from storage)
            history = []
            for msg in messages_data:
                if msg.get('role') in ['user', 'assistant']:
                    history.append(ChatMessage(
                        role=msg['role'],
                        content=msg['content'],
                        timestamp=msg.get('timestamp')
                    ))
            
            # Prune to fit token limit (keep most recent messages)
            pruned_history = self._prune_by_tokens(history, max_tokens)
            
            logger.info(f"Retrieved {len(pruned_history)} messages from conversation {conversation_id}")
            return pruned_history
            
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []
    
    def _prune_by_tokens(self, messages: List[ChatMessage], max_tokens: int) -> List[ChatMessage]:
        """
        Prune conversation history to fit within token limit
        Keeps the most recent messages that fit within the limit
        """
        if not messages:
            return []
        
        # Estimate tokens for each message
        total_tokens = 0
        pruned_messages = []
        
        # Start from the end (most recent) and work backwards
        for message in reversed(messages):
            message_tokens = self._estimate_tokens(message.content)
            
            if total_tokens + message_tokens > max_tokens:
                # If this message would exceed limit, stop here
                break
                
            total_tokens += message_tokens
            pruned_messages.insert(0, message)  # Insert at beginning to maintain order
        
        if len(pruned_messages) < len(messages):
            logger.info(f"Pruned conversation from {len(messages)} to {len(pruned_messages)} messages to fit {max_tokens} token limit")
        
        return pruned_messages
    
    def _estimate_tokens(self, text: str, model_type: str = 'gpt-4') -> int:
        """
        Estimate token count for text using tiktoken
        """
        try:
            encoding_name = self.encoders.get(model_type, 'cl100k_base')
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Error counting tokens: {str(e)}, using character-based estimation")
            # Fallback: rough estimation of 4 characters per token
            return len(text) // 4
    
    def format_for_openai(self, system_prompt: str, conversation_history: List[ChatMessage], current_query: str) -> List[Dict[str, str]]:
        """
        Format conversation history for OpenAI ChatCompletion API
        
        Returns:
            List of message dictionaries in OpenAI format
        """
        messages = []
        
        # Add system message first
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user query
        messages.append({"role": "user", "content": current_query})
        
        return messages
    
    def format_for_anthropic(self, system_prompt: str, conversation_history: List[ChatMessage], current_query: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Format conversation history for Anthropic Claude API
        
        Returns:
            Tuple of (system_prompt, messages_array)
        """
        messages = []
        
        # Add conversation history (no system messages in messages array for Anthropic)
        for msg in conversation_history:
            if msg.role != 'system':  # System messages handled separately
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Add current user query
        messages.append({"role": "user", "content": current_query})
        
        return system_prompt, messages
    
    def format_for_gemini(self, system_prompt: str, conversation_history: List[ChatMessage], current_query: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Format conversation history for Google Gemini API
        
        Returns:
            Tuple of (system_instruction, contents_array)
        """
        contents = []
        
        # Add conversation history
        for msg in conversation_history:
            if msg.role == 'user':
                role = 'user'
            elif msg.role == 'assistant':
                role = 'model'
            else:
                continue  # Skip system messages (handled as system_instruction)
            
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
        
        # Add current user query
        contents.append({
            "role": "user", 
            "parts": [{"text": current_query}]
        })
        
        return system_prompt, contents

# Global instance
conversation_manager = ConversationManager()
