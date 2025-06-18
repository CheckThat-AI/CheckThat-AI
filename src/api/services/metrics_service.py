import logging
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from ..metrics import (
    MeteorCalculator, MeteorConfig,
    RougeCalculator, RougeConfig,
    BleuCalculator, BleuConfig,
    BertCalculator, BertConfig,
    CosineSimilarityCalculator, CosineSimilarityConfig
)
from ..models.requests import MetricCalculationRequest, BatchMetricRequest, SessionMetricRequest, BatchSessionMetricRequest
from ..models.responses import MetricCalculationResponse, BatchMetricResponse
from .evaluation_session import evaluation_session_manager

logger = logging.getLogger(__name__)

class MetricsService:
    """
    Service for handling metric calculations with configuration and error handling.
    
    Provides a unified interface for all supported metrics with proper error handling,
    configuration management, performance monitoring, and session-based calculations.
    """
    
    # Supported metric types
    SUPPORTED_METRICS = {
        'meteor': {'calculator': MeteorCalculator, 'config': MeteorConfig},
        'rouge': {'calculator': RougeCalculator, 'config': RougeConfig},
        'bleu': {'calculator': BleuCalculator, 'config': BleuConfig},
        'bert': {'calculator': BertCalculator, 'config': BertConfig},
        'cosine': {'calculator': CosineSimilarityCalculator, 'config': CosineSimilarityConfig}
    }
    
    def __init__(self):
        """Initialize the metrics service"""
        self._calculator_cache: Dict[str, Any] = {}
        self._last_used_configs: Dict[str, Dict[str, Any]] = {}
    
    def _get_calculator(self, metric_type: str, config: Optional[Dict[str, Any]] = None) -> Any:
        """
        Get or create a calculator instance for the given metric type.
        
        Args:
            metric_type: Type of metric calculator needed
            config: Optional configuration for the calculator
            
        Returns:
            Calculator instance
            
        Raises:
            ValueError: If metric type is not supported
        """
        if metric_type not in self.SUPPORTED_METRICS:
            raise ValueError(f"Unsupported metric type: {metric_type}. "
                           f"Supported types: {list(self.SUPPORTED_METRICS.keys())}")
        
        # Create cache key based on metric type and config
        config_hash = str(hash(str(sorted((config or {}).items()))))
        cache_key = f"{metric_type}:{config_hash}"
        
        # Check if we need to create a new calculator or can reuse existing one
        if (cache_key not in self._calculator_cache or 
            self._last_used_configs.get(metric_type) != config):
            
            metric_info = self.SUPPORTED_METRICS[metric_type]
            
            if config:
                # Create config object from dict
                config_obj = metric_info['config'](**config)
                calculator = metric_info['calculator'](config=config_obj)
            else:
                # Use default configuration
                calculator = metric_info['calculator']()
            
            self._calculator_cache[cache_key] = calculator
            self._last_used_configs[metric_type] = config
            
            logger.debug(f"Created new {metric_type} calculator with config: {config}")
        
        return self._calculator_cache[cache_key]
    
    def _resolve_texts(self, request: MetricCalculationRequest) -> Tuple[List[str], List[str]]:
        """
        Resolve response and reference texts from either direct input or session storage.
        
        Args:
            request: Metric calculation request
            
        Returns:
            Tuple of (response_texts, reference_texts)
            
        Raises:
            ValueError: If texts cannot be resolved
        """
        # If texts are provided directly, use them
        if request.response_texts is not None and request.reference_texts is not None:
            return request.response_texts, request.reference_texts
        
        # If session_id is provided, get texts from session
        if request.session_id:
            claims_data = evaluation_session_manager.get_claims_for_metrics(request.session_id)
            if claims_data:
                return claims_data  # Returns (extracted_claims, reference_claims)
            else:
                raise ValueError(f"Session {request.session_id} not found or has no claim data")
        
        # If evaluation_result_id is provided (for future implementation)
        if request.evaluation_result_id:
            # This could be extended to support persistent storage
            raise ValueError("Evaluation result ID lookup not yet implemented")
        
        raise ValueError("No text data provided. Either specify response_texts/reference_texts or session_id")
    
    def calculate_metric(self, request: MetricCalculationRequest) -> MetricCalculationResponse:
        """
        Calculate a single metric for the given text pairs.
        
        Args:
            request: Metric calculation request
            
        Returns:
            Metric calculation response with scores and metadata
            
        Raises:
            ValueError: If request is invalid or calculation fails
        """
        start_time = time.time()
        
        try:
            # Resolve texts from request or session
            response_texts, reference_texts = self._resolve_texts(request)
            
            # Validate resolved texts
            if len(response_texts) != len(reference_texts):
                raise ValueError("Response and reference text lists must have the same length")
            
            if not response_texts:
                raise ValueError("Text lists cannot be empty")
            
            # Get calculator
            calculator = self._get_calculator(request.metric_type, request.config)
            
            # Calculate scores
            if len(response_texts) == 1:
                # Single pair calculation
                if request.return_detailed:
                    result = calculator.calculate_score(
                        response_texts[0], 
                        reference_texts[0],
                        return_detailed=True
                    )
                    scores = [result.score]
                    detailed_results = [result.dict()]
                else:
                    score = calculator.calculate_score(
                        response_texts[0], 
                        reference_texts[0]
                    )
                    scores = [score]
                    detailed_results = None
            else:
                # Batch calculation
                if request.return_detailed:
                    results = calculator.calculate_batch(
                        response_texts,
                        reference_texts,
                        return_detailed=True
                    )
                    scores = [r.score for r in results]
                    detailed_results = [r.dict() for r in results]
                else:
                    scores = calculator.calculate_batch(
                        response_texts,
                        reference_texts
                    )
                    detailed_results = None
            
            execution_time = time.time() - start_time
            
            # Get calculator metadata
            metadata = {
                "pairs_processed": len(response_texts),
                "calculator_config": request.config or {},
                "cache_info": calculator.get_cache_info() if hasattr(calculator, 'get_cache_info') else {},
                "data_source": "session" if request.session_id else "direct"
            }
            
            if request.session_id:
                metadata["session_id"] = request.session_id
            
            return MetricCalculationResponse(
                metric_type=request.metric_type,
                scores=scores,
                execution_time=execution_time,
                success=True,
                detailed_results=detailed_results,
                metadata=metadata
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Metric calculation failed for {request.metric_type}: {str(e)}")
            
            return MetricCalculationResponse(
                metric_type=request.metric_type,
                scores=[],
                execution_time=execution_time,
                success=False,
                metadata={"error": str(e)}
            )
    
    def calculate_session_metric(self, request: SessionMetricRequest) -> MetricCalculationResponse:
        """
        Calculate a single metric using session-stored data.
        
        Args:
            request: Session-based metric calculation request
            
        Returns:
            Metric calculation response
        """
        # Convert to full MetricCalculationRequest
        full_request = MetricCalculationRequest(
            metric_type=request.metric_type,
            session_id=request.session_id,
            config=request.config,
            return_detailed=request.return_detailed
        )
        return self.calculate_metric(full_request)
    
    def calculate_batch_metrics(self, request: BatchMetricRequest) -> BatchMetricResponse:
        """
        Calculate multiple metrics for the given text pairs.
        
        Args:
            request: Batch metric calculation request
            
        Returns:
            Batch metric calculation response with results for all metrics
        """
        start_time = time.time()
        results = {}
        failed_metrics = []
        
        try:
            # Resolve texts once for all metrics
            if request.session_id:
                claims_data = evaluation_session_manager.get_claims_for_metrics(request.session_id)
                if not claims_data:
                    return BatchMetricResponse(
                        results={},
                        total_execution_time=time.time() - start_time,
                        success=False,
                        failed_metrics=request.metrics
                    )
                response_texts, reference_texts = claims_data
            else:
                response_texts, reference_texts = request.response_texts, request.reference_texts
            
            # Validate common inputs
            if not response_texts or not reference_texts:
                return BatchMetricResponse(
                    results={},
                    total_execution_time=time.time() - start_time,
                    success=False,
                    failed_metrics=request.metrics
                )
            
            if len(response_texts) != len(reference_texts):
                return BatchMetricResponse(
                    results={},
                    total_execution_time=time.time() - start_time,
                    success=False,
                    failed_metrics=request.metrics
                )
        
        except Exception as e:
            logger.error(f"Failed to resolve texts for batch calculation: {str(e)}")
            return BatchMetricResponse(
                results={},
                total_execution_time=time.time() - start_time,
                success=False,
                failed_metrics=request.metrics
            )
        
        # Calculate each metric
        for metric_type in request.metrics:
            try:
                # Get metric-specific config
                metric_config = None
                if request.configs and metric_type in request.configs:
                    metric_config = request.configs[metric_type]
                
                # Create individual request
                individual_request = MetricCalculationRequest(
                    metric_type=metric_type,
                    response_texts=response_texts,
                    reference_texts=reference_texts,
                    config=metric_config,
                    return_detailed=request.return_detailed
                )
                
                # Calculate metric
                result = self.calculate_metric(individual_request)
                results[metric_type] = result
                
                if not result.success:
                    failed_metrics.append(metric_type)
                
            except Exception as e:
                logger.error(f"Failed to calculate {metric_type}: {str(e)}")
                failed_metrics.append(metric_type)
                
                # Add error result
                results[metric_type] = MetricCalculationResponse(
                    metric_type=metric_type,
                    scores=[],
                    execution_time=0.0,
                    success=False,
                    metadata={"error": str(e)}
                )
        
        total_execution_time = time.time() - start_time
        overall_success = len(failed_metrics) == 0
        
        return BatchMetricResponse(
            results=results,
            total_execution_time=total_execution_time,
            success=overall_success,
            failed_metrics=failed_metrics if failed_metrics else None
        )
    
    def calculate_batch_session_metrics(self, request: BatchSessionMetricRequest) -> BatchMetricResponse:
        """
        Calculate multiple metrics using session-stored data.
        
        Args:
            request: Session-based batch metric calculation request
            
        Returns:
            Batch metric calculation response
        """
        # Convert to full BatchMetricRequest
        full_request = BatchMetricRequest(
            metrics=request.metrics,
            session_id=request.session_id,
            configs=request.configs,
            return_detailed=request.return_detailed
        )
        return self.calculate_batch_metrics(full_request)
    
    def get_supported_metrics(self) -> List[str]:
        """Get list of supported metric types"""
        return list(self.SUPPORTED_METRICS.keys())
    
    def get_metric_info(self, metric_type: str) -> Dict[str, Any]:
        """
        Get information about a specific metric type.
        
        Args:
            metric_type: Type of metric to get info for
            
        Returns:
            Dictionary with metric information
            
        Raises:
            ValueError: If metric type is not supported
        """
        if metric_type not in self.SUPPORTED_METRICS:
            raise ValueError(f"Unsupported metric type: {metric_type}")
        
        metric_info = self.SUPPORTED_METRICS[metric_type]
        config_class = metric_info['config']
        
        # Get default config for schema
        default_config = config_class()
        
        return {
            "metric_type": metric_type,
            "calculator_class": metric_info['calculator'].__name__,
            "config_schema": default_config.dict(),
            "config_fields": list(default_config.dict().keys()),
            "description": metric_info['calculator'].__doc__ or f"{metric_type.upper()} metric calculator"
        }
    
    def clear_all_caches(self) -> Dict[str, int]:
        """
        Clear all calculator caches.
        
        Returns:
            Dictionary with cache sizes before clearing
        """
        cache_info = {}
        
        for cache_key, calculator in self._calculator_cache.items():
            if hasattr(calculator, 'get_cache_info'):
                cache_info[cache_key] = calculator.get_cache_info().get('cache_size', 0)
                calculator.clear_cache()
            else:
                cache_info[cache_key] = 0
        
        logger.info(f"Cleared caches for {len(cache_info)} calculators")
        return cache_info

# Create global service instance
metrics_service = MetricsService() 