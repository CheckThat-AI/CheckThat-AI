import os
import logging
from openai import OpenAI, NotGiven
from typing import Generator, Union, Type, Optional, List, Dict, Any
from fastapi import HTTPException
from json import JSONDecodeError
import json
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

    def generate_structured_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None, response_format: Optional[Union[Type[Union[NormalizedClaim, Feedback]], Dict[str, Any]]] = None) -> Any:
        try:
            # Format messages with conversation history
            if conversation_history:
                messages = conversation_manager.format_for_openai(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                if sys_prompt:
                    messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]
                else:
                    messages = [{"role": "user", "content": user_prompt}]

            # Determine the response format
            if isinstance(response_format, dict):
                # Handle response_format as dict (from API request)
                if response_format.get("type") == "json_schema" and "json_schema" in response_format:
                    # Use the new client.chat.completions.create method with response_format
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        response_format=response_format
                    )
                    # Extract the content and try to parse it as JSON
                    content = response.choices[0].message.content
                    try:
                        parsed_data = json.loads(content) if content else None
                        # Return an object with both content and parsed data
                        class StructuredResponse:
                            def __init__(self, content: str, parsed: Any):
                                self.content = content
                                self.parsed = parsed
                        return StructuredResponse(content=content, parsed=parsed_data)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON response: {content}")
                        return StructuredResponse(content=content, parsed=None)
                else:
                    raise ValueError("Invalid response_format structure")
            else:
                # Handle response_format as Pydantic model (legacy support)
                response = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=messages,
                    response_format=response_format
                )
                parsed_response = response.choices[0].message.parsed
                if parsed_response is not None:
                    return parsed_response
                else:
                    raise TypeError("xAI Model Error: Generated response is None")
                    
        except JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing structured response: {str(e)}")
            raise