from utils.evaluate import start_evaluation
import pandas as pd
import argparse
import os

def main():
    
    parser = argparse.ArgumentParser(
        description="""Evaluating the chosen model's performance with METEOR Score on the data set.
        Accepted model names: Llama, OpenAI, Gemini, Grok.
        Accepted prompt styles: Zero-shot, Few-shot, Zero-shot-CoT, Few-shot-CoT.
        Accepted self-refine iterations: Integer values only.
        Accepted data file format: CSV file only.
        Note: If no arguments are provided, default values will be used."""
    )
    parser.add_argument("-p", "--prompt", nargs='*', type=str, help="Prompt style.")
    parser.add_argument("-d", "--data", type=str, help="Path to the CSV file containing the dev set.")
    parser.add_argument("-m", "--model", nargs='*', type=str, help="Model name.")
    parser.add_argument("-it", "--iters", type=str, help="Number of self-refine iterations.")
    args = parser.parse_args()

    
    FILE_PATH: str
    DEV_DATA: pd.DataFrame
    MODEL: str
    PROMPT: str
    SR_ITERATIONS: int
    
    
    PROMPT_STYLE = args.prompt if args.prompt else "Zero-shot"    
    MODEL = args.model if args.model else "Llama"
    SR_ITERATIONS: int = int(args.iters) if args.iters else 0
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = args.data if args.data else os.path.join(os.path.dirname(current_dir), "data", "dev.csv")
    if not os.path.exists(FILE_PATH):
        print(f"Error: Data file not found at '{FILE_PATH}'")
        print("Please specify the correct path using the -d parameter")
        return
    
    DEV_DATA = pd.read_csv(FILE_PATH)

    METEOR_SCORE = start_evaluation(MODEL, PROMPT_STYLE, DEV_DATA, SR_ITERATIONS)
    
    print(f"\nAverage METEOR Score: {METEOR_SCORE}")
    
if __name__ == "__main__":
    main()