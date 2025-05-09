import os
import json
from together import Together

def get_llama_response(sys_prompt: str, user_prompt: str, response_format: str, gen_type: str) -> str:

    ERROR_MESSAGE = "Exception in Llama's response: "
    
    generated_claim: str = "None"
    
    try:
        TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        client = Together(api_key=TOGETHER_API_KEY)
        
        response = client.chat.completions.create(
                        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                        response_format={
                            "type": "json_object",
                            "schema": response_format.model_json_schema(),
                        },
                    )
        
        generated_claim = json.loads(response.choices[0].message.content)
            
        if gen_type == "init" or gen_type == "refine":
            generated_claim = generated_claim["claim"]

    except Exception as e:
        print(f"{ERROR_MESSAGE} {e}")
        generated_claim = "None"

    return generated_claim
