import os
import logging
from openai import OpenAI, Stream
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from typing import Generator, Union, Type, Any, Optional, List, Dict
from fastapi import HTTPException
from json import JSONDecodeError
import json
from ..types.claims import NormalizedClaim
from ..types.feedback import Feedback
from .._utils.conversation_manager import conversation_manager
from ..types.completions import ChatMessage
from .._utils.prompts import sys_prompt as SystemPrompt
    
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
        
    def generate_response_from_params(self, openai_params: Dict[str, Any]) -> Any:
        """Generate response directly from OpenAI parameters dict."""
        try:
            # Ensure model is set
            completion_params = {
                "model": self.model,
                **openai_params
            }
            
            logger.info(f"OpenAI API call with parameters: {list(completion_params.keys())}")
            
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
            
            logger.info(f"OpenAI streaming API call with parameters: {list(completion_params.keys())}")
            
            stream = self.client.chat.completions.create(**completion_params)
            return stream
        except Exception as e:
            logger.error(f"OpenAI streaming API response error: {str(e)}")
            raise

    def generate_response(self, user_prompt: str, sys_prompt: str = SystemPrompt, **openai_params) -> Any:
        """Legacy method - generate response with prompts."""
        messages = [
            {"role": "system", "content": sys_prompt}, 
            {"role": "user", "content": user_prompt}
        ]
        
        params = {
            "messages": messages,
            **openai_params
        }
        
        return self.generate_response_from_params(params)
        
    def generate_streaming_response(self, user_prompt: str, sys_prompt: str = SystemPrompt, **openai_params) -> Stream[ChatCompletionChunk]:
        """Legacy method - generate streaming response with prompts."""
        try:
            messages = [
                {"role": "system", "content": sys_prompt}, 
                {"role": "user", "content": user_prompt}
            ]
            
            params = {
                "messages": messages,
                **openai_params
            }
            
            return self.generate_streaming_response_from_params(params)
        except Exception as e:
            logger.error(f"OpenAI API response error: {str(e)}")
            raise

    def generate_structured_response(self, user_prompt: str, sys_prompt: str = SystemPrompt, response_format: ResponseFormat = None) -> Any:
        try:
            messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]

            response = self.client.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=response_format
            )
            return response
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            raise