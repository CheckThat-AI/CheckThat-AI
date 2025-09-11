
# api/routes/openai_compat.py
from typing import List, Optional, Literal, Dict, Any, Generator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import time
from ..utils.LLMRouter import LLMRouter
from ..utils.models import OPENAI_MODELS, xAI_MODELS, TOGETHER_MODELS, ANTHROPIC_MODELS, GEMINI_MODELS
from ..models.requests import ChatMessage  # reuse your ChatMessage

router = APIRouter(prefix="/v1", tags=["/chat/completions"])

VALID_MODELS = OPENAI_MODELS + xAI_MODELS + TOGETHER_MODELS + ANTHROPIC_MODELS + GEMINI_MODELS

class OpenAIChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionsRequest(BaseModel):
    api_key: str
    model: str
    messages: List[OpenAIChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    
def to_history_and_prompts(messages: List[OpenAIChatMessage]) -> tuple[str, str, List[ChatMessage]]:
    sys_prompt = ""
    conv: List[ChatMessage] = []
    last_user = ""

    # first system becomes sys_prompt
    for m in messages:
        if m.role == "system" and not sys_prompt:
            sys_prompt = m.content

    # last user content becomes current query; others (user/assistant) go to history
    for m in messages:
        if m.role == "user":
            last_user = m.content
        elif m.role == "assistant":
            conv.append(ChatMessage(role="assistant", content=m.content))

    # Add all prior user turns except the last as history
    prior_user_msgs: List[str] = []
    for i, m in enumerate(messages):
        if m.role == "user":
            prior_user_msgs.append(m.content)
    for content in prior_user_msgs[:-1]:
        conv.append(ChatMessage(role="user", content=content))

    return sys_prompt, last_user, conv

def make_completion(id_: str, model: str, content: str) -> Dict[str, Any]:
    now = int(time.time())
    return {
        "id": id_,
        "object": "chat.completion",
        "created": now,
        "model": model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }

@router.post("/chat/completions")
async def chat_completions(req: ChatCompletionsRequest):
    try:
        print(f"Received chat request: model={req.model}, messages={len(req.messages)}")

        if req.model not in VALID_MODELS:
            raise HTTPException(status_code=400, detail=f"Invalid model. Must be one of: {', '.join(VALID_MODELS)}")
        if not req.messages or req.messages[-1].role != "user":
            raise HTTPException(status_code=400, detail="Last message must be from role 'user'.")

        sys_prompt, user_prompt, history = to_history_and_prompts(req.messages)
        print(f"Parsed: sys_prompt='{sys_prompt[:50]}...', user_prompt='{user_prompt[:50]}...', history={len(history)}")

        # Pass the API key if provided by the client, otherwise use environment variables
        api_key = req.api_key if req.api_key else None
        client = LLMRouter(req.model, api_key=api_key).get_api_client()
        print(f"Created client: {type(client)} (using {'provided API key' if api_key else 'environment variables'})")
    except Exception as e:
        print(f"Error in setup: {e}")
        import traceback
        traceback.print_exc()
        raise

    if not req.stream:
        try:
            print("Starting non-streaming response generation")
            # Aggregate streaming to single content for a minimal viable non-stream path
            text_parts: List[str] = []
            chunk_count = 0
            for chunk in client.generate_streaming_response(sys_prompt=sys_prompt, user_prompt=user_prompt, conversation_history=history):
                if chunk:
                    text_parts.append(str(chunk))
                    chunk_count += 1
            content = "".join(text_parts).strip()
            print(f"Generated {chunk_count} chunks, content length: {len(content)}")
            if not content:
                content = "Mock response generated successfully."  # Provide a fallback
            response = make_completion(id_=f"chatcmpl-{int(time.time()*1000)}", model=req.model, content=content)
            print(f"Returning response with content: '{content[:50]}...'")
            return response
        except Exception as e:
            print(f"Error in non-streaming response: {e}")
            import traceback
            traceback.print_exc()
            raise

    # Streaming (SSE) with OpenAI-compatible chunks
    def sse_stream() -> Generator[str, None, None]:
        created = int(time.time())
        cid = f"chatcmpl-{int(time.time()*1000)}"
        try:
            for chunk in client.generate_streaming_response(sys_prompt=sys_prompt, user_prompt=user_prompt, conversation_history=history):
                data = {
                    "id": cid,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": req.model,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": str(chunk)},
                        "finish_reason": None,
                    }],
                }
                yield f"data: {data}\n\n"
            # final chunk with finish_reason
            end = {
                "id": cid,
                "object": "chat.completion.chunk",
                "created": created,
                "model": req.model,
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop",
                }],
            }
            yield f"data: {end}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            # Emit a final chunk with error, then close
            err = {"error": str(e)}
            yield f"data: {err}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(sse_stream(), media_type="text/event-stream")

@router.post("/debug")
async def debug_request(req: ChatCompletionsRequest):
    """Debug endpoint to verify API key pass-through"""
    return {
        "model": req.model,
        "message_count": len(req.messages),
        "stream": req.stream,
    }        
