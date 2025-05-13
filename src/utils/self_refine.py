import os
import json
from typing import Any, Dict, List
from pydantic import BaseModel
from .get_model_response import get_model_response
from .prompts import sys_prompt, instruction, chain_of_thought_trigger, few_shot_prompt, few_shot_CoT_prompt, feedback_prompt, feedback_sys_prompt, refine_sys_prompt

def self_refine(models: List[str], user_prompt: str, prompt_styles: List[str], self_refine_iters: int) -> str:
    """
    This function takes a list of models, a user prompt, and a list of prompt styles,
    and returns the generated response using the first model and prompt style in the lists.
    
    Args:
        models (List[str]): List of model identifiers to use.
        user_prompt (str): The user's input prompt with the task query.
        prompt_styles (List[str]): List of system prompts to guide the model's response.

    Returns:
        str: The generated response from the model.
    """
    # Use the first model and prompt style in the lists
    model = models[0]
    prompt_style = prompt_styles[0]
    
    if prompt_style == "Zero-shot":
        user_prompt = f"{instruction} {user_prompt}"
    elif prompt_style == "Zero-shot-CoT":
        user_prompt = f"{instruction} {user_prompt}\n{chain_of_thought_trigger}"
    elif prompt_style == "Few-shot":
        user_prompt = f"{few_shot_prompt}\n{instruction} {user_prompt} "
    elif prompt_style == "Few-shot-CoT":
        user_prompt = f"{few_shot_prompt}\n{instruction}{user_prompt}\n{chain_of_thought_trigger}"
    
    current_claim: str = ""
    feedback_user_prompt: str = ""
    feedback: str = ""
    refine_user_prompt: str = ""
    refined_claim: str = ""
    
    initial_claim = get_model_response(model, user_prompt, sys_prompt, "init")
    #print(f"\n\nInitial Claim: {initial_claim}")
    
    current_claim = initial_claim

    
    for _ in range(self_refine_iters):
        #print(f"\n-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ Self-refine Iteration {i+1} of {self_refine_iters} -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
        feedback_user_prompt = f"{user_prompt}\nResponse/Normalized Claim: {current_claim}\n{feedback_prompt}"
    
        feedback = get_model_response(model, feedback_user_prompt, feedback_sys_prompt, "feedback")
        
        #print(f"\n=========================== Feedback ==================================")

        #print('\n'.join(f"{k}: {v}" for k, v in feedback.model_dump().items())) if isinstance(feedback, BaseModel) else print(f"\nFeedback: {feedback}")
        
        feedback = str(feedback.model_dump()) if isinstance(feedback, BaseModel) else feedback
        #print(f"\n======================= End of Feedback ===============================")
        refine_user_prompt = f"<|user_query|>{user_prompt}<|end_of_user_query|><|assistant_response|>{current_claim}<|end_of_assistant_response|><|feedback|>{feedback}<|end_of_feedback|><|instruction|>Based on the feedback provided, please refine the above generated response/normalized claim.<|end_of_instruction|>"
    
        refined_claim = get_model_response(model, refine_user_prompt, refine_sys_prompt, "refine")
        #print(f"\nRefined Claim: {refined_claim}\n")
        current_claim = refined_claim
        #print(f"-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ End of Self-refine Iteration {i+1} of {self_refine_iters} -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-\n")
    
    return current_claim
    
    