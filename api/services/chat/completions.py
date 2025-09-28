"""
Chat Completion Service Layer

This module contains the business logic for chat completion requests.
It handles validation, parameter processing, and orchestration of LLM requests.
"""

import logging
import json
import traceback
from typing import List, Optional, Dict, Any, Union, Tuple
from deepeval.models.base_model import DeepEvalBaseLLM
from pydantic import ValidationError

from ..._utils.formatter import openai_formatter
from ...types.completions import (
    CheckThatCompletionCreateParams,
    ChatCompletion,
    ChatCompletionResponse,
    RefinementMetadata,
)
from ..._utils.prompts import sys_prompt as SystemPrompt, instruction
from ..._utils.openai import OpenAIModel
from ..._utils.xai import xAIModel
from ..._utils.togetherAI import TogetherModel
from ..._utils.gemini import GeminiModel
from ..._utils.anthropic import AnthropicModel
from ..._utils.LLMRouter import LLMRouter
from ..._utils.deepeval_model import DeepEvalModel
from ...services.refinement.refine import RefinementService


class ChatCompletionService:
    """
    Service layer for chat completion business logic.
    Handles validation, parameter processing, and orchestration of LLM requests.
    """

    def __init__(self, formatter=None):
        self.formatter = formatter or openai_formatter
        self.logger = logging.getLogger(__name__)

    def validate_request(self, raw_request_body: Union[str, Dict[str, Any]]) -> CheckThatCompletionCreateParams:
        """
        Step 1-2: Parse and validate the incoming request.

        Args:
            raw_request_body: Raw request body from HTTP endpoint

        Returns:
            Validated CheckThatCompletionCreateParams object

        Raises:
            HTTPException: If validation fails
        """
        try:
            if isinstance(raw_request_body, str):
                parsed_body = json.loads(raw_request_body)
            else:
                parsed_body = raw_request_body

            validated_params = CheckThatCompletionCreateParams(**parsed_body)
            self.logger.info("✅ Request validation successful")
            return validated_params

        except ValidationError as e:
            self.logger.error(f"❌ Request validation failed: {e}")
            # Import HTTPException here to avoid circular imports
            from fastapi import HTTPException
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Validation Error",
                    "details": json.loads(e.json())
                }
            )
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON parsing failed: {e}")
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid JSON",
                    "details": str(e)
                }
            )

    def segregate_parameters(self, validated_params: CheckThatCompletionCreateParams) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Step 3: Segregate standard OpenAI parameters from CheckThat AI custom parameters.

        Args:
            validated_params: Validated request parameters

        Returns:
            Tuple of (openai_payload, checkthat_config)
        """
        # Define CheckThat-specific fields to exclude
        CHECKTHAT_CUSTOM_KEYS = {
            "refine_claims",
            "refine_model",
            "refine_threshold",
            "refine_max_iters",
            "refine_metrics",
            "post_norm_eval_metrics",
            "save_eval_report",
            "checkthat_api_key",
            "api_key",  # Exclude api_key from OpenAI payload
        }

        # Extract OpenAI payload (exclude CheckThat fields and None values)
        openai_payload = validated_params.model_dump(
            exclude_unset=True,  # Exclude fields that were not in the original request
            exclude_none=True,   # Exclude fields with a value of None
            exclude=CHECKTHAT_CUSTOM_KEYS
        )
        
        # Remove api_key if present - it shouldn't be passed to OpenAI completions API
        openai_payload.pop('api_key', None)

        # Extract CheckThat configuration (only include custom fields)
        checkthat_config = validated_params.model_dump(
            include=CHECKTHAT_CUSTOM_KEYS,
            exclude_unset=True
        )

        self.logger.info(f"📋 Parameter segregation complete - OpenAI: {list(openai_payload.keys())}, CheckThat: {list(checkthat_config.keys())}")
        return openai_payload, checkthat_config

    def should_apply_custom_features(self, checkthat_config: Dict[str, Any]) -> bool:
        """Check if any custom CheckThat AI features should be applied."""
        return any([
            checkthat_config.get('refine_claims', False),
            checkthat_config.get('post_norm_eval_metrics'),
            checkthat_config.get('save_eval_report', False)
        ])

    def apply_custom_features(
        self, 
        response: ChatCompletion,
        client: Union[OpenAIModel, GeminiModel, xAIModel, AnthropicModel, TogetherModel],
        api_key: str,
        original_query: str,
        checkthat_config: Dict[str, Any]
    ) -> ChatCompletionResponse:
        
        # Initialize default values
        refined_response = response
        refinement_metadata = None
        
        if checkthat_config.get('refine_claims'):
            try:
                self.logger.info("🔧 Starting claim refinement process")
                self.logger.debug(f"🔧 Original query length: {len(original_query)}")
                
                # Safe access to response content
                try:
                    response_content = response.choices[0].message.content
                    self.logger.debug(f"🔧 Response content length: {len(response_content)}")
                except (AttributeError, IndexError, TypeError) as content_error:
                    self.logger.warning(f"🔧 Could not access response content: {content_error}")
                    response_content = str(response)
                
                self.logger.debug(f"🔧 Client type: {type(client)}")

                from ..refinement.refine import RefinementService
                from ..._utils.deepeval_model import DeepEvalModel

                refine_model = checkthat_config.get('refine_model')
                refine_threshold = checkthat_config.get('refine_threshold', 0.5)
                refine_max_iters = checkthat_config.get('refine_max_iters', 3)
                refine_metrics = checkthat_config.get('refine_metrics')

                self.logger.debug(f"🔧 Refinement params - model: {refine_model}, threshold: {refine_threshold}, max_iters: {refine_max_iters}")
                self.logger.debug(f"🔧 API key length: {len(api_key) if api_key else 0}")

                # Validate required parameters
                if not refine_model:
                    raise ValueError("refine_model is required for claim refinement")

                # Create DeepEval model for evaluation
                self.logger.debug("🔧 Creating DeepEval model...")
                deepeval_model = DeepEvalModel(model=refine_model, api_key=api_key)
                self.logger.debug("🔧 Getting evaluation model...")
                eval_model = deepeval_model.getEvalModel()

                self.logger.debug("🔧 Creating RefinementService...")
                refinement_service = RefinementService(
                    model=eval_model,
                    threshold=refine_threshold,
                    max_iters=refine_max_iters,
                    metrics=refine_metrics
                )

                self.logger.debug("🔧 Calling refine_single_claim...")
                refined_response, refinement_history = refinement_service.refine_single_claim(
                    original_query=original_query,
                    current_claim=response_content,
                    client=client,
                    original_response=response
                )

                self.logger.debug("🔧 Creating RefinementMetadata...")
                refinement_metadata = RefinementMetadata(
                    metric_used=refine_metrics,
                    threshold=refine_threshold,
                    refinement_model=refine_model,
                    refinement_history=refinement_history
                )

                self.logger.info("✅ Claim refinement completed successfully")

            except Exception as e:
                self.logger.error(f"❌ Claim refinement failed: {e}")
                self.logger.error(f"❌ Full traceback: {traceback.format_exc()}")
                
                # Keep original response if refinement fails
                refined_response = response
                
                # Import RefinementHistory for proper error handling
                from ...types.completions import RefinementHistory, ClaimType
                
                error_history = RefinementHistory(
                    claim_type=ClaimType.ORIGINAL,
                    claim=str(response),
                    score=0.0,
                    feedback=f"Refinement failed: {str(e)}"
                )
                
                refinement_metadata = RefinementMetadata(
                    metric_used=refine_metrics,
                    threshold=refine_threshold or 0.5,
                    refinement_model=refine_model or "unknown",
                    refinement_history=[error_history]
                )

        # Create enhanced response with proper error handling
        try:
            enhanced_response = ChatCompletionResponse(
                **refined_response.model_dump(),
                evaluation_report=None,
                refinement_metadata=refinement_metadata,
                checkthat_metadata={
                    "features_applied": {
                        "refine_claims": checkthat_config.get('refine_claims', False),
                        "post_norm_eval_metrics": bool(checkthat_config.get('post_norm_eval_metrics')),
                        "save_eval_report": checkthat_config.get('save_eval_report', False)
                    }
                }
            )
            return enhanced_response
        except Exception as e:
            self.logger.error(f"❌ Failed to create enhanced response: {e}")
            # Fallback to basic ChatCompletionResponse
            return ChatCompletionResponse(
                **response.model_dump(),
                evaluation_report=None,
                refinement_metadata=refinement_metadata,
                checkthat_metadata={
                    "features_applied": {
                        "refine_claims": False,
                        "post_norm_eval_metrics": False,
                        "save_eval_report": False
                    },
                    "error": f"Enhanced response creation failed: {str(e)}"
                }
            )

    def handle_streaming_request(self, openai_payload: Dict[str, Any], client: Any) -> Any:

        self.logger.info("🌊 Processing streaming request (no custom features)")

        api_payload = self.formatter.format_for_client(openai_payload, client.__class__.__name__)

        if hasattr(client, 'generate_streaming_response_from_params'):
            stream = client.generate_streaming_response_from_params(api_payload)
        else:
            messages = api_payload.get("messages", [])
            user_prompt = ""
            sys_prompt = SystemPrompt

            for msg in reversed(messages):
                if msg.get("role") == "user" and not user_prompt:
                    user_prompt = msg.get("content", "")
                elif msg.get("role") == "system":
                    sys_prompt = msg.get("content", SystemPrompt)

            stream_params = {k: v for k, v in api_payload.items()
                           if k not in ['messages', 'model', 'stream']}

            stream = client.generate_streaming_response(
                user_prompt=user_prompt,
                sys_prompt=sys_prompt,
                **stream_params
            )

        return stream

    def handle_non_streaming_request(
        self,
        client: Any,
        api_key: str,
        openai_payload: Dict[str, Any],
        checkthat_config: Dict[str, Any],
    ) -> Union[ChatCompletion, ChatCompletionResponse]:

        self.logger.info("📝 Processing non-streaming request")

        api_payload = self.formatter.format_for_client(openai_payload, client.__class__.__name__)

        # Extract messages for both modern and legacy clients
        messages = api_payload.get("messages", [])
        user_message = ""
        system_message = SystemPrompt

        for msg in reversed(messages):
            if msg.get("role") == "user" and not user_message:
                user_message = msg.get("content", "")
                user_message = f"{instruction}:{user_message}"
            elif msg.get("role") == "system":
                system_message = msg.get("content", SystemPrompt)

        if hasattr(client, 'generate_response_from_params'):
            # Filter out api_key if present - it shouldn't be in OpenAI API parameters
            filtered_payload = {k: v for k, v in api_payload.items() if k != 'api_key'}
            response = client.generate_response_from_params(filtered_payload)
        else:
            # Filter out parameters that shouldn't be passed to generate_response
            excluded_params = {'messages', 'api_key', 'model'}  # model is set by the client itself
            legacy_params = {k: v for k, v in api_payload.items() if k not in excluded_params}
            response = client.generate_response(user_message, system_message, **legacy_params)

        if self.should_apply_custom_features(checkthat_config):
            response = self.apply_custom_features(
                response=response,
                client=client,
                api_key=api_key,
                original_query=f"{instruction}:{user_message}",
                checkthat_config=checkthat_config
            )
            self.logger.info("✨ Custom CheckThat AI features applied")
        else:
            self.logger.info("🔄 No custom features requested")

        return response

    def process_completion_request(
        self,
        api_key: str,
        validated_params: CheckThatCompletionCreateParams,
    ) -> Union[Any, ChatCompletionResponse]:
        
        self.logger.info("🚀 Starting completion request processing")
        self.api_key = api_key
        self.model = validated_params.model
        self.client = LLMRouter(self.model, api_key=self.api_key).getAPIClient()
        
        openai_payload, checkthat_config = self.segregate_parameters(validated_params)

        if 'messages' in openai_payload:
            openai_payload['messages'] = self.formatter.process_messages(openai_payload['messages'])

        if openai_payload.get('stream', False):
            return self.handle_streaming_request(openai_payload, self.client)
        else:
            return self.handle_non_streaming_request(
                self.client, 
                self.api_key,
                openai_payload, 
                checkthat_config
            )

completion_service = ChatCompletionService()