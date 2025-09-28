import os
import json
import time
import uuid
import logging

import instructor
import anthropic

from fastapi import HTTPException
from json import JSONDecodeError

from ..types.claims import NormalizedClaim
from ..types.feedback import Feedback
from .conversation_manager import conversation_manager
from ..types.completions import ChatMessage
from typing import Generator, Union, Type, Optional, List, Dict, Any

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
    
    def generate_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None) -> Generator[str, None, None]:
        try:
            # Format messages with conversation history
            if conversation_history:
                system_instruction, messages = conversation_manager.format_for_anthropic(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                system_instruction = sys_prompt
                messages = [{"role": "user", "content": user_prompt}]
            
            logger.info(f"Anthropic API call with {len(messages)} messages")
            
            response = self.client.messages.create(
                max_tokens=8192,
                model=self.model,
                system=system_instruction,
                messages=messages,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API response error: {str(e)}")
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

    def _format_to_openai_response(self, anthropic_response: Any, requested_model: str, usage_info: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Transform Anthropic API response to OpenAI-compatible chat completion format.

        Args:
            anthropic_response: Raw response from Anthropic API (Message object or dict)
            requested_model: The model name that was requested
            usage_info: Optional usage information override

        Returns:
            Dict formatted as OpenAI chat completion response
        """
        try:
            # Extract content from Anthropic response
            content = ""
            if hasattr(anthropic_response, 'content') and anthropic_response.content:
                # Handle Message object with content array
                if isinstance(anthropic_response.content, list) and len(anthropic_response.content) > 0:
                    # Extract text from content blocks (handles current API format)
                    text_blocks = [block.text for block in anthropic_response.content if hasattr(block, 'text') and block.text]
                    content = "".join(text_blocks)
                else:
                    content = str(anthropic_response.content)
            elif isinstance(anthropic_response, dict) and 'content' in anthropic_response:
                # Handle dict format (current API response)
                if isinstance(anthropic_response['content'], list):
                    text_blocks = [block.get('text', '') for block in anthropic_response['content'] if isinstance(block, dict) and block.get('text')]
                    content = "".join(text_blocks)
                else:
                    content = str(anthropic_response['content'])
            elif isinstance(anthropic_response, str):
                # Handle direct text response
                content = anthropic_response
            else:
                content = str(anthropic_response)

            # Extract usage information from Anthropic response
            usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }

            # Check if usage_info override is provided
            if usage_info:
                usage.update(usage_info)
            # Check for usage in Anthropic response (current API includes this)
            elif hasattr(anthropic_response, 'usage') and anthropic_response.usage:
                anthropic_usage = anthropic_response.usage
                usage["prompt_tokens"] = getattr(anthropic_usage, 'input_tokens', 0)
                usage["completion_tokens"] = getattr(anthropic_usage, 'output_tokens', 0)
                usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
            elif isinstance(anthropic_response, dict) and 'usage' in anthropic_response:
                anthropic_usage = anthropic_response['usage']
                usage["prompt_tokens"] = anthropic_usage.get('input_tokens', 0)
                usage["completion_tokens"] = anthropic_usage.get('output_tokens', 0)
                usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
            else:
                # Fallback estimation if no usage info available
                completion_tokens = len(content.split()) * 1.3  # Rough token estimation
                usage["completion_tokens"] = int(completion_tokens)
                usage["total_tokens"] = int(completion_tokens)

            # Extract finish reason from Anthropic response
            finish_reason = "stop"
            stop_reason = None

            if hasattr(anthropic_response, 'stop_reason'):
                stop_reason = anthropic_response.stop_reason
            elif isinstance(anthropic_response, dict) and 'stop_reason' in anthropic_response:
                stop_reason = anthropic_response['stop_reason']

            if stop_reason:
                finish_reason_mapping = {
                    "end_turn": "stop",
                    "max_tokens": "length",
                    "stop_sequence": "stop"
                }
                finish_reason = finish_reason_mapping.get(stop_reason, "stop")

            # Use Anthropic's message ID if available, otherwise generate one
            message_id = f"chatcmpl-{uuid.uuid4().hex}"
            if hasattr(anthropic_response, 'id') and anthropic_response.id:
                message_id = f"chatcmpl-{anthropic_response.id}"
            elif isinstance(anthropic_response, dict) and 'id' in anthropic_response:
                message_id = f"chatcmpl-{anthropic_response['id']}"

            # Build OpenAI-compatible response
            openai_response = {
                "id": message_id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": requested_model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": finish_reason
                }],
                "usage": usage
            }

            # Add Anthropic-specific extensions for debugging/transparency
            anthropic_extensions = {}
            if hasattr(anthropic_response, 'stop_reason') or (isinstance(anthropic_response, dict) and 'stop_reason' in anthropic_response):
                anthropic_extensions["anthropic_stop_reason"] = stop_reason
            if hasattr(anthropic_response, 'stop_sequence') or (isinstance(anthropic_response, dict) and 'stop_sequence' in anthropic_response):
                stop_sequence = getattr(anthropic_response, 'stop_sequence', None) if hasattr(anthropic_response, 'stop_sequence') else anthropic_response.get('stop_sequence')
                if stop_sequence:
                    anthropic_extensions["anthropic_stop_sequence"] = stop_sequence

            if anthropic_extensions:
                openai_response.update(anthropic_extensions)

            return openai_response

        except Exception as e:
            logger.error(f"Error formatting Anthropic response to OpenAI format: {str(e)}")
            # Fallback to basic structure
            content = ""
            if isinstance(anthropic_response, dict) and 'content' in anthropic_response:
                if isinstance(anthropic_response['content'], list):
                    text_blocks = [block.get('text', '') for block in anthropic_response['content'] if isinstance(block, dict)]
                    content = "".join(text_blocks)
            else:
                content = str(anthropic_response) if anthropic_response else ""

            return {
                "id": f"chatcmpl-{uuid.uuid4().hex}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": requested_model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": len(content.split()) if content else 0,
                    "total_tokens": len(content.split()) if content else 0
                }
            }
