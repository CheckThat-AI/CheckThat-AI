import os
import anthropic
from typing import Any

def get_claude_response(model: str, sys_prompt: str, user_prompt: str, response_format: Any, gen_type: str) -> str:

    ERROR_MESSAGE = "Exception in Claude's response: "
    generated_claim: str = "None"

    try:
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        client = anthropic.Anthropic(
            # defaults to os.environ.get("ANTHROPIC_API_KEY")
            api_key=ANTHROPIC_API_KEY,
        )

        response = client.messages.create(
            model=model,
            response_format={"type": "json"},
            messages=[
                {"role": "user", "content": "Hello, Claude"}
            ]
        )
        generated_claim = response.content

        if gen_type == "init" or gen_type == "refine":
            generated_claim = generated_claim.claim

    except Exception as e:
        print(f"{ERROR_MESSAGE} {e}")
        generated_claim = "None"

    return generated_claim
