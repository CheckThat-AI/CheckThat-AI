import os
from google import genai
from google.genai import types
from typing import Any, Generator

def get_gemini_response(model: str, sys_prompt: str, user_prompt: str, response_format: Any, gen_type: str) -> Generator[str, None, None]:
    ERROR_MESSAGE = "Exception in Gemini's response: "
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=GEMINI_API_KEY)
        if response_format is not None:
            # Claim normalization: stream, then parse, then stream the claim field
            stream = client.models.generate_content(
                model=model,
                contents=[types.Part.from_text(text=user_prompt)],
                config=types.GenerateContentConfig(
                    system_instruction=sys_prompt,
                    response_mime_type='application/json',
                    response_schema=response_format
                ),
                stream=True
            )
            collected_chunks = []
            for chunk in stream:
                if hasattr(chunk, 'text') and chunk.text:
                    collected_chunks.append(chunk.text)
            # After streaming is complete, parse and stream the claim field
            full_response = "".join(collected_chunks)
            try:
                import json
                parsed_response = json.loads(full_response)
                claim_text = parsed_response.get("claim", "")
                for char in claim_text:
                    yield char
            except Exception:
                yield "Error: Invalid JSON response"
        else:
            # General chat: stream text as it arrives
            stream = client.models.generate_content(
                model=model,
                contents=[types.Part.from_text(text=user_prompt)],
                config=types.GenerateContentConfig(
                    system_instruction=sys_prompt
                ),
                stream=True
            )
            for chunk in stream:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
    except Exception as e:
        print(f"{ERROR_MESSAGE} {e}")
        yield "None"