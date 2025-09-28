"""
Chat Completions API Endpoint

This module provides the OpenAI-compatible chat completions endpoint.
It uses a service layer architecture for clean separation of concerns.
"""

import logging
import json
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

from ...types.completions import CheckThatCompletionCreateParams
from ...services.chat.completions import completion_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

router = APIRouter(prefix="/v1", tags=["chat/completions"])


# Legacy functions have been moved to the service layer for better separation of concerns


@router.post("/chat/completions")
async def completions(
    request: Request,
    body: CheckThatCompletionCreateParams,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    """
    OpenAI-compatible chat completions endpoint with CheckThat AI integration.

    This endpoint uses a service layer architecture following industry standards:
    - Business logic is handled by the service layer
    - Data transformation is handled by the formatter
    - HTTP concerns are handled by the endpoint
    """
    try:
        api_key = credentials.credentials

        logger.info("🚀 Starting OpenAI Chat Completion request processing")
        logger.info(f"Model: {body.model}, Stream: {body.stream}")

        # Use the service layer for business logic orchestration
        response = completion_service.process_completion_request(
            api_key=api_key,
            validated_params=body
        )

        logger.info("✅ Request processing completed successfully")

        # Handle streaming vs non-streaming responses
        if body.stream:
            # For streaming responses, create an async generator from the OpenAI stream
            async def generate_stream():
                try:
                    chunk_count = 0
                    for chunk in response:
                        chunk_count += 1
                        # Convert ChatCompletionChunk to SSE format
                        if hasattr(chunk, 'model_dump_json'):
                            # For OpenAI SDK v1+, chunk is a Pydantic model
                            # Use model_dump_json to avoid serialization issues
                            chunk_json = chunk.model_dump_json()
                            yield f"data: {chunk_json}\n\n"
                        elif hasattr(chunk, 'model_dump'):
                            # Fallback to model_dump and manual JSON encoding
                            chunk_dict = chunk.model_dump()
                            chunk_json = json.dumps(chunk_dict)
                            yield f"data: {chunk_json}\n\n"
                        else:
                            # Last resort: convert to string
                            logger.warning(f"Unexpected chunk type: {type(chunk)}")
                            yield f"data: {json.dumps({'content': str(chunk)})}\n\n"
                    
                    # Send completion signal
                    if chunk_count > 0:
                        yield "data: [DONE]\n\n"
                    else:
                        logger.warning("No chunks received from LLM stream")
                        yield f"data: {json.dumps({'error': 'No content received'})}\n\n"
                        
                except Exception as e:
                    logger.error(f"❌ Error during streaming: {e}")
                    error_response = {
                        "error": {
                            "message": str(e),
                            "type": "streaming_error"
                        }
                    }
                    yield f"data: {json.dumps(error_response)}\n\n"
                    yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
            )
        else:
            # For non-streaming responses, return the response object directly
            return response

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors from service layer)
        raise
    except ValueError as e:
        # Handle validation and parameter errors
        logger.error(f"❌ Validation error in chat completions: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Bad Request",
                "message": str(e),
                "type": "validation_error"
            }
        )
    except Exception as e:
        # Handle all other unexpected errors
        logger.error(f"❌ Unexpected error in chat completions: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while processing your request",
                "type": "server_error"
            }
        )
