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

def uploadfile(filepath:Any):
    file_name: str
    if filepath is None:
        file_name = "./data/finetune_data.jsonl"
    else:
        file_name = filepath
    try:
        client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
        file_resp = client.files.upload(file=file_name, check=True)
        return file_resp.model_dump()

    except Exception as e:
        print(f"Error: {e}")
        if e is FileNotFoundError:
            print(f"No file found for the data.\nPlease re-launch the program using python3 process_data.py -d path_to_data_file")
        exit()
        
def main():
    parser = argparse.ArgumentParser(description="Uploading the dataset file to together.ai fine-tuning data Queue.")
    parser.add_argument("-d", "--data", type=str, help="path to the data in the following format: ./data/finetune_data.jsonl.")
    args = parser.parse_args()
    upload_response: Any
    if args.data is None:
        upload_response = uploadfile(None)
    else:
        upload_response = uploadfile(args.data)
        
    print(f"File upload response:\n{upload_response}")

if __name__ == "__main__":
    main()