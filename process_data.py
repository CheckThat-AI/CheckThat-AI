"""
Author: Nikhil Kadapala
Date: 2-19-2025
Course: CS 881 - Spring 2025, UNH, Durham, USA
Description: This program is used to process the initial dataset and re-format it to match instruction fine-tuning data style.
             This is part of the task2 of the CheckThat! Lab's CLEF 2025 Edition.
"""
from typing import List, Dict, Any
import pandas as pd
import json
import argparse
import os

def read_prompt(path: Any) -> str:
    """
    Read the system prompt from the file and return the prompt as a string.

    Args:
        path (str): path to the file containing the system prompt.
    """
    file_path: str
    if path is None:
        file_path = "./prompt.jsonl"
    else:
        file_path = path
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_object = json.load(file)
            PROMPT = json_object['prompt']
            return PROMPT
    except FileNotFoundError:
        print(f"No file found for the prompt.\nPlease re-launch the program using python3 process_data.py -p path_to_prompt_file")
        exit()
        
def read_data(path: Any) -> pd.DataFrame:
    """
    Read the data from the file and return the data as a pandas DataFrame.

    Args:
        path (str): path to the file containing the data.
    """
    fp: str
    if path is None:
        fp = "./data/train.csv"
    else:
        fp = path
    try:
        data = pd.read_csv(fp)
        return data
    except Exception as e:
        print(f"Error: {e}")
        print(f"No file found for the data.\nPlease re-launch the program using python3 process_data.py -d path_to_data_file")
        exit()
        
def process_data(data: pd.DataFrame, prompt: str) -> Any:
    """
    Process the data to re-format it to match instruction fine-tuning data style.

    Args:
        data (pd.DataFrame): data to be processed.
        prompt (str): system prompt for the fine-tuning data.
    """
    train_examples = []
    output_file = "./data/buffer_data.jsonl"
    with open(output_file, 'w', encoding='utf-8') as f:
        for index, item in data.iterrows():
            json_data = {
                "messages": [
                                {
                                    "content":prompt,
                                    "role": "system"
                                },
                                {
                                    "content": item["post"],
                                    "role": "user"
                                },
                                {
                                    "content": item["normalized claim"],
                                    "role": "assistant"
                                }
                            ]
            }
            try:
                # Validate JSON by encoding and decoding
                json_line = json.dumps(json_data, ensure_ascii=False)
                json.loads(json_line)  # This will raise an error if JSON is invalid
                f.write(json_line + '\n')
            except json.JSONDecodeError as e:
                print(f"Error in line {index + 1}: {e}")
                
    with open(output_file, 'r', encoding='utf-8') as in_file, open("./data/finetune_data.jsonl", 'w', encoding='utf-8') as outfile:
        for line_number, line in enumerate(in_file, 1):
            try:
                # Try to parse the JSON
                json_object = json.loads(line.strip())

                # Write the valid JSON line to the output file
                json.dump(json_object, outfile)
                outfile.write('\n')
            except json.JSONDecodeError as e:
                print(f"Error in line {line_number}: {e}")
    os.remove(output_file)
    return outfile.name

def main():

    # adding a description of the program command to indicate what the command or program is intended to do.
    parser = argparse.ArgumentParser(description="Processing the initial dataset and re-formatting to match instruction fine-tuning data style.")

    # add the option or flag to specify the system prompt for the fine-tuning data and the path to the training data file.
    parser.add_argument("-d", "--data", type=str, help="path to the data in the following format: ./data/train.csv.")
    parser.add_argument("-p", "--prompt", type=str, help="System prompt for the fine-tuning data.")

    # use parse_args() method to parse the command line arguments 
    args = parser.parse_args()
    
    PROMPT: str
    file_path: str
    TRAIN_DATA: pd.DataFrame
    
    if args.prompt is None:
        PROMPT = read_prompt(None)
    else:
        PROMPT = read_prompt(args.prompt)
    
    if args.data is None:
        TRAIN_DATA = read_data(None)
    else:
        TRAIN_DATA = read_data(args.data)
    
    FINETUNE_DATA = process_data(TRAIN_DATA, PROMPT)
    print(f"Fine-tuning data has been created and saved in the file: {FINETUNE_DATA}")

if __name__ == "__main__":
    main()