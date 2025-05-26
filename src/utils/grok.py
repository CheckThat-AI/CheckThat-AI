import os
from openai import OpenAI
from typing import Any, Generator

def get_grok_response(model: str, sys_prompt: str, user_prompt: str, response_format: Any, gen_type: str) -> Generator[str, None, None]:
    ERROR_MESSAGE = "Exception in Grok's response: "
    try:
        GROK_API_KEY = os.getenv("GROK_API_KEY")
        client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")
        if response_format is not None:
            # Claim normalization: stream, then parse, then stream the claim field
            stream = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                response_format=response_format,
                stream=True
            )
            collected_chunks = []
            for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    collected_chunks.append(chunk.choices[0].delta.content)
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
            stream = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                stream=True
            )
            for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
    except Exception as e:
        print(f"{ERROR_MESSAGE} {e}")
        yield "None"