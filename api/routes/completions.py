import time
import json
import uuid
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union, Literal, Generator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse

from ..utils.LLMRouter import LLMRouter
from ..utils.models import OPENAI_MODELS, xAI_MODELS, TOGETHER_MODELS, ANTHROPIC_MODELS, GEMINI_MODELS
from ..types import (
    ChatCompletionCreateParams,
    ChatCompletion,
    ParsedChatCompletion,
    CompletionUsage,
    ChatCompletionChoice,
    EvaluationReport
)

router = APIRouter(prefix="/v1", tags=["enhanced-chat-completions"])

VALID_MODELS = OPENAI_MODELS + xAI_MODELS + TOGETHER_MODELS + ANTHROPIC_MODELS + GEMINI_MODELS

# Models that support structured outputs
STRUCTURED_OUTPUT_SUPPORTED_MODELS = [
    # OpenAI models
    "gpt-5-2025-08-07", "gpt-5-nano-2025-08-07", "o3-2025-04-16", "o4-mini-2025-04-16",
    "gpt-4o-2024-08-06", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20",
    "gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo",
    # Gemini models
    "gemini-2.5-pro", "gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash",
    # xAI models (Groq supports structured outputs)
    "grok-3", "grok-4-0709", "grok-3-mini",
    # Together AI models (some support structured outputs)
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    # Anthropic models (limited structured output support)
    "claude-sonnet-4-20250514"
]


def extract_checkthat_params(extra_body: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract CheckThat AI custom parameters from extra_body.

    Args:
        extra_body: The extra_body dictionary from the request

    Returns:
        Dictionary with extracted CheckThat AI parameters
    """
    if not extra_body:
        return {
            'refine_claims': False,
            'post_norm_eval_metrics': None,
            'save_eval_report': None,
            'checkthat_api_key': None
        }

    return {
        'refine_claims': extra_body.get('refine_claims', False),
        'post_norm_eval_metrics': extra_body.get('post_norm_eval_metrics'),
        'save_eval_report': extra_body.get('save_eval_report'),
        'checkthat_api_key': extra_body.get('checkthat_api_key')
    }


def create_completion_response(
    id_: str,
    model: str,
    content: str,
    usage: CompletionUsage,
    parsed_data: Optional[Dict[str, Any]] = None,
    evaluation_report: Optional[EvaluationReport] = None,
    refinement_metadata: Optional[Dict[str, Any]] = None
) -> ChatCompletion:
    """
    Create a standardized OpenAI-compatible ChatCompletion response.

    Args:
        id_: Unique completion identifier
        model: Model used for completion
        content: Generated content
        usage: Token usage statistics
        parsed_data: Parsed data for structured outputs
        evaluation_report: CheckThat AI evaluation results
        refinement_metadata: Metadata about claim refinement process

    Returns:
        ChatCompletion object matching OpenAI format
    """
    now = int(time.time())

    # Build message with content and optional parsed data
    message = {"role": "assistant", "content": content}
    if parsed_data is not None:
        message["parsed"] = parsed_data

    # Create response object
    response_data = {
        "id": id_,
        "object": "chat.completion",
        "created": now,
        "model": model,
        "choices": [{
            "index": 0,
            "message": message,
            "finish_reason": "stop",
        }],
        "usage": usage.model_dump(),
    }

    # Add CheckThat AI extensions if available
    if evaluation_report:
        response_data["evaluation_report"] = evaluation_report.model_dump()
    if refinement_metadata:
        response_data["refinement_metadata"] = refinement_metadata

    return ChatCompletion(**response_data)


def create_parsed_completion_response(
    id_: str,
    model: str,
    parsed_data: Any,
    usage: CompletionUsage,
    evaluation_report: Optional[EvaluationReport] = None,
    refinement_metadata: Optional[Dict[str, Any]] = None
) -> ParsedChatCompletion:
    """
    Create a ParsedChatCompletion response for structured outputs.

    Args:
        id_: Unique completion identifier
        model: Model used for completion
        parsed_data: Parsed structured data
        usage: Token usage statistics
        evaluation_report: CheckThat AI evaluation results
        refinement_metadata: Metadata about claim refinement process

    Returns:
        ParsedChatCompletion object matching OpenAI format
    """
    now = int(time.time())

    # Create response object with parsed data
    response_data = {
        "id": id_,
        "object": "chat.completion",
        "created": now,
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": json.dumps(parsed_data) if parsed_data else "",
                "parsed": parsed_data
            },
            "finish_reason": "stop",
        }],
        "usage": usage.model_dump(),
    }

    # Add CheckThat AI extensions if available
    if evaluation_report:
        response_data["evaluation_report"] = evaluation_report.model_dump()
    if refinement_metadata:
        response_data["refinement_metadata"] = refinement_metadata

    return ParsedChatCompletion(**response_data)


async def process_checkthat_enhancements(
    client,
    model: str,
    messages: List[Dict[str, Any]],
    content: str,
    checkthat_params: Dict[str, Any]
) -> tuple[Optional[EvaluationReport], Optional[Dict[str, Any]]]:
    """
    Process CheckThat AI enhancements (placeholder for future implementation).

    Args:
        client: LLM client instance
        model: Model name
        messages: Original messages
        content: Generated content
        checkthat_params: CheckThat AI custom parameters

    Returns:
        Tuple of (evaluation_report, refinement_metadata)
    """
    evaluation_report = None
    refinement_metadata = None

    # Placeholder for claim refinement processing
    if checkthat_params.get('refine_claims'):
        print("🔧 [PLACEHOLDER] Claim refinement processing would be implemented here")
        refinement_metadata = {
            "refinement_applied": True,
            "processing_timestamp": time.time(),
            "model_used": model
        }

    # Placeholder for evaluation processing
    if checkthat_params.get('post_norm_eval_metrics'):
        print(f"📊 [PLACEHOLDER] Evaluation processing would be implemented here for metrics: {checkthat_params['post_norm_eval_metrics']}")
        evaluation_report = EvaluationReport(
            metrics_used=checkthat_params['post_norm_eval_metrics'],
            scores={},  # Placeholder - would contain actual scores
            detailed_results={},  # Placeholder - would contain detailed results
            timestamp=time.time(),
            model_info={"model": model, "provider": "placeholder"}
        )

    # Placeholder for report saving
    if checkthat_params.get('save_eval_report') and evaluation_report:
        print("💾 [PLACEHOLDER] Report saving would be implemented here")
        if checkthat_params.get('checkthat_api_key'):
            print("☁️ [PLACEHOLDER] Cloud storage would be implemented here")
        else:
            print("💻 [PLACEHOLDER] Local storage would be implemented here")

    return evaluation_report, refinement_metadata


async def generate_completion_with_enhancements(
    client,
    model: str,
    messages: List[Dict[str, Any]],
    checkthat_params: Dict[str, Any],
    **generation_params
) -> tuple[str, CompletionUsage]:
    """
    Generate completion with CheckThat AI enhancements.

    Args:
        client: LLM client instance
        model: Model name
        messages: Conversation messages
        checkthat_params: CheckThat AI custom parameters
        **generation_params: Additional generation parameters

    Returns:
        Tuple of (generated_content, usage_stats)
    """
    # For now, use the existing streaming functionality to generate content
    # In the future, this could be enhanced with actual claim refinement

    # Extract system prompt and user query from messages
    sys_prompt = ""
    user_query = ""
    conversation_history = []

    for msg in messages:
        if msg["role"] == "system" and not sys_prompt:
            sys_prompt = msg["content"]
        elif msg["role"] == "user":
            user_query = msg["content"]
        elif msg["role"] == "assistant":
            conversation_history.append({"role": "assistant", "content": msg["content"]})

    # Generate content using existing streaming functionality
    content_parts = []
    chunk_count = 0

    for chunk in client.generate_streaming_response(
        sys_prompt=sys_prompt,
        user_prompt=user_query,
        conversation_history=conversation_history
    ):
        if chunk:
            content_parts.append(str(chunk))
            chunk_count += 1

    content = "".join(content_parts).strip()

    # Create usage statistics (placeholder - would be more accurate in production)
    usage = CompletionUsage(
        prompt_tokens=len(user_query.split()) + len(sys_prompt.split()),
        completion_tokens=len(content.split()),
        total_tokens=len(user_query.split()) + len(sys_prompt.split()) + len(content.split())
    )

    print(f"✅ Generated content: {len(content)} chars, {chunk_count} chunks")

    return content, usage


@router.post("/chat/completions")
async def enhanced_chat_completions(
    request: Request,
    params: ChatCompletionCreateParams
):
    """
    Enhanced OpenAI-compatible chat completions endpoint with CheckThat AI integration.

    Supports all OpenAI parameters plus CheckThat AI custom enhancements:
    - refine_claims: Enable claim refinement and normalization
    - post_norm_eval_metrics: Quality evaluation metrics to run
    - save_eval_report: Save evaluation reports
    - checkthat_api_key: CheckThat AI API key for cloud services

    Authentication: API key provided in request body (api_key field)
    """
    try:
        print(f"🚀 Received enhanced chat completion request: model={params.model}, messages={len(params.messages)}")

        # Get API key from request body
        api_key = params.api_key
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="API key is required. Provide api_key in the request body."
            )

        # Basic validation
        if params.model not in VALID_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model. Supported models: {', '.join(VALID_MODELS)}"
            )

        if not params.messages or params.messages[-1].role != "user":
            raise HTTPException(
                status_code=400,
                detail="Last message must be from role 'user'."
            )

        # Extract CheckThat AI custom parameters from extra_body
        checkthat_params = extract_checkthat_params(params.extra_body)
        print(f"🔧 CheckThat AI parameters: {checkthat_params}")

        # Get API client
        client = LLMRouter(params.model, api_key=api_key).get_api_client()

        # Handle structured output requests
        if params.response_format:
            print("🔧 Processing structured output request")

            # Validate model support for structured outputs
            if params.model not in STRUCTURED_OUTPUT_SUPPORTED_MODELS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Model {params.model} does not support structured outputs. Supported models: {', '.join(STRUCTURED_OUTPUT_SUPPORTED_MODELS)}"
                )

            # Validate streaming compatibility
            if params.stream:
                raise HTTPException(
                    status_code=400,
                    detail="Structured outputs do not support streaming. Set stream=false."
                )

            # For now, generate regular completion and return as parsed
            # In the future, this would use actual structured output generation
            content, usage = await generate_completion_with_enhancements(
                client, params.model, [msg.model_dump() for msg in params.messages], checkthat_params
            )

            # Process CheckThat AI enhancements
            evaluation_report, refinement_metadata = await process_checkthat_enhancements(
                client, params.model, [msg.model_dump() for msg in params.messages],
                content, checkthat_params
            )

            # Create parsed response (placeholder parsing)
            try:
                parsed_data = json.loads(content) if content.strip() else None
            except json.JSONDecodeError:
                parsed_data = {"content": content}

            response = create_parsed_completion_response(
                id_=f"chatcmpl-{uuid.uuid4().hex}",
                model=params.model,
                parsed_data=parsed_data,
                usage=usage,
                evaluation_report=evaluation_report,
                refinement_metadata=refinement_metadata
            )

        else:
            # Handle regular chat completion
            print("💬 Processing regular chat completion")

            if params.stream:
                # Handle streaming response
                return _create_enhanced_streaming_response(
                    client, params.model, [msg.model_dump() for msg in params.messages],
                    checkthat_params, params
                )
            else:
                # Handle non-streaming response
                content, usage = await generate_completion_with_enhancements(
                    client, params.model, [msg.model_dump() for msg in params.messages], checkthat_params
                )

                # Process CheckThat AI enhancements
                evaluation_report, refinement_metadata = await process_checkthat_enhancements(
                    client, params.model, [msg.model_dump() for msg in params.messages],
                    content, checkthat_params
                )

                response = create_completion_response(
                    id_=f"chatcmpl-{uuid.uuid4().hex}",
                    model=params.model,
            content=content,
                    usage=usage,
                    evaluation_report=evaluation_report,
                    refinement_metadata=refinement_metadata
        )

        print("✅ Enhanced chat completion processed successfully")
        return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in enhanced chat completions: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


def _create_enhanced_streaming_response(
    client,
    model: str,
    messages: List[Dict[str, Any]],
    checkthat_params: Dict[str, Any],
    params: ChatCompletionCreateParams
):
    """Create streaming response with CheckThat AI enhancements."""
    def sse_stream() -> Generator[str, None, None]:
        created = int(time.time())
        cid = f"chatcmpl-{uuid.uuid4().hex}"

        try:
            # For now, stream regular content
            # In the future, this could include real-time refinement indicators
            for chunk in client.generate_streaming_response(
                sys_prompt="",  # Would be extracted from messages
                user_prompt=messages[-1]["content"] if messages else "",
                conversation_history=messages[:-1] if len(messages) > 1 else []
            ):
                data = {
                    "id": cid,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": str(chunk)},
                        "finish_reason": None,
                    }],
                }
                yield f"data: {json.dumps(data)}\n\n"

            # Final chunk with finish_reason
            end = {
                "id": cid,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop",
                }],
            }
            yield f"data: {json.dumps(end)}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            err = {"error": str(e)}
            yield f"data: {json.dumps(err)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )