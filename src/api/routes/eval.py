from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

from ..models.requests import MetricCalculationRequest, BatchMetricRequest, SessionMetricRequest, BatchSessionMetricRequest, DeepEvalRequest
from ..models.responses import MetricCalculationResponse, BatchMetricResponse, ErrorResponse, DeepEvalResponse
from ..services.eval_service import eval_service
from ..services.extraction_session import extraction_session_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/eval", tags=["evaluation"])

@router.get("/supported", summary="Get supported metrics")
async def get_supported_metrics() -> Dict[str, List[str]]:
    """
    Get list of all supported metric types.
    
    Returns:
        Dictionary containing supported metric types
    """
    try:
        supported = eval_service.get_supported_metrics()
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
        info = eval_service.get_metric_info(metric_type)
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
        result = eval_service.calculate_metric(request)
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
        result = eval_service.calculate_session_metric(request)
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
        result = eval_service.calculate_batch_metrics(request)
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
        result = eval_service.calculate_batch_session_metrics(request)
        return result
    except Exception as e:
        logger.error(f"Error calculating batch session metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate batch session metrics")

@router.post("/deepeval", response_model=DeepEvalResponse, summary="Evaluate with DeepEval")
async def evaluate_with_deepeval(request: DeepEvalRequest) -> DeepEvalResponse:
    """
    Create a DeepEval dataset from session data and perform evaluation.
    
    This endpoint handles both dataset creation and evaluation using DeepEval's
    referenceless metrics. It can save datasets to DeepEval cloud or locally.
    
    Args:
        request: DeepEval evaluation request
        
    Returns:
        DeepEval evaluation response with dataset info and evaluation results
        
    Example:
        ```json
        {
            "session_id": "extraction_session_123",
            "metric_type": "faithfulness",
            "model_provider": "openai",
            "model_name": "gpt-4",
            "api_key": "sk-...",
            "confident_api_key": "de_...",
            "dataset_alias": "MyDataset",
            "threshold": 0.7,
            "include_reason": true,
            "strict_mode": false,
            "save_to_cloud": true,
            "local_directory": "./deepeval-test-dataset"
        }
        ```
    """
    try:
        # Note: Session validation is no longer required as DeepEval can work
        # with saved CSV files even if the session has expired
        result = eval_service.evaluate_with_deepeval(request)
        
        if not result.success:
            # Return the error response but don't raise HTTPException
            # since the service already formatted the error properly
            return result
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in DeepEval evaluation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"DeepEval evaluation failed: {str(e)}"
        )

@router.post("/deepeval/async", summary="Start async DeepEval evaluation with WebSocket progress")
async def start_async_deepeval(request: DeepEvalRequest) -> Dict[str, Any]:
    """
    Start an asynchronous DeepEval evaluation with real-time progress updates via WebSocket.
    
    This endpoint starts the evaluation process in the background and returns immediately.
    Progress updates are sent via WebSocket to the client.
    
    Args:
        request: DeepEval evaluation request
        
    Returns:
        Dictionary with evaluation start confirmation and WebSocket details
    """
    import asyncio
    import threading
    from ..services.websocket_manager import websocket_manager
    
    try:
        # Check if WebSocket connection exists for this session
        if not websocket_manager.is_connected(request.session_id):
            return {
                "success": False,
                "message": "WebSocket connection required for async evaluation",
                "error_details": "Please ensure WebSocket connection is active before starting evaluation"
            }
        
        # Send initial progress update
        await websocket_manager.send_message(request.session_id, {
            "type": "deepeval_progress",
            "stage": "starting",
            "progress": 0,
            "message": "Starting DeepEval evaluation...",
            "data": {
                "metric_type": request.metric_type,
                "model_provider": request.model_provider,
                "save_to_cloud": request.save_to_cloud
            }
        })
        
        # Get the current event loop to pass to the background thread
        current_loop = asyncio.get_running_loop()
        
        # Start evaluation in background thread
        def run_async_evaluation():
            try:
                # Run the evaluation with progress callbacks
                result = eval_service.evaluate_with_deepeval_async(request, websocket_manager, current_loop)
                
                # Ensure evaluation results are JSON serializable before sending
                try:
                    import json
                    
                    # Prepare the data payload with safe fallbacks
                    data_payload = {
                        "test_case_count": result.test_case_count,
                        "dataset_saved": result.dataset_saved,
                        "dataset_location": result.dataset_location,
                        "execution_time": result.execution_time,
                        "cloud_url": getattr(result, 'cloud_url', None),
                        "evaluation_results": result.evaluation_results
                    }
                    
                    # Test serialization of the entire result
                    json.dumps(data_payload)
                    
                    # If serialization succeeds, send the full result
                    final_message = {
                        "type": "deepeval_complete",
                        "stage": "complete",
                        "progress": 100,
                        "message": "DeepEval evaluation completed successfully",
                        "success": result.success,
                        "data": data_payload
                    }
                    
                except (TypeError, ValueError) as json_error:
                    logger.warning(f"Evaluation results not JSON serializable: {str(json_error)}")
                    # Send success message without complex evaluation results
                    final_message = {
                        "type": "deepeval_complete",
                        "stage": "complete",
                        "progress": 100,
                        "message": "DeepEval evaluation completed successfully (results available in logs)",
                        "success": result.success,
                        "data": {
                            "test_case_count": result.test_case_count,
                            "dataset_saved": result.dataset_saved,
                            "dataset_location": result.dataset_location,
                            "execution_time": result.execution_time,
                            "cloud_url": getattr(result, 'cloud_url', None),
                            "evaluation_results": {
                                "summary": f"Evaluation completed with {result.test_case_count} test cases",
                                "note": "Full results available via 'deepeval view' command",
                                "serialization_warning": "Complex results omitted due to JSON compatibility"
                            }
                        }
                    }
                
                # Send the final message with timeout and error handling
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        websocket_manager.send_message(request.session_id, final_message),
                        current_loop
                    )
                    future.result(timeout=10.0)  # Increased timeout for final message
                    logger.info(f"Successfully sent DeepEval completion message for session {request.session_id}")
                    
                except Exception as send_error:
                    logger.error(f"Failed to send completion message via WebSocket: {str(send_error)}")
                    # Try sending a simplified fallback message
                    try:
                        fallback_message = {
                            "type": "deepeval_complete",
                            "stage": "complete", 
                            "progress": 100,
                            "message": "Evaluation completed successfully - check logs for details",
                            "success": True,
                            "data": {
                                "test_case_count": getattr(result, 'test_case_count', 0),
                                "note": "WebSocket communication issue - evaluation completed successfully"
                            }
                        }
                        future = asyncio.run_coroutine_threadsafe(
                            websocket_manager.send_message(request.session_id, fallback_message),
                            current_loop
                        )
                        future.result(timeout=5.0)
                        logger.info(f"Sent fallback completion message for session {request.session_id}")
                    except Exception as fallback_error:
                        logger.error(f"Even fallback message failed: {str(fallback_error)}")

            except Exception as e:
                logger.error(f"Async DeepEval evaluation failed: {str(e)}")
                # Send error message using run_coroutine_threadsafe
                error_message = {
                    "type": "deepeval_error",
                    "stage": "error",
                    "progress": 0,
                    "message": f"DeepEval evaluation failed: {str(e)}",
                    "success": False,
                    "error_details": str(e)
                }
                
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        websocket_manager.send_message(request.session_id, error_message),
                        current_loop
                    )
                    future.result(timeout=5.0)
                except Exception as send_error:
                    logger.error(f"Failed to send error message: {str(send_error)}")
                    # Even error sending failed - log this critical issue
                    logger.critical(f"Complete WebSocket communication failure for session {request.session_id}")
        
        # Start the evaluation thread
        eval_thread = threading.Thread(target=run_async_evaluation)
        eval_thread.daemon = True
        eval_thread.start()
        
        return {
            "success": True,
            "message": "DeepEval evaluation started successfully",
            "session_id": request.session_id,
            "evaluation_id": f"eval_{request.session_id}_{int(__import__('time').time())}",
            "websocket_updates": True
        }
        
    except Exception as e:
        logger.error(f"Error starting async DeepEval evaluation: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to start DeepEval evaluation: {str(e)}",
            "error_details": str(e)
        }

@router.post("/cache/clear", summary="Clear metric caches")
async def clear_metric_caches() -> Dict[str, Any]:
    """
    Clear all metric calculation caches.
    
    Returns:
        Dictionary with information about cleared caches
    """
    try:
        cache_info = eval_service.clear_all_caches()
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

# Convenience endpoints for referenceless metrics

@router.post("/faithfulness", summary="Calculate faithfulness score")
async def calculate_faithfulness(
    response_texts: List[str] = None,
    reference_texts: List[str] = None,
    session_id: str = None,
    config: Dict[str, Any] = None,
    return_detailed: bool = False
) -> MetricCalculationResponse:
    """Convenience endpoint for faithfulness calculation (referenceless metric)"""
    request = MetricCalculationRequest(
        metric_type="faithfulness",
        response_texts=response_texts,
        reference_texts=reference_texts,
        session_id=session_id,
        config=config,
        return_detailed=return_detailed
    )
    return await calculate_metric(request)

@router.post("/hallucination", summary="Calculate hallucination score")
async def calculate_hallucination(
    response_texts: List[str] = None,
    reference_texts: List[str] = None,
    session_id: str = None,
    config: Dict[str, Any] = None,
    return_detailed: bool = False
) -> MetricCalculationResponse:
    """Convenience endpoint for hallucination calculation (referenceless metric)"""
    request = MetricCalculationRequest(
        metric_type="hallucination",
        response_texts=response_texts,
        reference_texts=reference_texts,
        session_id=session_id,
        config=config,
        return_detailed=return_detailed
    )
    return await calculate_metric(request)

@router.post("/answer_relevancy", summary="Calculate answer relevancy score")
async def calculate_answer_relevancy(
    response_texts: List[str] = None,
    reference_texts: List[str] = None,
    session_id: str = None,
    config: Dict[str, Any] = None,
    return_detailed: bool = False
) -> MetricCalculationResponse:
    """Convenience endpoint for answer relevancy calculation (referenceless metric)"""
    request = MetricCalculationRequest(
        metric_type="answer_relevancy",
        response_texts=response_texts,
        reference_texts=reference_texts,
        session_id=session_id,
        config=config,
        return_detailed=return_detailed
    )
    return await calculate_metric(request)

 