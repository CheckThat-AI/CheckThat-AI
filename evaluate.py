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
import json
from tqdm import tqdm
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def get_claim(model: Any, tokenizer: Any, user_prompt: str) -> str:
    sys_promt = """You are a helpful AI assistant that can generate a summary of claims made in a given text in the style of a news headline.
    Based on the input text, extract a claim that is being made or implied and return it as a json object."""
    inputs = tokenizer(f"{sys_promt}\ninput_text:{user_prompt}", return_tensors="pt").to('cuda')
    outputs = model.generate(
        **inputs,
        max_new_tokens=30,
        pad_token_id=tokenizer.eos_token_id,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        do_sample=True, 
        top_k=50,
        top_p=0.95,
        temperature=0.3
    )
    generated_claim = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    torch.cuda.empty_cache()
    return generated_claim

def evaluate_model(model: Any, tokenizer: Any, input_data: Any):
    scores = []
    responses = []
    for index, item in tqdm(input_data.iterrows(), total=len(input_data)):
        response = get_claim(model, tokenizer, item['post'])
        #print(f"Response: {response}")
        token_res = word_tokenize(response)
        token_label = word_tokenize(item['normalized claim'])
        scores.append(meteor_score([token_res], token_label))
        responses.append(response)
    with open("generated_claims_dev.jsonl", "w") as f:
        json.dump(responses,f, ensure_ascii=False)
        
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
    
    DEV_DATA = pd.read_csv(file_path)
    
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("CUDA version:", torch.version.cuda)
        print("Device name:", torch.cuda.get_device_name(0))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    base_model_path = "./meta-llama/Meta-Llama-3.1-8B-Instruct"  # Local directory of the base model
    lora_adapter_path = "./lora-adapters"  # Path to your LoRA adapters

    tokenizer = AutoTokenizer.from_pretrained(base_model_path, local_files_only=True)

    if tokenizer.pad_token is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
        tokenizer.pad_token = tokenizer.eos_token


    model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        local_files_only=True,
        torch_dtype=torch.float16,
        device_map="auto" 
    )
    model.config.pad_token_id = tokenizer.pad_token_id
    model = PeftModel.from_pretrained(model, lora_adapter_path, is_trainable=False)
    model = model.to(device)
    
    METEROR_SCORE = evaluate_model(model, tokenizer, DEV_DATA)
    
    print(f"Average METEOR Score: {METEROR_SCORE}")
    
if __name__ == "__main__":
    main()