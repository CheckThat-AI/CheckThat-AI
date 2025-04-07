"""
Author: Nikhil Kadapala
Date: 2-19-2025
Course: CS 881 - Spring 2025, UNH, Durham, USA
Description: This program is used to process the initial dataset and re-format it to match instruction fine-tuning data style.
             This is part of the task2 of the CheckThat! Lab's CLEF 2025 Edition.
"""
import os
from together import Together
from typing import Any
import argparse
import subprocess
import time

try:
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
except Exception as e:
    print(f"Error: {e}")
    exit()

try:
    WANDB_API_KEY = os.getenv("WANDB_API_KEY")
except Exception as e:
    print(f"Error: {e}")
    exit()

def create_finetune_job(model_name:str, file_id: str, model_suffix: Any):
    suffix: str
    client = Together(api_key = TOGETHER_API_KEY)
    if model_suffix is None:
        suffix = 'my-demo-finetune'
    else:
        suffix = model_suffix
    response = client.fine_tuning.create(
    training_file = file_id,
    model = model_name,
    lora = True,
    lora_r = 16,
    lora_alpha = 32,
    lora_dropout = 0.5,
    n_epochs = 1,
    n_checkpoints = 1,
    batch_size = "max",
    learning_rate = 2e-5,
    suffix = suffix,
    wandb_api_key = WANDB_API_KEY,
    )

    return response
    
def main():
    parser = argparse.ArgumentParser(description="Evaluating the fine-tuned model's performance with METEOR Score on the dev set.")
    parser.add_argument("-f", "--fileID", type=str, help="file-id of the file uploaded to together.ai")
    parser.add_argument("-m", "--model", type=str, help="Fine-tuned Model name.")
    args = parser.parse_args()
    
    finetune_response: Any
    FILE_ID: str
    MODEL: str
    SUFFIX: str
    
    if args.fileID is None:
        print("Please provide the fiLe-id. It looks something like this: file-5e32a8e6-72b3-485d-ab76-71a73d9e1f5b")
        exit()
    else:
        FILE_ID = args.fileID
    
    if args.model is None:
        print("Please provide the model name to fine-tune.")
        exit()
    else:
        MODEL = args.model
        
    suffix = input("Please provide the model suffix or press enter to use the default suffix: ").strip()
    
    if suffix != "":
        SUFFIX = suffix
    else:
        SUFFIX = None
        
    finetune_response = create_finetune_job(MODEL, FILE_ID, SUFFIX)
    print(f"Fine-tuning job creation request response:\n{finetune_response}")
    ft_id = finetune_response.id
    while True:
        process = subprocess.Popen(['together', 'fine-tuning', 'list-events', ft_id], stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate()
        print(output)
        if "Job finished" in output:
            break
        time.sleep(60)

if __name__ == "__main__":
    main()
    
