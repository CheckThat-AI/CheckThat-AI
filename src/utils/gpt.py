import os
from openai import OpenAI
from typing import Any

def get_gpt_response(model: str, sys_prompt: str, user_prompt: str, response_format: Any, gen_type: str) -> str:
    
    ERROR_MESSAGE = "Exception in GPT's response: "
    generated_claim: str = "None"
    
    try:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.beta.chat.completions.parse(
                        model=model,
                        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                        response_format=response_format
                    )
        
        generated_claim = response.choices[0].message.parsed
        
        if gen_type == "init" or gen_type == "refine":
            generated_claim = generated_claim.claim

    except Exception as e:
        print(f"{ERROR_MESSAGE} {e}")
        generated_claim = "None"

    return generated_claim
