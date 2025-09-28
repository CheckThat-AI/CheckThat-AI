import os
import json
import logging

from openai import OpenAI, NotGiven
from fastapi import HTTPException
from json import JSONDecodeError

from ..types.claims import NormalizedClaim
from ..types.feedback import Feedback
from .conversation_manager import conversation_manager
from ..types.completions import ChatMessage
from .._utils.prompts import sys_prompt as SystemPrompt
from typing import Generator, Union, Type, Optional, List, Dict, Any
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai import Stream

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
        
    def generate_response_from_params(self, openai_params: Dict[str, Any]) -> Any:
        """Generate response directly from OpenAI parameters dict."""
        try:
            # Ensure model is set
            completion_params = {
                "model": self.model,
                **openai_params
            }
            
            logger.info(f"xAI API call with parameters: {list(completion_params.keys())}")
            
            response = self.client.chat.completions.create(**completion_params)
            return response
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            raise

    def generate_streaming_response_from_params(self, openai_params: Dict[str, Any]) -> Stream[ChatCompletionChunk]:
        """Generate streaming response directly from OpenAI parameters dict."""
        try:
            # Ensure model and streaming are set
            completion_params = {
                "model": self.model,
                "stream": True,
                **openai_params
            }
            
            logger.info(f"xAI streaming API call with parameters: {list(completion_params.keys())}")
            
            stream = self.client.chat.completions.create(**completion_params)
            return stream
        except Exception as e:
            logger.error(f"xAI streaming API response error: {str(e)}")
            raise

    def generate_response(self, user_prompt: str, sys_prompt: str = SystemPrompt, conversation_history: Optional[List[ChatMessage]] = None, **openai_params) -> Any:
        """Legacy method - generate response with prompts."""
        try:
            # Format messages with conversation history (xAI uses OpenAI format)
            if conversation_history:
                messages = conversation_manager.format_for_openai(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]
            
            params = {
                "messages": messages,
                **openai_params
            }
            
            return self.generate_response_from_params(params)
        except Exception as e:
            logger.error(f"xAI API response error: {str(e)}")
            raise
        
    def generate_streaming_response(self, user_prompt: str, sys_prompt: str = SystemPrompt, conversation_history: Optional[List[ChatMessage]] = None, **openai_params) -> Stream[ChatCompletionChunk]:
        """Legacy method - generate streaming response with prompts."""
        try:
            # Format messages with conversation history (xAI uses OpenAI format)
            if conversation_history:
                messages = conversation_manager.format_for_openai(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]
            
            params = {
                "messages": messages,
                **openai_params
            }
            
            return self.generate_streaming_response_from_params(params)
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