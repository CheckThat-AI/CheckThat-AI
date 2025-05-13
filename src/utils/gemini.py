import os
from google import genai
from google.genai import types

def get_gemini_response(sys_prompt: str, user_prompt: str, response_format: str, gen_type: str) -> str:
    
    ERROR_MESSAGE = "Exception in Gemini's response: "
    generated_claim: str = "None"
        
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[types.Part.from_text(text=user_prompt)],
                        config=types.GenerateContentConfig(
                            system_instruction=sys_prompt,
                            response_mime_type='application/json',
                            response_schema=response_format
                        ),
                    )
        generated_claim = response.parsed
        
        if gen_type == "init" or gen_type == "refine":
            generated_claim = generated_claim.claim

    except Exception as e:
        print(f"{ERROR_MESSAGE} {e}")
        generated_claim = "None"

    return generated_claim