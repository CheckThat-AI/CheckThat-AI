"""
Claim Evaluation Service

This module provides claim evaluation functionality using DeepEval metrics
for quality assessment and scoring.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Import your existing model classes
from ..._utils.deepeval_model import DeepEvalModel
from ...types.completions import EvaluationReport

# DeepEval imports
from deepeval.metrics import GEval, BaseMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.tracing import observe

logger = logging.getLogger(__name__)


def create_evaluation_metrics(
    metric_types: List[str], 
    deepeval_model: Any
) -> Dict[str, GEval]:
    """
    Create G-Eval metrics based on requested evaluation types.
    
    Args:
        metric_types: List of metric names to create
        deepeval_model: DeepEval model instance
        
    Returns:
        Dictionary of metric_name -> GEval instance
    """
    metric_definitions = {
        "verifiability": {
            "name": "Verifiability Assessment",
            "criteria": "Evaluate how easily this claim can be verified using reliable sources",
            "evaluation_steps": [
                "Check if the claim contains specific, factual assertions",
                "Assess whether evidence can be found to support or refute the claim",
                "Consider if the claim is time-sensitive or location-specific",
                "Determine if the claim requires expert knowledge to verify"
            ]
        },
        "check_worthiness": {
            "name": "Check-Worthiness Assessment", 
            "criteria": "Evaluate the importance and urgency of fact-checking this claim",
            "evaluation_steps": [
                "Assess potential harm if the claim is false",
                "Consider the claim's reach and influence potential",
                "Evaluate public interest in the claim's veracity",
                "Determine if the claim could mislead vulnerable populations"
            ]
        },
        "factual_consistency": {
            "name": "Factual Consistency Assessment",
            "criteria": "Evaluate if the claim accurately represents facts without distortion",
            "evaluation_steps": [
                "Check if the claim introduces new information not in the source",
                "Verify the claim doesn't misrepresent the original context",
                "Ensure the claim maintains factual accuracy",
                "Confirm the claim doesn't contain hallucinations"
            ]
        },
        "clarity": {
            "name": "Clarity Assessment",
            "criteria": "Evaluate how clear and understandable the claim is",
            "evaluation_steps": [
                "Check if the claim is written in clear, simple language",
                "Assess if the claim avoids ambiguous terms",
                "Determine if the claim is self-contained",
                "Evaluate if the claim is concise yet comprehensive"
            ]
        },
        "relevance": {
            "name": "Relevance Assessment",
            "criteria": "Evaluate how relevant the claim is to current events or public discourse",
            "evaluation_steps": [
                "Assess if the claim addresses current issues",
                "Consider the claim's impact on public opinion",
                "Evaluate the claim's newsworthiness",
                "Determine if the claim affects policy or decision-making"
            ]
        }
    }
    
    metrics = {}
    for metric_type in metric_types:
        if metric_type in metric_definitions:
            metrics[metric_type] = GEval(
                name=metric_definitions[metric_type]["name"],
                criteria=metric_definitions[metric_type]["criteria"],
                evaluation_steps=metric_definitions[metric_type]["evaluation_steps"],
                evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
                model=deepeval_model,
                threshold=0.5
            )
        else:
            logger.warning(f"Unknown metric type: {metric_type}")
            
    return metrics


def evaluate_text_with_metrics(
    text: str,
    metrics: Dict[str, GEval]
) -> Dict[str, Dict[str, Any]]:
    """
    Evaluate text using provided metrics.
    
    Args:
        text: Text content to evaluate
        metrics: Dictionary of metric_name -> GEval instance
        
    Returns:
        Dictionary of evaluation results
    """
    results = {}
    
    for metric_name, metric in metrics.items():
        try:
            logger.info(f"🔍 Running {metric_name} evaluation")
            
            # Create test case
            test_case = LLMTestCase(
                input=f"Evaluate this text: {text}",
                actual_output=text,
                expected_output="High-quality, verified content",
                retrieval_context=[]
            )
            
            # Measure
            metric.measure(test_case)
            
            # Store results
            results[metric_name] = {
                "score": metric.score,
                "reasoning": getattr(metric, 'reasoning', ''),
                "evaluation_details": getattr(metric, 'evaluation_details', {}),
                "threshold": metric.threshold,
                "passed": metric.score >= metric.threshold
            }
            
        except Exception as e:
            logger.warning(f"Failed to evaluate {metric_name}: {e}")
            results[metric_name] = {
                "score": 0.0,
                "error": str(e),
                "passed": False
            }
            
    return results


@observe(name="claim_evaluation_service")
def evaluate_claims_service(
    response: Any, 
    config: Dict[str, Any]
) -> Tuple[Any, Optional[EvaluationReport]]:
    """
    Main evaluation service function.
    
    Args:
        response: ChatCompletion response object
        config: Evaluation configuration containing metrics, model, etc.
        
    Returns:
        Tuple of (response, evaluation_report)
    """
    try:
        logger.info("📊 Starting claim evaluation service")
        
        # Get evaluation metrics from config
        metrics_to_use = config.get('metrics', [])
        
        if not metrics_to_use:
            logger.info("No evaluation metrics specified")
            return response, None
            
        # Extract content from response
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
        else:
            logger.warning("No content found in response to evaluate")
            return response, None
            
        # Get model information
        model_name = config.get('model', 'gpt-3.5-turbo')
        api_key = config.get('api_key')
        
        # Create DeepEval model
        deepeval_model_wrapper = DeepEvalModel(model=model_name, api_key=api_key)
        deepeval_model = deepeval_model_wrapper.get_model()
        
        # Create evaluation metrics
        evaluation_metrics = create_evaluation_metrics(metrics_to_use, deepeval_model)
        
        if not evaluation_metrics:
            logger.warning("No valid evaluation metrics created")
            return response, None
            
        # Run evaluations
        detailed_results = evaluate_text_with_metrics(content, evaluation_metrics)
        
        # Extract scores
        scores = {name: result.get('score', 0.0) for name, result in detailed_results.items()}
        
        # Create evaluation report
        evaluation_report = EvaluationReport(
            metrics_used=list(scores.keys()),
            scores=scores,
            detailed_results=detailed_results,
            timestamp=datetime.utcnow().isoformat(),
            model_info={
                "model_name": model_name,
                "evaluation_model": deepeval_model.get_model_name() if hasattr(deepeval_model, 'get_model_name') else model_name
            }
        )
        
        logger.info(f"✅ Claim evaluation completed: {len(scores)} metrics evaluated")
        return response, evaluation_report
        
    except Exception as e:
        logger.error(f"❌ Error during claim evaluation: {e}")
        # Return original response if evaluation fails
        return response, None
