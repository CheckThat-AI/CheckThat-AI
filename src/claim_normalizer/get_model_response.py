import os
import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from openai import OpenAI
from together import Together
from google import genai
from google.genai import types

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROK_API_KEY = os.getenv("GROK_API_KEY")

class NormalizedClaim(BaseModel):
    claim: str = Field(description="A normalized claim extracted from the noisy input text.")

class Feedback(BaseModel):
    verifiability: List[str] = Field(description="Feedback and Score for verifiability (0-10 scale)")
    false_likelihood: List[str] = Field(description="Feedback and Score for likelihood of being false (0-10 scale)")
    public_interest: List[str] = Field(description="Feedback and Score for public interest (0-10 scale)")
    potential_harm: List[str] = Field(description="Feedback and Score for potential harm (0-10 scale)")
    check_worthiness: List[str] = Field(description="Feedback and Score for check-worthiness (0-10 scale)")
    
chain_of_thought_trigger = "Let's think step by step."

def get_model_response(model:str, user_prompt:str, sys_prompt:str, gen_type:str)->str:
    """ This function takes a user prompt and a system prompt, and returns the generated response of the model using OpenAI's API.
    
    Args:
        user_prompt (str): The user's input prompt with the task query.
        sys_prompt (str): The system prompt to guide the model's response.

    Returns:
        str: The generated response from the model.
    
    """
    assert isinstance(user_prompt, str), "user_prompt must be a string"
    assert isinstance(sys_prompt, str), "sys_prompt must be a string"
    assert gen_type in ("feedback", "init", "refine"), f"gen_type must be either 'feedback' or 'init' or 'refine'; got {gen_type}"
    
    if gen_type == "feedback":
        output_type = Feedback
    else:
        output_type = NormalizedClaim
    
    generated_claim: str = "None"
     
    if model == "OpenAI":
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4.1-nano-2025-04-14",
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                response_format=output_type
            )
            generated_claim = response.choices[0].message.parsed
            if gen_type == "init" or gen_type == "refine":
                generated_claim = generated_claim.claim

        except Exception as e:
            print("Error:", e)
            generated_claim = "None"
    
    elif model == "Grok":
        client = OpenAI(
            api_key=GROK_API_KEY,
            base_url="https://api.x.ai/v1",
        )
        
        try:
            response = client.beta.chat.completions.parse(
                model="grok-3-latest",
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                response_format=output_type
            )

            generated_claim = response.choices[0].message.parsed
            if gen_type == "init" or gen_type == "refine":
                generated_claim = generated_claim.claim

        except Exception as e:
            print("Error:", e)
            generated_claim = "None"
             
    elif model == "Llama":
        client = Together(api_key=TOGETHER_API_KEY)
        
        try:
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                response_format={
                    "type": "json_object",
                    "schema": output_type.model_json_schema(),
                },
            )
            generated_claim = json.loads(response.choices[0].message.content)
            if gen_type == "init" or gen_type == "refine":
                generated_claim = generated_claim["claim"]
            
        except Exception as e:
            print(f"Error: {e}", response.choices[0].message.content)
            generated_claim = "None"  
        
    elif model == "Gemini":
        client = genai.Client(api_key=GEMINI_API_KEY)
       
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[types.Part.from_text(text=user_prompt)],
                config=types.GenerateContentConfig(
                    system_instruction=sys_prompt,
                    response_mime_type='application/json',
                    response_schema=output_type
                ),
            )
            generated_claim = response.parsed
            if gen_type == "init" or gen_type == "refine":
                generated_claim = generated_claim.claim

        except Exception as e:
            print("Error:", e)
            generated_claim = "None"
            
    #print(f"Model: {model}, Response: {generated_claim}")
    return generated_claim