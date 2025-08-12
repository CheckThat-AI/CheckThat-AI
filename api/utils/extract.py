import os
import json
import pandas as pd
from tqdm import tqdm
from typing import Any, Dict, List, Tuple, Optional, Union
import re
import logging

from .self_refine import self_refine

logger = logging.getLogger(__name__)

def clean_filename(text: str) -> str:
    """Convert text to a valid filename by removing invalid characters"""
    return re.sub(r'[\\/*?:"<>|]', "_", text)

def start_extraction(model: str, prompt_style: str, input_data: pd.DataFrame, refine_iters: int, cross_refine_model: Optional[str] = None, progress_callback=None, stop_event=None, custom_prompt: Optional[str] = None, session_id: Optional[str] = None) -> Union[Tuple[str, List[str], List[str]], bool]:
    """
    Perform claim extraction on the given data using specified model and prompt style.
    
    Args:
        model: The model to use for extraction
        prompt_style: The prompting strategy to use
        input_data: DataFrame containing the posts to process
        refine_iters: Number of self-refinement iterations
        cross_refine_model: Optional model for cross-refinement
        progress_callback: Optional callback for progress updates
        stop_event: Optional event to signal stopping
        custom_prompt: Optional custom prompt to use instead of predefined styles
        session_id: Optional session ID for multi-user support
        
    Returns:
        Tuple of (file_path, extracted_claims, reference_claims) on success, False on failure/stop
    """
    try:
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
        
        combo_key = f"{clean_filename(model)}_{clean_filename(prompt_style)}"
        
        results_by_combination[combo_key] = {
            'input': [],
            'actual_output': [],
            'context': [],
            'retrieval_context': [],
            'model': [],
            'prompt_style': [],
            'session_id': []  # Add session_id column for multi-user support
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
        
        for index, item in tqdm(input_data.iterrows(), total=len(input_data), desc="Extracting claims"):
            # Increment the counter at the beginning of each iteration
            processed_count += 1
            
            # Check for stop signal
            if stop_event and stop_event.is_set():
                print("Evaluation stopped by user")
                if progress_callback:
                    progress_callback("status", {"message": "Evaluation stopped by user"})
                return False
            
            # Check for empty/invalid data more safely
            post_empty = str(item['post']).strip() == ""
            
            # Handle reference claims (normalized claim column may not exist)
            normalized_claim = None
            claim_invalid = True  # Default to invalid if no reference claims
            
            if 'normalized claim' in input_data.columns:
                normalized_claim = item['normalized claim']
                # Check if normalized claim is invalid (NaN, None, empty string, etc.)
                try:
                    if pd.isna(normalized_claim) or str(normalized_claim).strip() in ["", "nan", "NaN", "None"]:
                        claim_invalid = True
                    else:
                        claim_invalid = False
                except Exception:
                    claim_invalid = True
            else:
                # No reference claims available - this is valid for referenceless metrics
                normalized_claim = item['post']  # Use post as placeholder for reference
                claim_invalid = False  # Not invalid, just no reference available
                print(f"No reference claims column found - dataset suitable for referenceless metrics only")
            
            # Construct the user prompt based on prompt style or use custom prompt
            if custom_prompt:
                # For custom prompts, use the custom prompt with the post content
                # The custom prompt should include {post} placeholder or similar
                if "{post}" in custom_prompt:
                    user_input = custom_prompt.replace("{post}", str(item['post']))
                elif "{input}" in custom_prompt:
                    user_input = custom_prompt.replace("{input}", str(item['post']))
                else:
                    # If no placeholder, append the post to the custom prompt
                    user_input = f"{custom_prompt} {item['post']}"
            else:
                # Use default prompt styles
                from .prompts import instruction, chain_of_thought_trigger, few_shot_prompt, few_shot_CoT_prompt
                
                if prompt_style == "Zero-shot":
                    user_input = f"{instruction} {item['post']}"
                elif prompt_style == "Zero-shot-CoT":
                    user_input = f"{instruction} {item['post']}\n{chain_of_thought_trigger}"
                elif prompt_style == "Few-shot":
                    user_input = f"{few_shot_prompt}\n{instruction} {item['post']} "
                elif prompt_style == "Few-shot-CoT":
                    user_input = f"{few_shot_CoT_prompt}\n{instruction}{item['post']}\n{chain_of_thought_trigger}"
                else:
                    user_input = f"{instruction} {item['post']}"  # Fallback to zero-shot
            
            if post_empty:
                print(f"Skipping item with empty post: {item['post']}")
                results_by_combination[combo_key]['input'].append(user_input)
                results_by_combination[combo_key]['actual_output'].append("No output - empty post")
                results_by_combination[combo_key]['context'].append(str(item['post']))
                results_by_combination[combo_key]['retrieval_context'].append(str(item['post']))
                results_by_combination[combo_key]['model'].append(model)
                results_by_combination[combo_key]['prompt_style'].append(prompt_style)
                results_by_combination[combo_key]['session_id'].append(session_id or "unknown")
            elif claim_invalid and 'normalized claim' in input_data.columns:
                # Only skip if we have reference claims column but the claim is invalid
                print(f"Skipping item with invalid reference claim: {item['post']} and {normalized_claim}")
                results_by_combination[combo_key]['input'].append(user_input)
                results_by_combination[combo_key]['actual_output'].append("No output - invalid reference claim")
                results_by_combination[combo_key]['context'].append(str(item['post']))
                results_by_combination[combo_key]['retrieval_context'].append(str(item['post']))
                results_by_combination[combo_key]['model'].append(model)
                results_by_combination[combo_key]['prompt_style'].append(prompt_style)
                results_by_combination[combo_key]['session_id'].append(session_id or "unknown")
            else:
                if progress_callback:
                    progress_callback("log", {"message": f"Processing item {processed_count}/{total_items}: {item['post'][:50]}...", "model": model, "prompt_style": prompt_style, "type": "item_processed"})
                
                # Pass the custom prompt to self_refine if available
                if custom_prompt:
                    response_text, logs_from_self_refine = self_refine(model, item['post'], "Custom", refine_iters, cross_refine_model, custom_prompt)
                else:
                    response_text, logs_from_self_refine = self_refine(model, item['post'], prompt_style, refine_iters, cross_refine_model)

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

                results_by_combination[combo_key]['input'].append(user_input)
                results_by_combination[combo_key]['actual_output'].append(response_text)
                results_by_combination[combo_key]['context'].append(str(item['post']))
                results_by_combination[combo_key]['retrieval_context'].append(str(item['post']))
                results_by_combination[combo_key]['model'].append(model)
                results_by_combination[combo_key]['prompt_style'].append(prompt_style)
                results_by_combination[combo_key]['session_id'].append(session_id or "unknown")
            
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
        
        # Calculate the path to data directory from api/utils/
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), "data")
        
        # Save results for each combination in separate files
        for combo_key, results in results_by_combination.items():
            output_path = f"{results_dir}/inference_results_{combo_key}.csv"
            pd.DataFrame(results).to_csv(output_path, index=False)

            # Save basic extraction info without scores
            new_data = {
                'model': model,
                'prompt_style': prompt_style,
                'total_processed': len(results['actual_output']),
            }

            extraction_log_path = os.path.join(data_dir, "results", "extraction_log.jsonl")
            with open(extraction_log_path, "a") as file:
                json_line = json.dumps(new_data)
                file.write(json_line + "\n")
        
        # Save combined results
        combined_results = {
            'input': [],
            'actual_output': [],
            'context': [],
            'retrieval_context': [],
            'model': [],
            'prompt_style': [],
            'session_id': []
        }
        
        for results in results_by_combination.values():
            for key in combined_results:
                combined_results[key].extend(results[key])
        
        combined_results_path = os.path.join(data_dir, "inference_results.csv")
        pd.DataFrame(combined_results).to_csv(combined_results_path, index=False)
        
        # Also save session-specific combined results if session_id is provided
        if session_id:
            session_results_path = os.path.join(data_dir, f"inference_results_{session_id}.csv")
            pd.DataFrame(combined_results).to_csv(session_results_path, index=False)
            logger.info(f"Saved session-specific results to: {session_results_path}")
            
            # Also save session-specific files in results directory
            for combo_key, results in results_by_combination.items():
                session_combo_path = os.path.join(results_dir, f"inference_results_{session_id}_{combo_key}.csv")
                pd.DataFrame(results).to_csv(session_combo_path, index=False)
                logger.info(f"Saved session-specific combo results to: {session_combo_path}")
        
        # Extract claims for return (maintain backward compatibility with existing code)
        extracted_claims = combined_results['actual_output']
        # For faithfulness evaluation, reference_claims should always be the original posts
        # not the normalized claims, since we need the full social media post as context
        reference_claims = [item['post'] for _, item in input_data.iterrows()]
        
        # Return tuple of (file_path, extracted_claims, reference_claims) on success
        return (combined_results_path, extracted_claims, reference_claims)
        
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
        if progress_callback:
            progress_callback("status", {"message": f"Error during evaluation: {str(e)}"})
        return False