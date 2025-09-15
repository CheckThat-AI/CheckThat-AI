import os
import json
import logging
import instructor
import anthropic
from typing import Generator, Union, Type, Optional, List, Dict, Any
from fastapi import HTTPException
from json import JSONDecodeError
from ..schemas.claims import NormalizedClaim
from ..schemas.feedback import Feedback
from .conversation_manager import conversation_manager
from ..models.requests import ChatMessage

logger = logging.getLogger(__name__)

class AnthropicModel:
    """
    This class is used to generate responses from the Anthropic API.
    """
    def __init__(self, model: str, api_key: str = None):
        self.model = model
        try:
            self.api_key = api_key
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Anthropic Client creation error: {str(e)}")
            raise
    
    def generate_streaming_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None) -> Generator[str, None, None]:
        try:
            # Format messages with conversation history
            if conversation_history:
                system_instruction, messages = conversation_manager.format_for_anthropic(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                system_instruction = sys_prompt
                messages = [{"role": "user", "content": user_prompt}]
            
            logger.info(f"Anthropic API call with {len(messages)} messages")
            
            with self.client.messages.stream(
                max_tokens=8192,
                model=self.model,
                system=system_instruction,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic API response error: {str(e)}")
            raise

    def generate_structured_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None, response_format: Optional[Union[Type[Union[NormalizedClaim, Feedback]], Dict[str, Any]]] = None) -> Any:
        """
        Anthropic structured outputs support - currently limited to Pydantic models via instructor.
        Note: This provider doesn't fully support the new response_format dict structure yet.
        """
        # For now, only support Pydantic model formats (not JSON schema)
        if isinstance(response_format, dict):
            raise HTTPException(
                status_code=400, 
                detail="Anthropic provider currently only supports Pydantic model response formats, not JSON schema"
            )
        
        try:
            client = instructor.from_anthropic(anthropic.Anthropic(api_key=self.api_key))
        except Exception as e:
            logger.error(f"Anthropic Instructor creation error: {str(e)}")
            raise
    
        try:
            # Format messages with conversation history
            if conversation_history:
                messages = conversation_manager.format_for_anthropic(sys_prompt, conversation_history, user_prompt)
                # Extract system message from messages format
                system_msg = ""
                user_messages = []
                for msg in messages:
                    if msg.get("role") == "system":
                        system_msg = msg.get("content", "")
                    else:
                        user_messages.append(msg)
            else:
                system_msg = sys_prompt
                user_messages = [{"role": "user", "content": user_prompt}]
            
            response = client.chat.completions.create(
                max_tokens=8192,
                model=self.model,
                system=system_msg,
                messages=user_messages,
                response_model=response_format,
                max_retries=2,
            )
            return response
        except JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing structured response: {str(e)}")
            raise
