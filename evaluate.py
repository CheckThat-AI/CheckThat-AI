"""
Author: Nikhil Kadapala
Date: 2-19-2025
Course: CS 881 - Spring 2025, UNH, Durham, USA
Description: This program is used to process the initial dataset and re-format it to match instruction fine-tuning data style.
             This is part of the task2 of the CheckThat! Lab's CLEF 2025 Edition.
"""
import os
import argparse
from together import Together
from typing import Any
import nltk
nltk.download('wordnet', quiet=True)
from nltk.tokenize import word_tokenize
from nltk.translate.meteor_score import meteor_score
import numpy as np
import pandas as pd
from tqdm import tqdm

def get_claim(model_name: str, user_prompt: str) -> str:
    client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        max_tokens=50,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>"],
        stream=False
    )
    return response.choices[0].message.content

def evaluate_model(model_name, input_data, labels):
    scores = []
    for data, label in tqdm(zip(input_data, labels), total=len(input_data)):
        response = get_claim(model_name, data)
        token_res = word_tokenize(response)
        token_label = word_tokenize(label)
        scores.append(meteor_score([token_res], token_label))
    return np.mean(scores)

def main():

    parser = argparse.ArgumentParser(description="Evaluating the fine-tuned model's performance with METEOR Score on the dev set.")
    parser.add_argument("-d", "--data", type=str, help="path to the data in the following format: ./data/dev.csv")
    parser.add_argument("-m", "--model", type=str, help="Fine-tuned Model name.")
    args = parser.parse_args()
    
    file_path: str
    DEV_DATA: pd.DataFrame
    
    if args.data is None:
        file_path = "./data/dev.csv"
    else:
        file_path = args.data
    
    if args.model is None:
        print("Please provide the fine-tuned model name.")
        exit()
    else:
        model_name = args.model
    
    DEV_DATA = pd.read_csv(file_path)
    
    METEROR_SCORE = evaluate_model(model_name, DEV_DATA["post"], DEV_DATA["normalized claim"])
    
    print(f"Average METEOR Score: {METEROR_SCORE}")
    
if __name__ == "__main__":
    main()