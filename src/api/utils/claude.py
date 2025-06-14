import os
import json
import instructor
import anthropic
from typing import Generator, Union, Type
from fastapi import HTTPException
from json import JSONDecodeError
from .schema import NormalizedClaim, Feedback

def get_claude_streaming_response(model: str, sys_prompt: str, user_prompt: str) -> Generator[str, None, None]:
    try:
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        try:
            with client.messages.stream(
                max_tokens=8192,
                system=sys_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                model=model,
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error during streaming: {str(e)}"
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Anthropic API error: {str(e)}"
        )

def get_claude_structured_response(model: str, sys_prompt: str, user_prompt: str, response_format: Type[Union[NormalizedClaim, Feedback]]) -> Union[NormalizedClaim, Feedback]:
    try:
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        client = instructor.from_anthropic(anthropic.Anthropic(api_key=ANTHROPIC_API_KEY))
        try:
            response = client.chat.completions.create(
                model=model,
                system=sys_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                response_model=response_format,
                max_retries=2,
            )
            return response
        except JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse JSON response: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing response: {str(e)}"
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Anthropic API error: {str(e)}"
        )