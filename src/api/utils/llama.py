import os
import json
from together import Together
from typing import Generator, Union, Type
from fastapi import HTTPException
from json import JSONDecodeError
from .schema import NormalizedClaim, Feedback

def get_llama_structured_response(model: str, sys_prompt: str, user_prompt: str, response_format: Type[Union[NormalizedClaim, Feedback]]) -> Union[NormalizedClaim, Feedback]:
    """Get a structured JSON response from Llama (non-streaming)"""
    try:
        TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        client = Together(api_key=TOGETHER_API_KEY)
        
        assert response_format in [NormalizedClaim, Feedback], "response_format must be NormalizedClaim or Feedback"
        
        try:
            # Get complete response without streaming
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                model=model,
                response_format={
                    "type": "json_object",
                    "schema": response_format.model_json_schema(),
                }
            )
            parsed_response = json.loads(response.choices[0].message.content)
            
            # return an instance of the specified response_format
            return response_format(**parsed_response)
            
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
            detail=f"Llama API error: {str(e)}"
        )

def get_llama_streaming_response(model: str, sys_prompt: str, user_prompt: str) -> Generator[str, None, None]:
    """Get a streaming text response from Llama"""
    try:
        TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        client = Together(api_key=TOGETHER_API_KEY)
        
        try:
            # General chat: stream text as it arrives
            stream = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                model=model,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
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
            detail=f"Llama API error: {str(e)}"
        )