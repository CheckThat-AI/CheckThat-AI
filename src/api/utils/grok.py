import os
from openai import OpenAI
from typing import Generator, Union, Type
from fastapi import HTTPException
from json import JSONDecodeError
from .schema import NormalizedClaim, Feedback

def get_grok_streaming_response(model: str, sys_prompt: str, user_prompt: str) -> Generator[str, None, None]:
    try:
        GROK_API_KEY = os.getenv("GROK_API_KEY")
        client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                    stream=True
                )
            for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
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
            detail=f"Grok API error: {str(e)}"
        )

def get_grok_structured_response(model: str, sys_prompt: str, user_prompt: str, response_format: Type[Union[NormalizedClaim, Feedback]]) -> Union[NormalizedClaim, Feedback]:
    try:
        GROK_API_KEY = os.getenv("GROK_API_KEY")
        client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")
        try:
            response = client.beta.chat.completions.parse(
                            model=model,
                            messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                            response_format=response_format
                        )
            parsed_response = response.choices[0].message.parsed
            return parsed_response
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
            detail=f"Grok API error: {str(e)}"
        )