import os
import sys
from pathlib import Path
from typing import Union, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from starlette.concurrency import iterate_in_threadpool

# Import from the utils folder that's now inside the api folder
from ..utils.LLMRouter import LLMRouter
from ..utils.prompts import sys_prompt, few_shot_CoT_prompt, chat_guide
from ..utils.models import OPENAI_MODELS, xAI_MODELS, TOGETHER_MODELS, ANTHROPIC_MODELS, GEMINI_MODELS
from ..utils.conversation_manager import conversation_manager
from ..models.requests import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])

VALID_MODELS = OPENAI_MODELS + xAI_MODELS + TOGETHER_MODELS + ANTHROPIC_MODELS + GEMINI_MODELS

@router.post("")
async def chat_interface(request: ChatRequest):
    """
    Endpoint to normalize a single claim from the user provided text
    """
    try:
        print("Requested model:", request.model)

        if request.model not in VALID_MODELS:
            print(f"Invalid model: {request.model}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model. Must be one of: {', '.join(VALID_MODELS)}"
            )

        # Add validation for user_query
        if not request.user_query or not request.user_query.strip():
            raise HTTPException(
                status_code=400,
                detail="User query cannot be empty"
            )
        if request.model in TOGETHER_MODELS:
            api_key = os.getenv("TOGETHER_API_KEY")
        elif request.model in GEMINI_MODELS:
            api_key = os.getenv("GEMINI_API_KEY")
        else:
            api_key = request.api_key
            
        client = LLMRouter(model=request.model, api_key=api_key).get_api_client()

        # Retrieve conversation history if conversation_id is provided
        conversation_history = []
        if request.conversation_id:
            conversation_history = await conversation_manager.get_conversation_history(
                request.conversation_id, 
                request.max_history_tokens or 4000
            )
            print(f"Retrieved {len(conversation_history)} messages from conversation {request.conversation_id}")
        
        # Use conversation history if provided in request (fallback)
        if not conversation_history and request.conversation_history:
            conversation_history = request.conversation_history
            print(f"Using provided conversation history with {len(conversation_history)} messages")

        # Use a sync generator and run it via iterate_in_threadpool to avoid blocking the event loop
        def stream_response():
            try:
                chunk_count = 0
                
                # Build the user prompt with context
                full_user_prompt = f"{few_shot_CoT_prompt}\n{chat_guide}\n\n{request.user_query}"
                
                for chunk in client.generate_streaming_response(
                    sys_prompt=sys_prompt,
                    user_prompt=full_user_prompt,
                    conversation_history=conversation_history
                ):
                    # Extract the text content if chunk is a tuple
                    if isinstance(chunk, tuple) and len(chunk) > 0:
                        content = str(chunk[0])
                    else:
                        content = str(chunk)
                    
                    # Yield small text chunks promptly
                    if content:
                        chunk_count += 1
                        yield content
                
                # Log completion for debugging
                print(f"Stream completed successfully. Total chunks: {chunk_count}")
                
            except ValueError as ve:
                print(f"Value error in stream_response: {str(ve)}")
                yield f"\n\n[Error 400: Bad Request - {str(ve)}]"
            except PermissionError as pe:
                print(f"Permission error in stream_response: {str(pe)}")
                yield f"\n\n[Error 403: Forbidden - {str(pe)}]"
            except Exception as e:
                print(f"Error in stream_response: {str(e)}")
                # Yield error message if something goes wrong
                yield f"\n\n[{str(e)}]"
            finally:
                # Ensure generator properly closes
                print("Stream generator finished")

        return StreamingResponse(
            iterate_in_threadpool(stream_response()),
            media_type="text/plain; charset=utf-8",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            },
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        print("Error in chat_interface:", str(e))
        raise HTTPException(status_code=500, detail=str(e))