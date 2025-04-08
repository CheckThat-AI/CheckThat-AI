import os
import argparse
from together import Together
from typing import Any, Dict, List
import numpy as np
import pandas as pd
import json
from tqdm import tqdm
import nltk
nltk.download('wordnet', quiet=True)
from nltk.tokenize import word_tokenize
from nltk.translate.meteor_score import meteor_score
from pydantic import BaseModel, Field

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=TOGETHER_API_KEY)

class NormalizedClaim(BaseModel):
    title: str = Field(description="A Normalized claim from the input text.")
    claim: str = Field(description="The claim made in the input text.")

def get_claim(model: Any, user_prompt: str) -> str:
    sys_promt = """You are a helpful AI assistant that can extract a claim made in a given text. Always return the claim in English even if the original input is in a different language.
    input:Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC Lieutenant Retired General Asif Mumtaz appointed as Chairman Pakistan Medical Commission PMC None
    claim: Pakistani government appoints former army general to head medical regulatory body
    input: A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed A priceless clip of 1970 of Bruce Lee playing Table Tennis with his Nan-chak !! His focus on speed None
    claim: Late actor and martial artist Bruce Lee playing table tennis with a set of nunchucks.
    input: ▪️Fake snow on texas..
            Haarp used chemtrail snow.
            #OperationDarkWinter ❄️
            #WeatherModification 
            ▪️Fake snow on texas..
            Haarp used chemtrail snow.
            #OperationDarkWinter ❄️
            #WeatherModification 
            ▪️Fake snow on texas..
            Haarp used chemtrail snow.
            #OperationDarkWinter ❄️
            #WeatherModification None
    claim: Video shows snow in Texas is fake
    input: Corona virus before it reaches the lungs it remains in the throat for four days and at this time the person begins to cough and have throat pains. If he drinks water a lot and gargling with warm water & salt or vinegar eliminates the virus. Spread this information because you can save someone with this information
    claim: Gargling water can proect against coronavirus
    """
    inputs = f"{sys_promt}\ninput:{user_prompt}"
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": user_prompt}, {"role": "system", "content": sys_promt}],
        response_format={
            "type": "json_object",
            "schema": NormalizedClaim.model_json_schema(),
        },
    )
    generated_claim = json.loads(response.choices[0].message.content)
    return generated_claim["claim"]

def evaluate_model(model: Any, input_data: Any):
    inf_results: Dict[List, List, List] = {
                                            'scores' : ["METEOR(Nikhil/Llama-3.3-70B-Few-shot-prompt)"],
                                            'responses' : ["Generated Claims"],
                                            'labels' : ["Ground Truth"] 
                                        }
    for index, item in tqdm(input_data.iterrows(), total=len(input_data)):
        response = get_claim(model, item['post'])
        response_tokens = word_tokenize(response)
        label_tokens = word_tokenize(item['normalized claim'])
        inf_results['scores'].append(meteor_score([response_tokens], label_tokens))
        inf_results['responses'].append(response)
        inf_results['labels'].append(item['normalized claim'])
        
    with open("./data/inference_results.csv", "w", encoding="utf-8") as f:
        pd.DataFrame(inf_results).to_csv(f, index=False)
       
    return np.mean(inf_results['scores'][1:])

def main():
    
    file_path: str
    DEV_DATA: pd.DataFrame
        
    file_path = "./data/dev.csv"
    DEV_DATA = pd.read_csv(file_path)
    model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    
    METEROR_SCORE = evaluate_model(model, DEV_DATA[0:200])
    
    print(f"Average METEOR Score: {METEROR_SCORE}")
    
if __name__ == "__main__":
    main()