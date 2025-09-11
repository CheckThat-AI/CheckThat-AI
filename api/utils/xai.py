import os
import logging
from openai import OpenAI, NotGiven
from typing import Generator, Union, Type, Optional, List
from fastapi import HTTPException
from json import JSONDecodeError
from ..schemas.claims import NormalizedClaim
from ..schemas.feedback import Feedback
from .conversation_manager import conversation_manager
from ..models.requests import ChatMessage

logger = logging.getLogger(__name__)

class xAIModel:
    """
    This class is used to generate responses from the xAI API.
    """
    
    def __init__(self, model: str, api_key: str = None):
        self.model = model
        try:
            self.api_key = api_key
            self.client = OpenAI(api_key=self.api_key, base_url="https://api.x.ai/v1")
        except Exception as e:
            logger.error(f"xAI Client creation error: {str(e)}")
            raise
        
    def generate_streaming_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None) -> Generator[str, None, None]:
        try:
            # Format messages with conversation history (xAI uses OpenAI format)
            if conversation_history:
                messages = conversation_manager.format_for_openai(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]
            
            logger.info(f"xAI API call with {len(messages)} messages")
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"xAI API response error: {str(e)}")
            raise

    def generate_structured_response(self, sys_prompt: str, user_prompt: str, response_format: Type[Union[NormalizedClaim, Feedback]]) -> Union[NormalizedClaim, Feedback, None]:
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                response_format=response_format
            )
            parsed_response = response.choices[0].message.parsed
            if parsed_response is not None:
                return parsed_response
            else:
                raise TypeError("OpenAI Model Error: Generated response is None")
        except JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")