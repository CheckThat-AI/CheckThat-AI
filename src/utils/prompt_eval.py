import os
import json
from together import Together
from typing import Any
from pydantic import BaseModel, Field

class PromptType(BaseModel):
    prompt_type: str = Field(description="The type of user query.")

def get_prompt_type(user_prompt:str) -> PromptType:
    """ This function takes a user prompt and returns the type of prompt.
    
    Args:
        user_prompt (str): The user's input prompt.
    """
    assert isinstance(user_prompt, str), "user_prompt must be a string"
    
    ERROR_MESSAGE = "Exception in get_prompt_type: "
    
    system_prompt = """# Identity
    You are a helpful assistant that can identify the type of user query. 
    # Instructions
    * Your job is to evaluate the user prompt or query provided and assess the type of user query.
    * The user query can be of the following types:
        - A source text that needs to be examined for claims and that claim needs to be normalized. This kind of query may or may not accompany any task instruction along with the source text.
        - A simple general query that is likely directed to a chatbot and needs to be answered by the chatbot responding to the user query on a broad range of topics including the claim normalization concept.
    * Your job is to identify the type of user query of one of the two types mentioned above.
    * Your response should be a JSON object with the following fields:
        - prompt_type: The type of user query.
        - Eg: {"prompt_type": "claim_normalization"} or {"prompt_type": "general_query"}
    """
    try:
        TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        client = Together(api_key=TOGETHER_API_KEY)
        
        response = client.chat.completions.create(
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                        response_format={
                            "type": "json_object",
                            "schema": PromptType.model_json_schema(),
                        },
                    )
        
        generated_claim = json.loads(response.choices[0].message.content)
        prompt_type = generated_claim["prompt_type"]
        #print(f"Prompt type: {prompt_type}")

    except Exception as e:
        print(f"{ERROR_MESSAGE} {e}")
        prompt_type = "None"

    return prompt_type