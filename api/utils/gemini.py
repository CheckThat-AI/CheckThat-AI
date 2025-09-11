import os
from google import genai
from google.genai import types
from typing import Generator, Union, Type, Optional, List
from fastapi import HTTPException
from json import JSONDecodeError
from ..schemas.claims import NormalizedClaim
from ..schemas.feedback import Feedback
from .conversation_manager import conversation_manager
from ..models.requests import ChatMessage

import logging

logger = logging.getLogger(__name__)
    
class GeminiModel:
    """
    This class is used to generate responses from the Gemini API.
    """
    def __init__(self, model: str, api_key: str = None):
        self.model = model
        try:
            if not api_key:
                raise ValueError("Gemini API key is required but not provided")
            
            self.api_key = api_key
            logger.info(f"Initializing Gemini client for model: {model}")
            # Avoid logging API key length to prevent leaking sensitive information
            logger.debug(f"API key present: {bool(api_key)}")
            
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Gemini Client creation error: {str(e)}")
            raise
    
    def generate_streaming_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None) -> Generator[str, None, None]:
        try:
            logger.info(f"Starting Gemini streaming response for model: {self.model}")
            logger.debug(f"API key configured: {bool(self.api_key)}")
            
            # Format messages with conversation history
            if conversation_history:
                system_instruction, contents = conversation_manager.format_for_gemini(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                system_instruction = sys_prompt
                contents = [types.Part.from_text(text=user_prompt)]
            
            logger.info(f"Gemini API call with {len(contents)} content parts")
            
            stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            for chunk in stream:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini API response error: {str(e)}")
            raise
    
    def generate_structured_response(self, sys_prompt: str, user_prompt: str, response_format: Type[Union[NormalizedClaim, Feedback]]) -> Union[NormalizedClaim, Feedback, None]:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[types.Part.from_text(text=user_prompt)],
                config=types.GenerateContentConfig(
                    system_instruction=sys_prompt,
                    response_mime_type='application/json',
                    response_schema=response_format
                )
            )
            parsed_response = response.parsed
            if parsed_response is not None:
                return parsed_response
            else:
                raise TypeError("Gemini Model Error: Generated response is None")
        except JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            raise