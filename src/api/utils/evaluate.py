import os
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Any, Dict, List, Tuple, Optional
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

def start_evaluation(models: List[str], prompt_styles: List[str], input_data: pd.DataFrame, refine_iters: int, progress_callback=None, stop_event=None, cross_refine_model: Optional[str] = None) -> Dict[str, float]:
    # Dictionary to store results by model and prompt style
    results_by_combination: Dict[str, Dict[str, List]] = {}
    
    # Update path to correctly point to data directory from api/utils/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up from utils -> api -> src -> root, then down to data/results
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), "data", "results")
    # Create output directory if it doesn't exist
    os.makedirs(results_dir, exist_ok=True)
    
    # Track progress per combination
    total_items_per_combo: Dict[str, int] = {}
    completed_items_per_combo: Dict[str, int] = {}
    last_reported_progress: Dict[str, int] = {}
    
    # Since frontend only allows one model and one prompt style
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
    
    total_items = len(input_data)
    if progress_callback:
        progress_callback("status", {"message": f"Processing {total_items} items...", "progress": 0})
    
    # Initialize total items per combo (single combo)
    combo_key_single = f"{clean_filename(model)}_{clean_filename(prompt_style)}"
    total_items_per_combo[combo_key_single] = total_items
    completed_items_per_combo[combo_key_single] = 0
    last_reported_progress[combo_key_single] = -1 # Use -1 to ensure first report at 0%

    # Use a proper counter instead of relying on pandas index
    processed_count = 0
    
    for index, item in tqdm(input_data.iterrows(), total=len(input_data), desc="Extracting claims and evaluating with METEOR"):
        # Increment the counter at the beginning of each iteration
        processed_count += 1
        
        # Check for stop signal
        if stop_event and stop_event.is_set():
            print("Evaluation stopped by user")
            if progress_callback:
                progress_callback("status", {"message": "Evaluation stopped by user"})
            return {}
        
        # Check for empty/invalid data more safely
        post_empty = str(item['post']).strip() == ""
        normalized_claim = item['normalized claim']
        
        # Check if normalized claim is invalid (NaN, None, empty string, etc.)
        claim_invalid = False
        try:
            if pd.isna(normalized_claim) or str(normalized_claim).strip() in ["", "nan", "NaN", "None"]:
                claim_invalid = True
        except Exception:
            claim_invalid = True
        
        if post_empty or claim_invalid:
            print(f"Skipping item: {item['post']} and {item['normalized claim']}")
            results_by_combination[combo_key]['scores'].append(0.0)
            results_by_combination[combo_key]['responses'].append(str(item['post']))
            results_by_combination[combo_key]['labels'].append(str(item['post']))
            results_by_combination[combo_key]['model'].append(model)
            results_by_combination[combo_key]['prompt_style'].append(prompt_style)
        else:
            if progress_callback:
                progress_callback("log", {"message": f"Processing item {processed_count}/{total_items}: {item['post'][:50]}...", "model": model, "prompt_style": prompt_style, "type": "item_processed"})
            
            response_text, logs_from_self_refine = self_refine(models, item['post'], prompt_styles, refine_iters, cross_refine_model)

            # Send only important logs from self_refine to reduce WebSocket overhead
            if progress_callback and logs_from_self_refine:
                important_log_types = ["initial_claim", "final_claim", "item_error", "debug_feedback_model"]
                for log_entry in logs_from_self_refine:
                    log_type = log_entry.get("type", "")
                    # Only send important logs to client, but print all logs to server console
                    if log_type in important_log_types:
                        try:
                            progress_callback("log", log_entry)
                        except Exception as e:
                            print(f"Error in progress callback for log entry from self_refine: {e}")
                    # Always print to server console for debugging
                    # print(f"[SELF_REFINE] {log_entry.get('message', '')}")

            response_tokens = word_tokenize(response_text)
            label_tokens = word_tokenize(str(normalized_claim))
            score = meteor_score([response_tokens], label_tokens)
            
            results_by_combination[combo_key]['scores'].append(score)
            results_by_combination[combo_key]['responses'].append(response_text)
            results_by_combination[combo_key]['labels'].append(str(normalized_claim))
            results_by_combination[combo_key]['model'].append(model)
            results_by_combination[combo_key]['prompt_style'].append(prompt_style)
        
        # Update per-combination progress and send log if changed significantly
        combo_key_current = f"{clean_filename(model)}_{clean_filename(prompt_style)}"
        completed_items_per_combo[combo_key_current] += 1
        
        # Calculate progress percentage once and use it for both UI and logs
        progress_percentage = round((processed_count / total_items) * 100, 1)
        current_combo_percentage = int(progress_percentage)  # Convert to int for comparison
        
        if current_combo_percentage > last_reported_progress[combo_key_current]:
            if progress_callback:
                try:
                    progress_callback("log", {
                        "message": f"Progress: {progress_percentage}%",
                        "model": model,
                        "prompt_style": prompt_style,
                        "type": "combo_progress"
                    })
                except Exception as e:
                    print(f"Error in progress callback for combo progress: {e}")
            last_reported_progress[combo_key_current] = current_combo_percentage
         
        # Send overall progress update using the same calculation as tqdm
        if progress_callback:
            try:
                # Use the same progress_percentage calculated above
                progress_callback("progress", {
                    "current": processed_count, 
                    "total": total_items, 
                    "percentage": progress_percentage
                })
            except Exception as e:
                print(f"Error in progress callback: {e}")
    
    # Dictionary to store the average score for each combination
    combination_scores = {}
    
    # Calculate the path to data directory from api/utils/
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), "data")
    
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

        scores_file_path = os.path.join(data_dir, "results", "scores.jsonl")
        with open(scores_file_path, "a") as file:
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
    
    combined_results_path = os.path.join(data_dir, "inference_results.csv")
    pd.DataFrame(combined_results).to_csv(combined_results_path, index=False)
    #print(f"\nCombined results saved to {combined_results_path}")
    
    # Return a dictionary containing the average score for each combination
    return combination_scores