import os
import json
from typing import Any, Dict, List, Tuple, Optional
from .schema import Feedback
from .get_model_response import get_model_response
from .prompts import sys_prompt, instruction, chain_of_thought_trigger, few_shot_prompt, few_shot_CoT_prompt, feedback_prompt, feedback_sys_prompt, refine_sys_prompt

def format_feedback_for_prompt(feedback: Feedback) -> str:
    """Format feedback into readable text for LLM consumption"""
    formatted_parts = []
    
    criteria = {
        "verifiability": "Verifiability",
        "false_likelihood": "Likelihood of Being False", 
        "public_interest": "Public Interest",
        "potential_harm": "Potential Harm",
        "check_worthiness": "Check-Worthiness"
    }
    
    for field, display_name in criteria.items():
        field_data = getattr(feedback, field)
        if field_data and len(field_data) >= 2:
            score = field_data[0]
            explanation = field_data[1]
            formatted_parts.append(f"**{display_name}:** Score {score}/10 - {explanation}")
    
    return "\n".join(formatted_parts)

def self_refine(models: List[str], user_prompt: str, prompt_styles: List[str], refine_iters: int, cross_refine_model: Optional[str] = None) -> Tuple[str, List[Dict[str, Any]]]:
    """
    This function takes a list of models, a user prompt, and a list of prompt styles,
    and returns the generated response using the first model and prompt style in the lists.
    
    Args:
        models (List[str]): List of model identifiers to use.
        user_prompt (str): The user's input prompt with the task query.
        prompt_styles (List[str]): List of system prompts to guide the model's response.
        self_refine_iters (int): Number of self-refinement iterations.
        cross_refine_model (Optional[str]): The model to use for cross-refinement feedback generation.

    Returns:
        Tuple[str, List[Dict[str, Any]]]: The final refined claim and a list of logs generated during the process.
    """
    # Use the first model and prompt style in the lists
    model = models[0]
    prompt_style = prompt_styles[0]
    
    logs: List[Dict[str, Any]] = []

    if prompt_style == "Zero-shot":
        user_prompt = f"{instruction} {user_prompt}"
    elif prompt_style == "Zero-shot-CoT":
        user_prompt = f"{instruction} {user_prompt}\n{chain_of_thought_trigger}"
    elif prompt_style == "Few-shot":
        user_prompt = f"{few_shot_prompt}\n{instruction} {user_prompt} "
    elif prompt_style == "Few-shot-CoT":
        user_prompt = f"{few_shot_CoT_prompt}\n{instruction}{user_prompt}\n{chain_of_thought_trigger}"
    
    current_claim: str = ""
    feedback_user_prompt: str = ""
    feedback: str = ""
    refine_user_prompt: str = ""
    refined_claim: str = ""
    
    initial_claim = get_model_response(model, user_prompt, sys_prompt, "init")
 
    current_claim = initial_claim.claim
    logs.append({"message": f"Initial Claim: {initial_claim.claim}", "type": "initial_claim"})

    
    for i in range(refine_iters):
        logs.append({"message": f"Self-refine Iteration {i+1} of {refine_iters}", "type": "iteration_start"})
        feedback_user_prompt = f"{user_prompt}\nResponse/Normalized Claim: {current_claim}\n{feedback_prompt}"
    
        # Use cross_refine_model for feedback if provided, otherwise use the main model
        feedback_generation_model = cross_refine_model if cross_refine_model else model
        logs.append({"message": f"Using feedback model: {feedback_generation_model}", "type": "debug_feedback_model"})
        feedback = get_model_response(feedback_generation_model, feedback_user_prompt, feedback_sys_prompt, "feedback")
        
        logs.append({"message": "Feedback: ", "type": "feedback_start"})
        logs.extend([{"message": f"{k}: {v}", "type": "feedback_detail"} for k, v in feedback.model_dump().items()])
        logs.append({"message": "End of Feedback", "type": "feedback_end"})
        
        feedback_text = format_feedback_for_prompt(feedback)
        refine_user_prompt = f"""
            ## Original Query
            {user_prompt}

            ## Current Response  
            {current_claim}

            ## Feedback
            {feedback_text}

            ## Task
            Refine the current response based on the feedback to improve its accuracy, verifiability, and overall quality.
        """
        refined_claim = get_model_response(model, refine_user_prompt, refine_sys_prompt, "refine")
        logs.append({"message": f"Refined Claim: {refined_claim.claim}", "type": "refined_claim"})
        current_claim = refined_claim.claim
        logs.append({"message": f"End of Self-refine Iteration {i+1} of {refine_iters}", "type": "iteration_end"})
        
    logs.append({"message": f"Final Claim: {current_claim}", "type": "final_claim"})
    return current_claim, logs
    
    