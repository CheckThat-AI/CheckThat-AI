"""
Claim Refinement Service

This module provides claim refinement functionality using DeepEval metrics
and custom model integration for quality assessment and improvement.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

from api._utils.openai import OpenAIModel
from api._utils.gemini import GeminiModel
from api._utils.xai import xAIModel
from api._utils.anthropic import AnthropicModel
from api._utils.togetherAI import TogetherModel
 
from ..._utils.prompts import feedback_sys_prompt, refine_sys_prompt, instruction
from ..._utils.deepeval_model import DeepEvalModel
from ...types.completions import RefinementMetadata, RefinementHistory, ClaimType
from ...types.evals import STATIC_EVAL_SPECS

from deepeval import evaluate
from deepeval.metrics import GEval, BaseMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.tracing import observe
from deepeval.models import GPTModel, GeminiModel, AnthropicModel, GrokModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RefinementService:
    def __init__(
        self, 
        model: Union[GPTModel, GeminiModel, AnthropicModel, GrokModel], 
        threshold: float = 0.5,
        max_iters: int = 3,
        metrics: Optional[List[str]] = None,
    ):
        self.model = model
        self.threshold = threshold
        self.max_iters = max_iters
        self.metrics = metrics
        self.logger = logging.getLogger(__name__)
        
        self.feedback_sys_prompt = feedback_sys_prompt
        self.refine_sys_prompt = refine_sys_prompt

    def refine_single_claim(
        self,
        original_query: str,
        current_claim: str,
        client: Union[OpenAIModel, GeminiModel, xAIModel, AnthropicModel, TogetherModel],
        original_response: Optional[Any] = None,
    ) -> Tuple[Any, List[RefinementHistory]]:
        from ...types.completions import RefinementHistory, ClaimType
        
        refinement_history = []
        current_response = original_response
        
        try:
            if self.metrics is None:
                eval_metric = GEval(
                    name="Claim Quality Assessment",
                    criteria=STATIC_EVAL_SPECS.criteria,
                    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
                    model=self.model,
                    threshold=self.threshold
                )
            else:
                eval_metric = self.metrics
                eval_metric.model = self.model
                eval_metric.threshold = self.threshold
                
            # Track the original claim
            test_case = LLMTestCase(
                input=original_query,
                actual_output=current_claim,
            )
            
            eval_result = evaluate(test_cases=[test_case], metrics=[eval_metric])
            original_score = eval_result.test_results[0].metrics_data[0].score
            original_feedback = eval_result.test_results[0].metrics_data[0].reason
            
            refinement_history.append(RefinementHistory(
                claim_type=ClaimType.ORIGINAL,
                claim=current_claim,
                score=original_score,
                feedback=original_feedback
            ))
            
            # If original claim meets threshold, return it
            if original_score >= self.threshold:
                return current_response, refinement_history
            
            # Iterate through refinements
            for i in range(self.max_iters):
                refine_user_prompt = f"""
                ## Original Query
                {original_query}

                ## Current Response  
                {current_claim}

                ## Feedback
                {eval_result.test_results[0].metrics_data[0].reason}

                ## Task
                Refine the current response based on the feedback to improve its accuracy, verifiability, and overall quality.
                """
                logger.debug(f"🔧 Refinement - Calling client.generate_response with prompt length: {len(refine_user_prompt)}")
                logger.debug(f"🔧 Refinement - System prompt length: {len(self.refine_sys_prompt)}")
                
                refined_response = client.generate_response(user_prompt=refine_user_prompt, sys_prompt=self.refine_sys_prompt)
                refined_claim = refined_response.choices[0].message.content
                
                # Update current state
                current_claim = refined_claim
                current_response = refined_response
                
                # Evaluate the refined claim
                test_case = LLMTestCase(
                    input=original_query,
                    actual_output=refined_claim,
                )
                eval_result = evaluate(test_cases=[test_case], metrics=[eval_metric])
                score = eval_result.test_results[0].metrics_data[0].score
                feedback_text = eval_result.test_results[0].metrics_data[0].reason
                
                # Track this refinement iteration
                refinement_history.append(RefinementHistory(
                    claim_type=ClaimType.REFINED,
                    claim=refined_claim,
                    score=score,
                    feedback=feedback_text
                ))
                
                # Check if threshold is met
                if score >= self.threshold:
                    break
                    
            # Mark the final claim
            if refinement_history:
                final_history_entry = refinement_history[-1]
                final_history_entry.claim_type = ClaimType.FINAL
            
            return current_response, refinement_history
            
        except Exception as e:
            logger.warning(f"Failed to refine claim: {e}")
            # Return original response with error in history if refinement fails
            error_history = RefinementHistory(
                claim_type=ClaimType.FINAL,
                claim=current_claim,
                score=0.0,
                feedback=f"Refinement failed: {str(e)}"
            )
            if not refinement_history:
                refinement_history = [error_history]
            else:
                refinement_history.append(error_history)
            return current_response or original_response, refinement_history