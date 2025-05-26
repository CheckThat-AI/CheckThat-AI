import os
import json
from together import Together
from typing import Any, Generator

def get_llama_response(model: str, sys_prompt: str, user_prompt: str, response_format: Any, gen_type: str) -> Generator[str, None, None]:
    ERROR_MESSAGE = "Exception in Llama's response: "
    try:
        TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        client = Together(api_key=TOGETHER_API_KEY)
        print(f"Response format is {response_format}")
        if response_format is not None:
            # Claim normalization: stream, then parse, then stream the claim field
            stream = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                model=model,
                response_format={
                    "type": "json_object",
                    "schema": response_format.model_json_schema(),
                },
                stream=True
            )
            collected_chunks = []
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    collected_chunks.append(chunk.choices[0].delta.content)
            # After streaming is complete, parse and stream the claim field
            full_response = "".join(collected_chunks)
            try:
                parsed_response = json.loads(full_response)
                claim_text = parsed_response.get("claim", "")
                for char in claim_text:
                    yield char
            except json.JSONDecodeError:
                yield "Error: Invalid JSON response"
        else:
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
        print(f"{ERROR_MESSAGE} {e}")
        yield "None"
