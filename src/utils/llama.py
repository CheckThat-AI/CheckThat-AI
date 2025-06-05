import os
import json
from together import Together
from typing import Any, Generator
from fastapi import HTTPException

def get_llama_response(model: str, sys_prompt: str, user_prompt: str, response_format: Any, gen_type: str) -> Generator[str, None, None]:
    try:
        TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        if not TOGETHER_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="TOGETHER_API_KEY environment variable is not set"
            )

        client = Together(api_key=TOGETHER_API_KEY)
        
        if response_format is not None:
            try:
                # Claim normalization: get complete response without streaming
                response = client.chat.completions.create(
                    messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                    model=model,
                    response_format={
                        "type": "json_object",
                        "schema": response_format.model_json_schema(),
                    }
                )
                
                parsed_response = json.loads(response.choices[0].message.content)
                if gen_type == "init":
                    return parsed_response
                else:
                    claim_text = parsed_response.get("claim", "")
                    yield json.dumps({"normalizedClaim": claim_text})
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to parse JSON response: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing response: {str(e)}"
                )
        else:
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