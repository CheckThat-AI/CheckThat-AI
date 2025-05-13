import os
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Any, Dict, List, Tuple
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import re

import nltk
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
from nltk.corpus import wordnet
wordnet.ensure_loaded()
from nltk.tokenize import word_tokenize
from nltk.translate.meteor_score import meteor_score

from .self_refine import self_refine

def clean_filename(text: str) -> str:
    """Convert text to a valid filename by removing invalid characters"""
    return re.sub(r'[\\/*?:"<>|]', "_", text)

def process_item(args: Tuple[str, str, pd.Series, int]) -> Tuple[float, str, str, str, str]:
    """
    Process a single item with specific model and prompt style
    Returns score, response, label, model and prompt_style as a tuple
    """
    model, prompt_style, item, self_refine_iters = args
    if item['post'] == "" or np.isnan(item['normalized claim']):
        print(f"Skipping item: {item['post']} and {item['normalized claim']}")
        return (0.0, "", "", model, prompt_style)
    print(f"Processing item: {item['post']} and {item['normalized claim']}")
    response = self_refine([model], item['post'], [prompt_style], self_refine_iters)
    response_tokens = word_tokenize(response)
    label_tokens = word_tokenize(item['normalized claim'])
    score = meteor_score([response_tokens], label_tokens)
    return (score, response, item['normalized claim'], model, prompt_style)

def start_evaluation(models: List[str], prompt_styles: List[str], input_data: pd.DataFrame, self_refine_iters: int) -> Dict[str, float]:
    # Dictionary to store results by model and prompt style
    results_by_combination: Dict[str, Dict[str, List]] = {}
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(os.path.dirname(current_dir), "data", "results")
    # Create output directory if it doesn't exist
    os.makedirs(results_dir, exist_ok=True)
    
    # Check if we need to use multi-threading
    use_threading = len(models) > 1 or len(prompt_styles) > 1
    
    if use_threading:
        print(f"Using threading for {len(models)} models: {models} and {len(prompt_styles)} prompt styles: {prompt_styles}")
        # Create all combinations of models, and prompt_styles
        combinations = []
        for model, prompt_style in product(models, prompt_styles):
            for _, item in input_data.iterrows():
                combinations.append((model, prompt_style, item, self_refine_iters))
        
        with ProcessPoolExecutor(max_workers=min(12, len(combinations))) as executor:
            results = list(tqdm(
                executor.map(process_item, combinations),
                total=len(combinations),
                desc="Processing with multiple threads"
            ))
            
        # Organize results by model and prompt style combination
        for score, response, label, model, prompt_style in results:
            combo_key = f"{clean_filename(model)}_{clean_filename(prompt_style)}"
            
            if combo_key not in results_by_combination:
                results_by_combination[combo_key] = {
                    'scores': [],
                    'responses': [],
                    'labels': [],
                    'model': [],
                    'prompt_style': []
                }
                
            results_by_combination[combo_key]['scores'].append(score)
            results_by_combination[combo_key]['responses'].append(response)
            results_by_combination[combo_key]['labels'].append(label)
            results_by_combination[combo_key]['model'].append(model)
            results_by_combination[combo_key]['prompt_style'].append(prompt_style)
    else:
        model = models[0] if models else ""
        prompt_style = prompt_styles[0] if prompt_styles else ""
        combo_key = f"{clean_filename(model)}_{clean_filename(prompt_style)}"
        
        results_by_combination[combo_key] = {
            'scores': [],
            'responses': [],
            'labels': [],
            'model': [],
            'prompt_style': []
        }
        
        for index, item in tqdm(input_data.iterrows(), total=len(input_data), desc="Extracting claims and evaluating with METEOR"):
            if item['post'] == "" or (isinstance(item['normalized claim'], float) and np.isnan(item['normalized claim'])):
                print(f"Skipping item: {item['post']} and {item['normalized claim']}")
                results_by_combination[combo_key]['scores'].append(0.0)
                results_by_combination[combo_key]['responses'].append(item['post'])
                results_by_combination[combo_key]['labels'].append(item['post'])
                results_by_combination[combo_key]['model'].append(model)
                results_by_combination[combo_key]['prompt_style'].append(prompt_style)
            else:
                response = self_refine(models, item['post'], prompt_styles, self_refine_iters)
                response_tokens = word_tokenize(response)
                label_tokens = word_tokenize(item['normalized claim'])
                score = meteor_score([response_tokens], label_tokens)
                
                results_by_combination[combo_key]['scores'].append(score)
                results_by_combination[combo_key]['responses'].append(response)
                results_by_combination[combo_key]['labels'].append(item['normalized claim'])
                results_by_combination[combo_key]['model'].append(model)
                results_by_combination[combo_key]['prompt_style'].append(prompt_style)
    
    # Dictionary to store the average score for each combination
    combination_scores = {}
    
    # Save results for each combination in separate files
    for combo_key, results in results_by_combination.items():
        output_path = f"{results_dir}/inference_results_{combo_key}.csv"

        pd.DataFrame(results).to_csv(output_path, index=False)

        avg_score = np.mean(results['scores'])
        combination_scores[combo_key] = avg_score
        new_data = {
            'model': model,
            'prompt_style': prompt_style,
            'meteor_score': avg_score,
        }

        with open("./data/results/scores.jsonl", "a") as file:
            json_line = json.dumps(new_data)
            file.write(json_line + "\n")
    
    # Save combined results
    combined_results = {
        'scores': [],
        'responses': [],
        'labels': [],
        'model': [],
        'prompt_style': []
    }
    
    for results in results_by_combination.values():
        for key in combined_results:
            combined_results[key].extend(results[key])
    
    pd.DataFrame(combined_results).to_csv("./data/inference_results.csv", index=False)
    #print("\nCombined results saved to ./data/inference_results.csv")
    
    # Return a dictionary containing the average score for each combination
    return combination_scores