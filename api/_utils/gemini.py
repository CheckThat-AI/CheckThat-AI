import os
import time
import uuid
from google import genai
from google.genai import types
from typing import Generator, Union, Type, Optional, List, Dict, Any
from fastapi import HTTPException
from json import JSONDecodeError
import json
from ..types.claims import NormalizedClaim
from ..types.feedback import Feedback
from .conversation_manager import conversation_manager
from ..types.completions import ChatMessage

import logging  

logger = logging.getLogger(__name__)
    
class GeminiModel:
    """
    This class is used to generate responses from the Gemini API.
    """
    def __init__(self, model: str, api_key: str = None):
        try:
            if not api_key:
                raise ValueError("Gemini API key is required but not provided")
            
            self.model = model
            self.api_key = api_key
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Gemini Client creation error: {str(e)}")
            raise
    
    def generate_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None) -> Generator[str, None, None]:
        try:
            # Format messages with conversation history
            if conversation_history:
                system_instruction, contents = conversation_manager.format_for_gemini(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                system_instruction = sys_prompt
                contents = [types.Part.from_text(text=user_prompt)]
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API response error: {str(e)}")
            raise
        
    def generate_streaming_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None) -> Generator[str, None, None]:
        try:
            # Format messages with conversation history
            if conversation_history:
                system_instruction, contents = conversation_manager.format_for_gemini(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                system_instruction = sys_prompt
                contents = [types.Part.from_text(text=user_prompt)]
            
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
    
    def generate_structured_response(self, sys_prompt: str, user_prompt: str, conversation_history: Optional[List[ChatMessage]] = None, response_format: Optional[Union[Type[Union[NormalizedClaim, Feedback]], Dict[str, Any]]] = None) -> Any:
        try:
            # Format messages with conversation history
            if conversation_history:
                system_instruction, contents = conversation_manager.format_for_gemini(sys_prompt, conversation_history, user_prompt)
            else:
                # Fallback to single-turn format
                system_instruction = sys_prompt
                contents = [types.Part.from_text(text=user_prompt)]

            # Determine the response format
            if isinstance(response_format, dict):
                # Handle response_format as dict (from API request)
                if response_format.get("type") == "json_schema" and "json_schema" in response_format:
                    json_schema = response_format["json_schema"]
                    schema = json_schema.get("schema", {})
                    
                    # Use Gemini's structured generation
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            response_mime_type='application/json',
                            response_schema=schema  # Pass the schema directly
                        )
                    )
                    
                    # Extract the content and parsed data
                    content = response.text if hasattr(response, 'text') else ""
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
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
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
            raise
        except Exception as e:
            logger.error(f"Error processing structured response: {str(e)}")
            raise

    def _format_to_openai_response(self, gemini_response: Any, requested_model: str) -> Dict[str, Any]:
        """
        Transform Gemini API response to OpenAI-compatible chat completion format.

        Args:
            gemini_response: Raw response from Gemini API
            requested_model: The model name that was requested (not the response model)

        Returns:
            Dict formatted as OpenAI chat completion response
        """
        try:
            # Extract content from Gemini's nested structure
            content = ""
            finish_reason = "stop"

            if hasattr(gemini_response, 'candidates') and gemini_response.candidates:
                candidate = gemini_response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                    content = candidate.content.parts[0].text if hasattr(candidate.content.parts[0], 'text') else ""

                # Map Gemini finish reasons to OpenAI format
                if hasattr(candidate, 'finish_reason'):
                    finish_reason_mapping = {
                        "STOP": "stop",
                        "MAX_TOKENS": "length",
                        "SAFETY": "content_filter",
                        "RECITATION": "content_filter",
                        "OTHER": "stop"
                    }
                    finish_reason = finish_reason_mapping.get(candidate.finish_reason, "stop")

            # Extract usage information
            usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }

            if hasattr(gemini_response, 'usage_metadata'):
                usage_meta = gemini_response.usage_metadata
                usage["prompt_tokens"] = getattr(usage_meta, 'prompt_token_count', 0)
                usage["completion_tokens"] = getattr(usage_meta, 'candidates_token_count', 0)
                usage["total_tokens"] = getattr(usage_meta, 'total_token_count', 0)

            # Build OpenAI-compatible response
            openai_response = {
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
                    "finish_reason": finish_reason
                }],
                "usage": usage
            }

            # Add any Gemini-specific extensions if needed
            if hasattr(gemini_response, 'candidates') and gemini_response.candidates:
                candidate = gemini_response.candidates[0]
                if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                    openai_response["gemini_safety_ratings"] = [
                        {
                            "category": getattr(rating, 'category', ''),
                            "probability": getattr(rating, 'probability', '')
                        } for rating in candidate.safety_ratings
                    ]

            return openai_response

        except Exception as e:
            logger.error(f"Error formatting Gemini response to OpenAI format: {str(e)}")
            # Fallback to basic structure
            return {
                "id": f"chatcmpl-{uuid.uuid4().hex}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": requested_model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": str(gemini_response)
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }