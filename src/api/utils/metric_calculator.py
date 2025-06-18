"""
Utility functions for metric calculation that can be integrated into existing services.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from ..services.metrics_service import metrics_service
from ..models.requests import MetricCalculationRequest, BatchMetricRequest

logger = logging.getLogger(__name__)

def calculate_single_metric(
    metric_type: str,
    response_texts: List[str],
    reference_texts: List[str],
    config: Optional[Dict[str, Any]] = None,
    return_detailed: bool = False
) -> Dict[str, Any]:
    """
    Calculate a single metric for text pairs.
    
    Args:
        metric_type: Type of metric ('meteor', 'rouge', 'bleu', 'bert', 'cosine')
        response_texts: List of generated/predicted texts
        reference_texts: List of reference/ground truth texts
        config: Optional configuration for the metric
        return_detailed: Whether to return detailed results
        
    Returns:
        Dictionary with calculation results
        
    Raises:
        ValueError: If metric type is unsupported or inputs are invalid
    """
    try:
        request = MetricCalculationRequest(
            metric_type=metric_type,
            response_texts=response_texts,
            reference_texts=reference_texts,
            config=config,
            return_detailed=return_detailed
        )
        
        result = metrics_service.calculate_metric(request)
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error calculating {metric_type} metric: {str(e)}")
        raise ValueError(f"Failed to calculate {metric_type} metric: {str(e)}")

def calculate_multiple_metrics(
    metrics: List[str],
    response_texts: List[str],
    reference_texts: List[str],
    configs: Optional[Dict[str, Dict[str, Any]]] = None,
    return_detailed: bool = False
) -> Dict[str, Any]:
    """
    Calculate multiple metrics for text pairs.
    
    Args:
        metrics: List of metric types to calculate
        response_texts: List of generated/predicted texts
        reference_texts: List of reference/ground truth texts
        configs: Optional configurations per metric
        return_detailed: Whether to return detailed results
        
    Returns:
        Dictionary with results for all metrics
        
    Raises:
        ValueError: If inputs are invalid
    """
    try:
        request = BatchMetricRequest(
            metrics=metrics,
            response_texts=response_texts,
            reference_texts=reference_texts,
            configs=configs,
            return_detailed=return_detailed
        )
        
        result = metrics_service.calculate_batch_metrics(request)
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error calculating batch metrics: {str(e)}")
        raise ValueError(f"Failed to calculate batch metrics: {str(e)}")

def get_metric_scores_only(
    metric_type: str,
    response_texts: List[str],
    reference_texts: List[str],
    config: Optional[Dict[str, Any]] = None
) -> List[float]:
    """
    Calculate metric and return only the scores (simplified interface).
    
    Args:
        metric_type: Type of metric to calculate
        response_texts: List of generated/predicted texts
        reference_texts: List of reference/ground truth texts
        config: Optional configuration for the metric
        
    Returns:
        List of metric scores
        
    Raises:
        ValueError: If calculation fails
    """
    try:
        result = calculate_single_metric(
            metric_type=metric_type,
            response_texts=response_texts,
            reference_texts=reference_texts,
            config=config,
            return_detailed=False
        )
        
        if result['success']:
            return result['scores']
        else:
            raise ValueError(f"Metric calculation failed: {result.get('metadata', {}).get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error getting scores for {metric_type}: {str(e)}")
        raise ValueError(f"Failed to get {metric_type} scores: {str(e)}")

def calculate_evaluation_metrics(
    response_texts: List[str],
    reference_texts: List[str],
    selected_metric: str = "meteor",
    metric_config: Optional[Dict[str, Any]] = None
) -> Dict[str, float]:
    """
    Calculate metrics for evaluation results.
    
    This function is designed to be called from the evaluation service
    to calculate metrics after claim extraction is complete.
    
    Args:
        response_texts: List of extracted/generated claims
        reference_texts: List of reference/ground truth claims
        selected_metric: The metric to use for evaluation
        metric_config: Optional configuration for the metric
        
    Returns:
        Dictionary with metric results
        
    Raises:
        ValueError: If calculation fails
    """
    try:
        # Validate inputs
        if not response_texts or not reference_texts:
            raise ValueError("Text lists cannot be empty")
        
        if len(response_texts) != len(reference_texts):
            raise ValueError("Response and reference text lists must have the same length")
        
        # Calculate the selected metric
        scores = get_metric_scores_only(
            metric_type=selected_metric,
            response_texts=response_texts,
            reference_texts=reference_texts,
            config=metric_config
        )
        
        # Calculate summary statistics
        avg_score = sum(scores) / len(scores) if scores else 0.0
        min_score = min(scores) if scores else 0.0
        max_score = max(scores) if scores else 0.0
        
        return {
            f"{selected_metric}_scores": scores,
            f"{selected_metric}_avg": avg_score,
            f"{selected_metric}_min": min_score,
            f"{selected_metric}_max": max_score,
            "total_pairs": len(scores)
        }
        
    except Exception as e:
        logger.error(f"Error calculating evaluation metrics: {str(e)}")
        raise ValueError(f"Failed to calculate evaluation metrics: {str(e)}")

def get_supported_metrics() -> List[str]:
    """Get list of supported metric types."""
    return metrics_service.get_supported_metrics()

def get_metric_config_schema(metric_type: str) -> Dict[str, Any]:
    """
    Get configuration schema for a specific metric type.
    
    Args:
        metric_type: Type of metric to get schema for
        
    Returns:
        Dictionary with configuration schema
        
    Raises:
        ValueError: If metric type is not supported
    """
    try:
        info = metrics_service.get_metric_info(metric_type)
        return info["config_schema"]
    except Exception as e:
        logger.error(f"Error getting config schema for {metric_type}: {str(e)}")
        raise ValueError(f"Failed to get config schema for {metric_type}: {str(e)}") 