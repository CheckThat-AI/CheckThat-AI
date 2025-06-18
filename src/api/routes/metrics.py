from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

from ..models.requests import MetricCalculationRequest, BatchMetricRequest, SessionMetricRequest, BatchSessionMetricRequest
from ..models.responses import MetricCalculationResponse, BatchMetricResponse, ErrorResponse
from ..services.metrics_service import metrics_service
from ..services.extraction_session import extraction_session_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/supported", summary="Get supported metrics")
async def get_supported_metrics() -> Dict[str, List[str]]:
    """
    Get list of all supported metric types.
    
    Returns:
        Dictionary containing supported metric types
    """
    try:
        supported = metrics_service.get_supported_metrics()
        return {"supported_metrics": supported}
    except Exception as e:
        logger.error(f"Error getting supported metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get supported metrics")

@router.get("/info/{metric_type}", summary="Get metric information")
async def get_metric_info(metric_type: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific metric type.
    
    Args:
        metric_type: Type of metric to get information for
        
    Returns:
        Dictionary with metric information including configuration schema
        
    Raises:
        HTTPException: If metric type is not supported
    """
    try:
        info = metrics_service.get_metric_info(metric_type)
        return info
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting metric info for {metric_type}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get metric information")

@router.post("/calculate", response_model=MetricCalculationResponse, summary="Calculate single metric")
async def calculate_metric(request: MetricCalculationRequest) -> MetricCalculationResponse:
    """
    Calculate a single metric for the provided text pairs or session data.
    
    Args:
        request: Metric calculation request containing texts/session_id and configuration
        
    Returns:
        Metric calculation response with scores and metadata
        
    Example with direct texts:
        ```json
        {
            "metric_type": "meteor",
            "response_texts": ["The cat sat on the mat"],
            "reference_texts": ["A cat was sitting on the mat"],
            "config": {"alpha": 0.9, "beta": 3.0},
            "return_detailed": true
        }
        ```
        
    Example with session data:
        ```json
        {
            "metric_type": "meteor",
            "session_id": "eval_session_123",
            "config": {"alpha": 0.9, "beta": 3.0},
            "return_detailed": true
        }
        ```
    """
    try:
        result = metrics_service.calculate_metric(request)
        return result
    except Exception as e:
        logger.error(f"Error calculating {request.metric_type} metric: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate {request.metric_type} metric")

@router.post("/calculate/session", response_model=MetricCalculationResponse, summary="Calculate metric for session")
async def calculate_session_metric(request: SessionMetricRequest) -> MetricCalculationResponse:
    """
    Calculate a single metric using session-stored evaluation data.
    
    This is a simplified endpoint for when you just want to specify the metric type
    and session ID without needing to send the text data again.
    
    Args:
        request: Session-based metric calculation request
        
    Returns:
        Metric calculation response with scores and metadata
        
    Example:
        ```json
        {
            "session_id": "eval_session_123",
            "metric_type": "meteor",
            "config": {"alpha": 0.9},
            "return_detailed": true
        }
        ```
    """
    try:
        result = metrics_service.calculate_session_metric(request)
        return result
    except Exception as e:
        logger.error(f"Error calculating session {request.metric_type} metric: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate session {request.metric_type} metric")

@router.post("/calculate/batch", response_model=BatchMetricResponse, summary="Calculate multiple metrics")
async def calculate_batch_metrics(request: BatchMetricRequest) -> BatchMetricResponse:
    """
    Calculate multiple metrics for the provided text pairs or session data.
    
    Args:
        request: Batch metric calculation request
        
    Returns:
        Batch metric calculation response with results for all requested metrics
        
    Example with direct texts:
        ```json
        {
            "metrics": ["meteor", "rouge", "bleu"],
            "response_texts": ["The cat sat on the mat"],
            "reference_texts": ["A cat was sitting on the mat"],
            "configs": {
                "meteor": {"alpha": 0.9},
                "rouge": {"rouge_types": ["rouge1", "rougeL"]}
            },
            "return_detailed": true
        }
        ```
        
    Example with session data:
        ```json
        {
            "metrics": ["meteor", "rouge", "bleu"],
            "session_id": "eval_session_123",
            "configs": {
                "meteor": {"alpha": 0.9},
                "rouge": {"rouge_types": ["rouge1", "rougeL"]}
            },
            "return_detailed": true
        }
        ```
    """
    try:
        result = metrics_service.calculate_batch_metrics(request)
        return result
    except Exception as e:
        logger.error(f"Error calculating batch metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate batch metrics")

@router.post("/calculate/batch/session", response_model=BatchMetricResponse, summary="Calculate multiple metrics for session")
async def calculate_batch_session_metrics(request: BatchSessionMetricRequest) -> BatchMetricResponse:
    """
    Calculate multiple metrics using session-stored evaluation data.
    
    This is a simplified endpoint for batch metric calculation when you just want to
    specify the metric types and session ID without needing to send the text data again.
    
    Args:
        request: Session-based batch metric calculation request
        
    Returns:
        Batch metric calculation response with results for all requested metrics
        
    Example:
        ```json
        {
            "session_id": "eval_session_123",
            "metrics": ["meteor", "rouge", "bleu"],
            "configs": {
                "meteor": {"alpha": 0.9},
                "rouge": {"rouge_types": ["rouge1", "rougeL"]}
            },
            "return_detailed": true
        }
        ```
    """
    try:
        result = metrics_service.calculate_batch_session_metrics(request)
        return result
    except Exception as e:
        logger.error(f"Error calculating batch session metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate batch session metrics")

@router.post("/cache/clear", summary="Clear metric caches")
async def clear_metric_caches() -> Dict[str, Any]:
    """
    Clear all metric calculation caches.
    
    Returns:
        Dictionary with information about cleared caches
    """
    try:
        cache_info = metrics_service.clear_all_caches()
        return {
            "message": "Caches cleared successfully",
            "cleared_caches": cache_info,
            "total_calculators": len(cache_info)
        }
    except Exception as e:
        logger.error(f"Error clearing caches: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear caches")

# Session management endpoints

@router.get("/sessions", summary="List evaluation sessions")
async def list_sessions() -> Dict[str, Any]:
    """
    List all active evaluation sessions.
    
    Returns:
        Dictionary with session information
    """
    try:
        sessions = extraction_session_manager.list_sessions()
        stats = extraction_session_manager.get_session_stats()
        return {
            "sessions": sessions,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")

@router.get("/sessions/{session_id}", summary="Get session details")
async def get_session_details(session_id: str) -> Dict[str, Any]:
    """
    Get details for a specific session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session details including claim counts and metadata
    """
    try:
        eval_data = extraction_session_manager.get_evaluation_data(session_id)
        if not eval_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "session_id": eval_data.session_id,
            "extracted_claims_count": len(eval_data.extracted_claims),
            "reference_claims_count": len(eval_data.reference_claims),
            "model_combinations": eval_data.model_combinations,
            "metadata": eval_data.metadata,
            "created_at": eval_data.created_at,
            "last_accessed": eval_data.last_accessed
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get session details")

@router.delete("/sessions/{session_id}", summary="Remove session")
async def remove_session(session_id: str) -> Dict[str, Any]:
    """
    Remove a session from storage.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Confirmation message
    """
    try:
        success = extraction_session_manager.remove_session(session_id)
        if success:
            return {"message": f"Session {session_id} removed successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove session")

# Convenience endpoints for individual metrics (updated to support session-based calculation)

@router.post("/meteor", summary="Calculate METEOR score")
async def calculate_meteor(
    response_texts: List[str] = None,
    reference_texts: List[str] = None,
    session_id: str = None,
    config: Dict[str, Any] = None,
    return_detailed: bool = False
) -> MetricCalculationResponse:
    """Convenience endpoint for METEOR calculation (supports both direct texts and session data)"""
    request = MetricCalculationRequest(
        metric_type="meteor",
        response_texts=response_texts,
        reference_texts=reference_texts,
        session_id=session_id,
        config=config,
        return_detailed=return_detailed
    )
    return await calculate_metric(request)

@router.post("/rouge", summary="Calculate ROUGE score")
async def calculate_rouge(
    response_texts: List[str] = None,
    reference_texts: List[str] = None,
    session_id: str = None,
    config: Dict[str, Any] = None,
    return_detailed: bool = False
) -> MetricCalculationResponse:
    """Convenience endpoint for ROUGE calculation (supports both direct texts and session data)"""
    request = MetricCalculationRequest(
        metric_type="rouge",
        response_texts=response_texts,
        reference_texts=reference_texts,
        session_id=session_id,
        config=config,
        return_detailed=return_detailed
    )
    return await calculate_metric(request)

@router.post("/bleu", summary="Calculate BLEU score")
async def calculate_bleu(
    response_texts: List[str] = None,
    reference_texts: List[str] = None,
    session_id: str = None,
    config: Dict[str, Any] = None,
    return_detailed: bool = False
) -> MetricCalculationResponse:
    """Convenience endpoint for BLEU calculation (supports both direct texts and session data)"""
    request = MetricCalculationRequest(
        metric_type="bleu",
        response_texts=response_texts,
        reference_texts=reference_texts,
        session_id=session_id,
        config=config,
        return_detailed=return_detailed
    )
    return await calculate_metric(request)

@router.post("/bert", summary="Calculate BERT score")
async def calculate_bert(
    response_texts: List[str] = None,
    reference_texts: List[str] = None,
    session_id: str = None,
    config: Dict[str, Any] = None,
    return_detailed: bool = False
) -> MetricCalculationResponse:
    """Convenience endpoint for BERT score calculation (supports both direct texts and session data)"""
    request = MetricCalculationRequest(
        metric_type="bert",
        response_texts=response_texts,
        reference_texts=reference_texts,
        session_id=session_id,
        config=config,
        return_detailed=return_detailed
    )
    return await calculate_metric(request)

@router.post("/cosine", summary="Calculate cosine similarity")
async def calculate_cosine_similarity(
    response_texts: List[str] = None,
    reference_texts: List[str] = None,
    session_id: str = None,
    config: Dict[str, Any] = None,
    return_detailed: bool = False
) -> MetricCalculationResponse:
    """Convenience endpoint for cosine similarity calculation (supports both direct texts and session data)"""
    request = MetricCalculationRequest(
        metric_type="cosine",
        response_texts=response_texts,
        reference_texts=reference_texts,
        session_id=session_id,
        config=config,
        return_detailed=return_detailed
    )
    return await calculate_metric(request) 