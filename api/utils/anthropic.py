import os
import json
import logging
import instructor
import anthropic
from typing import Generator, Union, Type, Optional, List
from fastapi import HTTPException
from json import JSONDecodeError
from .schema import NormalizedClaim, Feedback
from .conversation_manager import conversation_manager
from ..models.requests import ChatMessage

logger = logging.getLogger(__name__)

class AnthropicModel:
    """
    This class is used to generate responses from the Anthropic API.
    """
    def __init__(self, model: str, api_key: Optional[str] = None):
        self.model = model
        try:
            self.api_key = api_key if not None else os.getenv("ANTHROPIC_API_KEY")
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
            raise HTTPException(
                status_code=500,
                detail=f"Error during streaming: {str(e)}"
            )

    def generate_structured_response(self, sys_prompt: str, user_prompt: str, response_format: Type[Union[NormalizedClaim, Feedback]]) -> Union[NormalizedClaim, Feedback]:
        try:
            client = instructor.from_anthropic(anthropic.Anthropic(api_key=self.api_key))
        except Exception as e:
            logger.error(f"Anthropic Instructor creation error: {str(e)}")
            raise
    
        try:
            response = client.chat.completions.create(
                max_tokens=8192,
                model=self.model,
                system=sys_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                response_model=response_format,
                max_retries=2,
            )
            return response
        except JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse JSON response: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing response: {str(e)}"
            )
