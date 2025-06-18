import os
from google import genai
from google.genai import types
from typing import Generator, Union, Type
from fastapi import HTTPException
from json import JSONDecodeError
from .schema import NormalizedClaim, Feedback

def get_gemini_streaming_response(model: str, sys_prompt: str, user_prompt: str) -> Generator[str, None, None]:
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=GEMINI_API_KEY)
        try:
            stream = client.models.generate_content_stream(
                model=model,
                contents=[types.Part.from_text(text=user_prompt)],
                config=types.GenerateContentConfig(
                    system_instruction=sys_prompt
                )
            )
            for chunk in stream:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
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
            detail=f"Gemini API error: {str(e)}"
        )
        
def get_gemini_structured_response(model: str, sys_prompt: str, user_prompt: str, response_format: Type[Union[NormalizedClaim, Feedback]]) -> Union[NormalizedClaim, Feedback]:
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=GEMINI_API_KEY)
        try:
            response = client.models.generate_content(
                            model=model,
                            contents=[types.Part.from_text(text=user_prompt)],
                            config=types.GenerateContentConfig(
                                system_instruction=sys_prompt,
                                response_mime_type='application/json',
                                response_schema=response_format
                            ),
                        )
            parsed_response = response.parsed
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
            detail=f"Gemini API error: {str(e)}"
        )