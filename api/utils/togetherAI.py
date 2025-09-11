import os
import json
import logging
from together import Together
from typing import Generator, Union, Type, Optional, Any, List
from fastapi import HTTPException
from json import JSONDecodeError
from ..schemas.claims import NormalizedClaim
from ..schemas.feedback import Feedback
from .conversation_manager import conversation_manager
from ..models.requests import ChatMessage
            
logger = logging.getLogger(__name__)

class TogetherModel:
    """
    This class is used to generate responses from the Together API for Llama and Deepseek models.
    """
    def __init__(self, model: str, api_key: str = None):
        self.model = model
        try:
            self.api_key = api_key
            self.client = Together(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Together Client creation error: {str(e)}")
            raise

    def generate_streaming_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None) -> Generator[str, None, None]:
        try:
            # Format messages with conversation history (TogetherAI uses OpenAI format)
            if conversation_history:
                messages = conversation_manager.format_for_openai(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]
            
            logger.info(f"TogetherAI API call with {len(messages)} messages")
            
            stream = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                stream=True
            )
            for chunk in stream:
                if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Together API response error: {str(e)}")
            raise
    
    def generate_structured_response(self, sys_prompt: str, user_prompt: str, response_format: Type[Union[NormalizedClaim, Feedback]]) -> Union[NormalizedClaim, Feedback]:
        try:
            # Get complete response without streaming
            response = self.client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                model=self.model,
                response_format={
                    "type": "json_object",
                    "schema": response_format.model_json_schema(),
                }
            )
            parsed_response = response.choices[0].message.content
            if parsed_response is not None:
                return response_format(**parsed_response)
            else:
                raise TypeError("Together Model Error: Generated response is None")
        except JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            raise