import os
import json
import time
import uuid
import logging

from together import Together
from fastapi import HTTPException
from json import JSONDecodeError

from ..types.claims import NormalizedClaim
from ..types.feedback import Feedback
from .conversation_manager import conversation_manager
from ..types.completions import ChatMessage
from typing import Generator, Union, Type, Optional, Any, List, Dict
            
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
        
    def generate_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None) -> Generator[str, None, None]:
        try:
            # Format messages with conversation history (TogetherAI uses OpenAI format)
            if conversation_history:
                messages = conversation_manager.format_for_openai(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]
            
            logger.info(f"TogetherAI API call with {len(messages)} messages")
            
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
            )
            return response
        except Exception as e:
            logger.error(f"Together API response error: {str(e)}")
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
                    json_schema = response_format["json_schema"]
                    schema = json_schema.get("schema", {})
                    
                    # Get complete response without streaming
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.model,
                        response_format={
                            "type": "json_object",
                            "schema": schema,
                        }
                    )
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
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.model,
                    response_format={
                        "type": "json_object",
                        "schema": response_format.model_json_schema(),
                    }
                )
                parsed_response = response.choices[0].message.content
                if parsed_response is not None:
                    return response_format(**json.loads(parsed_response))
                else:
                    raise TypeError("Together Model Error: Generated response is None")

        except JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing structured response: {str(e)}")
            raise

    def _format_to_openai_response(self, together_response: Any, requested_model: str) -> Dict[str, Any]:
        """
        Transform TogetherAI API response to OpenAI-compatible chat completion format.

        TogetherAI already returns OpenAI-compatible responses, so this function mainly
        ensures consistency and handles any TogetherAI-specific extensions.

        Args:
            together_response: Raw response from TogetherAI API (OpenAI-compatible object)
            requested_model: The model name that was requested

        Returns:
            Dict formatted as OpenAI chat completion response
        """
        try:
            # TogetherAI responses are already OpenAI-compatible, but we need to handle them properly
            if hasattr(together_response, 'model_dump'):
                # If it's a Pydantic model (newer OpenAI SDK versions)
                response_dict = together_response.model_dump()
            elif hasattr(together_response, '__dict__'):
                # If it's an object with attributes
                response_dict = together_response.__dict__
            elif isinstance(together_response, dict):
                # If it's already a dict
                response_dict = together_response
            else:
                # Fallback: try to convert to dict
                response_dict = dict(together_response) if hasattr(together_response, 'keys') else {}

            # Ensure all required OpenAI fields are present
            openai_response = {
                "id": response_dict.get("id", f"chatcmpl-{uuid.uuid4().hex}"),
                "object": response_dict.get("object", "chat.completion"),
                "created": response_dict.get("created", int(time.time())),
                "model": requested_model,  # Use requested model instead of response model
                "choices": response_dict.get("choices", []),
                "usage": response_dict.get("usage", {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                })
            }

            # Handle TogetherAI-specific extensions
            togetherai_extensions = {}

            # Preserve warnings if present (TogetherAI-specific field)
            if "warnings" in response_dict and response_dict["warnings"]:
                togetherai_extensions["togetherai_warnings"] = response_dict["warnings"]

            # Preserve any additional TogetherAI metadata
            if hasattr(together_response, 'seed') and together_response.seed is not None:
                togetherai_extensions["togetherai_seed"] = together_response.seed

            if hasattr(together_response, 'finish_reason') and together_response.finish_reason:
                # Ensure finish_reason is properly set in choices
                if openai_response["choices"] and len(openai_response["choices"]) > 0:
                    openai_response["choices"][0]["finish_reason"] = together_response.finish_reason

            # Add extensions if any exist
            if togetherai_extensions:
                openai_response.update(togetherai_extensions)

            return openai_response

        except Exception as e:
            logger.error(f"Error formatting TogetherAI response to OpenAI format: {str(e)}")
            # Fallback to basic structure - try to extract content if possible
            content = ""
            if hasattr(together_response, 'choices') and together_response.choices:
                choice = together_response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    content = choice.message.content or ""

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