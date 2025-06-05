import os
import anthropic
from typing import Any, Generator

def get_claude_response(model: str, sys_prompt: str, user_prompt: str, response_format: Any, gen_type: str) -> Generator[str, None, None]:
    ERROR_MESSAGE = "Exception in Claude's response: "
    try:
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        if response_format is not None:
            # Claim normalization: stream, then parse, then stream the claim field
            stream = client.messages.create(
                model=model,
                max_tokens=8192,
                response_format={"type": "json"},
                messages=[{"role": "user", "content": user_prompt}, {"role": "system", "content": sys_prompt}],
                stream=True
            )
            collected_chunks = []
            for chunk in stream:
                if hasattr(chunk, 'content') and chunk.content:
                    collected_chunks.append(chunk.content)
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
            stream = client.messages.create(
                model=model,
                messages=[{"role": "user", "content": user_prompt}],
                stream=True
            )
            for chunk in stream:
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
    except Exception as e:
        print(f"{ERROR_MESSAGE} {e}")
        yield "None"
