import os
import logging
from openai import OpenAI
from openai.types.chat.completion_create_params import ResponseFormat
from typing import Generator, Union, Type, Any, Optional, List, Dict
from fastapi import HTTPException
from json import JSONDecodeError
import json
from ..schemas.claims import NormalizedClaim
from ..schemas.feedback import Feedback
from .conversation_manager import conversation_manager
from ..models.requests import ChatMessage
    
logger = logging.getLogger(__name__)

class OpenAIModel:
    """
    This class is used to generate responses from the OpenAI API.
    """
    def __init__(self, model: str, api_key: str = None):
        self.model = model
        try:
            self.api_key = api_key
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            logger.error(f"OpenAI Client creation error: {str(e)}")
            raise
        
    def generate_streaming_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None) -> Generator[str, None, None]:
        try:
            if conversation_history:
                messages = conversation_manager.format_for_openai(sys_prompt, conversation_history, user_prompt)
            else:
                if sys_prompt:
                    messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]
                else:
                    messages = [{"role": "user", "content": user_prompt}]

            logger.info(f"OpenAI API call with {len(messages)} messages")

            stream = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                stream=True
            )
            for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI API response error: {str(e)}")
            raise

    def generate_structured_response(self, sys_prompt: str, user_prompt: str, response_format: ResponseFormat = None, conversation_history: Optional[List[ChatMessage]] = None) -> Any:
        try:
            if conversation_history:
                messages = conversation_manager.format_for_openai(sys_prompt, conversation_history, user_prompt)
            else:
                if sys_prompt:
                    messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]
                else:
                    messages = [{"role": "user", "content": user_prompt}]

            response = self.client.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=response_format
            )
            parsed_response = response.choices[0].message.parsed
            if parsed_response is not None:
                return parsed_response
            else:
                raise TypeError("OpenAI Error: Model failed to generate structured response")              
        except JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing structured response: {str(e)}")
            raise