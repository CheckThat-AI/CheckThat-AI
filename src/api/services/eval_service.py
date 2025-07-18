import logging
import time
import os
from typing import List, Dict, Any, Optional, Union, Tuple
from ..metrics import (
    MeteorCalculator, MeteorConfig,
    RougeCalculator, RougeConfig,
    BleuCalculator, BleuConfig,
    BertCalculator, BertConfig,
    CosineSimilarityCalculator, CosineSimilarityConfig,
    FaithfulnessCalculator, FaithfulnessConfig,
    HallucinationCalculator, HallucinationConfig,
    AnswerRelevancyCalculator, AnswerRelevancyConfig
)

# All metric calculators are imported from their respective modules

from ..models.requests import MetricCalculationRequest, BatchMetricRequest, SessionMetricRequest, BatchSessionMetricRequest, DeepEvalRequest
from ..models.responses import MetricCalculationResponse, BatchMetricResponse, DeepEvalResponse
from .extraction_session import extraction_session_manager

logger = logging.getLogger(__name__)

class EvalService:
    """
    Service for handling metric calculations with configuration and error handling.
    
    Provides a unified interface for all supported metrics with proper error handling,
    configuration management, performance monitoring, and session-based calculations.
    """
    
    # Supported metric types
    SUPPORTED_METRICS = {
        # Reference-based metrics
        'meteor': {'calculator': MeteorCalculator, 'config': MeteorConfig},
        'rouge': {'calculator': RougeCalculator, 'config': RougeConfig},
        'bleu': {'calculator': BleuCalculator, 'config': BleuConfig},
        'bert': {'calculator': BertCalculator, 'config': BertConfig},
        'cosine': {'calculator': CosineSimilarityCalculator, 'config': CosineSimilarityConfig},
        # Referenceless metrics 
        'faithfulness': {'calculator': FaithfulnessCalculator, 'config': FaithfulnessConfig},
        'hallucination': {'calculator': HallucinationCalculator, 'config': HallucinationConfig},
        'answer_relevancy': {'calculator': AnswerRelevancyCalculator, 'config': AnswerRelevancyConfig},
    }
    
    def __init__(self):
        """Initialize the eval service"""
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
            
            # Always create config object, using defaults if none provided
            config_dict = config or {}
            config_obj = metric_info['config'](**config_dict)
            calculator = metric_info['calculator'](config=config_obj)
            
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
            claims_data = extraction_session_manager.get_claims_for_metrics(request.session_id)
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
            
            # Add debugging
            logger.info(f"Resolved texts for {request.metric_type}: response_texts={len(response_texts)}, reference_texts={len(reference_texts)}")
            logger.info(f"Response texts types: {[type(t) for t in response_texts[:3]]}")  # First 3 items
            logger.info(f"Reference texts types: {[type(t) for t in reference_texts[:3]]}")  # First 3 items
            logger.info(f"Response texts sample: {response_texts[:2] if response_texts else []}")
            logger.info(f"Reference texts sample: {reference_texts[:2] if reference_texts else []}")
            
            # Validate resolved texts
            if len(response_texts) != len(reference_texts):
                raise ValueError("Response and reference text lists must have the same length")
            
            if not response_texts:
                raise ValueError("Text lists cannot be empty")
            
            # Check for None values or non-strings
            for i, (resp, ref) in enumerate(zip(response_texts, reference_texts)):
                if resp is None or ref is None:
                    raise ValueError(f"Found None value at index {i}: response={resp}, reference={ref}")
                if not isinstance(resp, str) or not isinstance(ref, str):
                    raise ValueError(f"Found non-string value at index {i}: response={type(resp)}, reference={type(ref)}")
            
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
                claims_data = extraction_session_manager.get_claims_for_metrics(request.session_id)
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
    
    def get_cache_info(self) -> Dict[str, Dict[str, Any]]:
        """Get cache information for all calculators"""
        cache_info = {}
        for metric_type, calculator in self._calculator_cache.items():
            if hasattr(calculator, 'get_cache_info'):
                cache_info[metric_type] = calculator.get_cache_info()
        return cache_info
    
    def _get_cloud_test_run_url(self) -> Optional[str]:
        """
        Read the cloud test run URL from DeepEval's .latest_test_run.json file or parse from logs.
        
        Returns:
            URL to view results on Confident AI cloud, or None if not found
        """
        try:
            import json
            import re
            
            # Check multiple possible locations for the .latest_test_run.json file
            possible_paths = [
                os.path.join(os.getcwd(), ".deepeval", ".latest_test_run.json"),
                os.path.join(".", ".deepeval", ".latest_test_run.json"),
                ".deepeval/.latest_test_run.json",
                os.path.join("src", "api", ".deepeval", ".latest_test_run.json"),
                "src/api/.deepeval/.latest_test_run.json"
            ]
            
            logger.info(f"Searching for .latest_test_run.json in {len(possible_paths)} locations...")
            logger.info(f"Current working directory: {os.getcwd()}")
            
            for path in possible_paths:
                logger.debug(f"Checking path: {path}")
                if os.path.exists(path):
                    logger.info(f"Found file at: {path}")
                    try:
                        with open(path, 'r') as f:
                            data = json.load(f)
                            logger.info(f"File contents: {data}")
                            test_run_link = data.get('testRunLink')
                            if test_run_link:
                                logger.info(f"Found cloud test run URL: {test_run_link}")
                                return test_run_link
                            else:
                                logger.warning(f"No testRunLink found in {path}")
                    except Exception as file_error:
                        logger.error(f"Error reading file {path}: {str(file_error)}")
                        
            # Alternative approach: Parse URL from recent log output
            # Look for the pattern "View results on https://app.confident-ai.com/..."
            try:
                import io
                import sys
                from contextlib import redirect_stdout, redirect_stderr
                
                # Create string buffers to capture output
                stdout_buffer = io.StringIO()
                stderr_buffer = io.StringIO()
                
                # Get any captured output from the evaluation process
                # This is a fallback method to extract URLs from DeepEval's console output
                
                # Check for URL pattern in logging output or try to read from log files
                log_patterns = [
                    r'View results on (https://app\.confident-ai\.com/[^\s]+)',
                    r'✓ Done.*View results on (https://app\.confident-ai\.com/[^\s]+)',
                    r'https://app\.confident-ai\.com/project/[^/]+/evaluation/test-runs/[^/\s]+/?[^\s]*'
                ]
                
                # Look for recent log entries that might contain the URL
                for pattern in log_patterns:
                    # This is a simplified approach - in practice, you might want to
                    # integrate with your logging system to capture this information
                    pass
                    
            except Exception as parse_error:
                logger.debug(f"URL parsing from logs failed: {str(parse_error)}")
            
            # If file method fails, check if any .deepeval directory exists for debugging
            deepeval_dirs = [
                os.path.join(os.getcwd(), ".deepeval"),
                ".deepeval",
                os.path.join("src", "api", ".deepeval"),
                "src/api/.deepeval"
            ]
            
            for dir_path in deepeval_dirs:
                if os.path.exists(dir_path):
                    logger.info(f"DeepEval directory exists at: {dir_path}")
                    try:
                        files = os.listdir(dir_path)
                        logger.info(f"Files in {dir_path}: {files}")
                        
                        # Check if there are any .json files that might contain the URL
                        for file in files:
                            if file.endswith('.json'):
                                file_path = os.path.join(dir_path, file)
                                try:
                                    with open(file_path, 'r') as f:
                                        content = f.read()
                                        # Look for confident-ai.com URLs in any JSON file
                                        url_match = re.search(r'https://app\.confident-ai\.com/[^\s"]+', content)
                                        if url_match:
                                            found_url = url_match.group(0)
                                            logger.info(f"Found URL in {file}: {found_url}")
                                            return found_url
                                except Exception as e:
                                    logger.debug(f"Error reading {file_path}: {str(e)}")
                                    
                    except Exception as e:
                        logger.error(f"Error listing directory {dir_path}: {str(e)}")
                else:
                    logger.debug(f"DeepEval directory not found at: {dir_path}")
            
            logger.warning("Could not find cloud test run URL in any expected location")
            return None
            
        except Exception as e:
            logger.error(f"Error reading cloud test run URL: {str(e)}")
            return None

    def _serialize_evaluation_results(self, evaluation_results):
        """
        Convert DeepEval EvaluationResult objects to JSON-serializable dictionaries.
        
        Args:
            evaluation_results: DeepEval evaluation results (could be various types)
            
        Returns:
            JSON-serializable dictionary representation
        """
        try:
            if evaluation_results is None:
                return None
            
            # Handle different types of evaluation results
            if hasattr(evaluation_results, '__dict__'):
                # If it's an object with attributes, convert to dict
                result_dict = {}
                for key, value in evaluation_results.__dict__.items():
                    try:
                        if hasattr(value, '__dict__'):
                            # Nested object, recursively serialize
                            result_dict[key] = self._serialize_evaluation_results(value)
                        elif isinstance(value, (list, tuple)):
                            # Handle lists/tuples of objects
                            result_dict[key] = [self._serialize_evaluation_results(item) for item in value]
                        elif isinstance(value, dict):
                            # Handle dictionaries
                            result_dict[key] = {k: self._serialize_evaluation_results(v) for k, v in value.items()}
                        elif isinstance(value, (str, int, float, bool)) or value is None:
                            # Basic JSON-serializable types
                            result_dict[key] = value
                        else:
                            # For other types, convert to string representation
                            result_dict[key] = str(value)
                    except Exception as e:
                        # If individual field fails, store as string
                        result_dict[key] = f"<serialization_error: {str(e)}>"
                return result_dict
            elif isinstance(evaluation_results, (list, tuple)):
                # Handle lists/tuples
                return [self._serialize_evaluation_results(item) for item in evaluation_results]
            elif isinstance(evaluation_results, dict):
                # Handle dictionaries
                return {k: self._serialize_evaluation_results(v) for k, v in evaluation_results.items()}
            else:
                # For basic types or unknown objects, return string representation
                return str(evaluation_results)
                
        except Exception as e:
            logger.warning(f"Failed to serialize evaluation results: {str(e)}")
            return {"error": f"Serialization failed: {str(e)}", "raw_type": str(type(evaluation_results))}
    
    def evaluate_with_deepeval(self, request: DeepEvalRequest) -> DeepEvalResponse:
        """
        Create and evaluate a dataset using DeepEval.
        
        Args:
            request: DeepEval evaluation request
            
        Returns:
            DeepEval evaluation response
        """
        start_time = time.time()
        
        def send_progress(stage: str, progress: int, message: str, **kwargs):
            """Helper to send progress updates via WebSocket"""
            try:
                import asyncio
                from ..services.websocket_manager import websocket_manager
                # Create a message with progress information
                progress_message = {
                    "type": "deepeval_progress",
                    "stage": stage,
                    "progress": progress,
                    "message": message,
                    **kwargs
                }
                
                # Use the provided event loop or try to get the running one
                main_loop = asyncio.get_event_loop()
                if main_loop is None:
                    try:
                        main_loop = asyncio.get_running_loop()
                    except RuntimeError:
                        logger.warning("No asyncio event loop available, cannot send progress update")
                        return
                
                # Schedule the coroutine in the main event loop
                future = asyncio.run_coroutine_threadsafe(
                    websocket_manager.send_message(request.session_id, progress_message),
                    main_loop
                )
                
                # Wait for completion with a timeout to avoid blocking indefinitely
                try:
                    future.result(timeout=5.0)  # 5 second timeout
                except Exception as e:
                    logger.warning(f"Failed to send progress update: {str(e)}")
                
            except Exception as e:
                logger.warning(f"Failed to send progress update: {str(e)}")
        
        try:
            # Import DeepEval components and session manager
            from ..utils.create_dataset import DatasetBuilder, MetricType, ModelProvider
            from ..utils.deepeval_session_manager import deepeval_session_manager
            
            # Store API keys in session if requested
            if request.store_api_keys:
                deepeval_session_manager.set_session_api_key(
                    request.session_id, 
                    request.confident_api_key
                )
            
            # Check if we need to recreate the dataset based on file changes
            from ..services.extraction_session import extraction_session_manager
            
            # Get the current file data to calculate hash
            current_file_data = None
            try:
                session_data = extraction_session_manager.get_extraction_data(request.session_id)
                if session_data:
                    # Calculate hash based on extraction claims data
                    claims_content = {
                        'extracted_claims': session_data.extracted_claims,
                        'reference_claims': session_data.reference_claims,
                        'model_combinations': session_data.model_combinations
                    }
                    file_content = str(claims_content).encode('utf-8')
                    current_file_hash = deepeval_session_manager.calculate_file_hash(file_content)
                    
                    # Check if dataset should be recreated
                    should_recreate, existing_dataset_info = deepeval_session_manager.should_recreate_dataset(
                        request.session_id, current_file_hash
                    )
                    
                    if not should_recreate and existing_dataset_info:
                        # Dataset exists and file hasn't changed, skip creation and proceed to evaluation
                        logger.info(f"Reusing existing dataset for session {request.session_id}")
                        
                        # Load existing dataset for evaluation - skip to evaluation stage
                        dataset_wrapper = DatasetBuilder(request.session_id, extraction_session_manager) \
                            .with_metric_type(metric_type) \
                            .with_model_config(
                                provider=model_provider,
                                model_name=request.model_name,
                                api_key=api_key_to_use,
                                temperature=0.0
                            ) \
                            .with_metric_config(
                                threshold=request.threshold,
                                include_reason=request.include_reason,
                                strict_mode=request.strict_mode
                            ) \
                            .build()
                        
                        # Jump to evaluation stage
                        send_progress("evaluation", 0, "Starting evaluation with existing dataset...")
                        evaluation_results = dataset_wrapper.evaluate()
                        send_progress("evaluation", 100, "Evaluation completed successfully!")
                        
                        # Serialize evaluation results to ensure JSON compatibility
                        serialized_results = self._serialize_evaluation_results(evaluation_results)
                        
                        # Try to get cloud URL if this was a cloud evaluation
                        logger.info(f"Checking for cloud URL: save_to_cloud={request.save_to_cloud}, confident_api_key={'***' if request.confident_api_key else None}")
                        cloud_url = self._get_cloud_test_run_url() if request.save_to_cloud else None
                        logger.info(f"Cloud URL result: {cloud_url}")
                        
                        return DeepEvalResponse(
                            success=True,
                            message="DeepEval evaluation completed successfully (reused existing dataset)",
                            dataset_saved=True,
                            dataset_location=existing_dataset_info.get('location'),
                            test_case_count=existing_dataset_info.get('test_case_count', 0),
                            dataset_reused=True,
                            evaluation_results=serialized_results,
                            execution_time=time.time() - start_time,
                            file_hash=current_file_hash,
                            cloud_url=cloud_url
                        )
                            
                        # Store the current file hash for future comparisons
                        deepeval_session_manager.set_session_file_hash(request.session_id, current_file_hash)
                    
                else:
                    logger.warning(f"No file data found for session {request.session_id}")
                    
            except Exception as e:
                logger.warning(f"Error checking dataset existence: {str(e)}")
                # Continue with normal flow if there's an error
            
            # Prepare environment for evaluation type
            preparation_success = deepeval_session_manager.prepare_for_evaluation(
                request.session_id,
                request.save_to_cloud
            )
            
            if not preparation_success:
                return DeepEvalResponse(
                    success=False,
                    message="Failed to prepare evaluation environment",
                    dataset_saved=False,
                    test_case_count=0,
                    execution_time=time.time() - start_time,
                    error_details="Session preparation failed - check API key configuration"
                )
            
            # Map request values to enum types
            try:
                metric_type = MetricType(request.metric_type.lower())
            except ValueError:
                return DeepEvalResponse(
                    success=False,
                    message=f"Unsupported metric type: {request.metric_type}",
                    dataset_saved=False,
                    test_case_count=0,
                    execution_time=time.time() - start_time,
                    error_details=f"Supported metrics: {[m.value for m in MetricType]}"
                )
            
            try:
                model_provider = ModelProvider(request.model_provider.lower())
            except ValueError:
                return DeepEvalResponse(
                    success=False,
                    message=f"Unsupported model provider: {request.model_provider}",
                    dataset_saved=False,
                    test_case_count=0,
                    execution_time=time.time() - start_time,
                    error_details=f"Supported providers: {[p.value for p in ModelProvider]}"
                )
            
            # Build and save dataset
            logger.info(f"Building DeepEval dataset for session {request.session_id}")
            dataset_wrapper, save_success = (
                DatasetBuilder(request.session_id)
                .with_metric_type(metric_type)
                .with_model_config(
                    provider=model_provider,
                    model_name=request.model_name,
                    api_key=api_key_to_use
                )
                .with_metric_config(
                    threshold=request.threshold,
                    include_reason=request.include_reason,
                    strict_mode=request.strict_mode
                )
                .build_and_save(
                     confident_api_key=confident_api_key_to_use if request.save_to_cloud else None,
                     alias=f"{request.dataset_alias}_{request.session_id}",
                     local_directory=request.local_directory,
                     force_local=not request.save_to_cloud
                 )
            )
            
            test_case_count = dataset_wrapper.get_test_case_count()
            dataset_location = request.dataset_alias if request.save_to_cloud else request.local_directory
            
            # Store dataset information in session manager if save was successful
            if save_success:
                deepeval_session_manager.set_session_dataset_info(
                    request.session_id,
                    f"{request.dataset_alias}_{request.session_id}",
                    dataset_location,
                    test_case_count
                )
            
            if not save_success:
                # Check if this was an authentication failure for cloud save
                if request.save_to_cloud and request.confident_api_key:
                    logger.error("Dataset created but cloud save failed - likely authentication issue")
                    return DeepEvalResponse(
                        success=False,
                        message="Failed to authenticate with DeepEval cloud. Please check your API key.",
                        dataset_saved=False,
                        dataset_location=dataset_location,
                        test_case_count=test_case_count,
                        execution_time=time.time() - start_time,
                        error_details="Authentication failed - verify your DeepEval API key is correct"
                    )
                else:
                    logger.warning("Dataset created but saving failed")
                    return DeepEvalResponse(
                        success=False,
                        message="Dataset created but saving failed",
                        dataset_saved=False,
                        dataset_location=dataset_location,
                        test_case_count=test_case_count,
                        execution_time=time.time() - start_time,
                        error_details="Failed to save dataset to specified location"
                    )
            
            # Evaluate the dataset
            logger.info(f"Starting evaluation of {test_case_count} test cases")
            evaluation_results = dataset_wrapper.evaluate()
            
            execution_time = time.time() - start_time
            
            # Get the file hash for response
            response_file_hash = None
            try:
                from ..services.extraction_session import extraction_session_manager
                session_data = extraction_session_manager.get_extraction_data(request.session_id)
                if session_data:
                    claims_content = {
                        'extracted_claims': session_data.extracted_claims,
                        'reference_claims': session_data.reference_claims,
                        'model_combinations': session_data.model_combinations
                    }
                    file_content = str(claims_content).encode('utf-8')
                    response_file_hash = deepeval_session_manager.calculate_file_hash(file_content)
            except Exception:
                pass  # Don't fail the response if we can't get the hash
            
            # Try to get cloud URL if this was a cloud evaluation
            logger.info(f"Checking for cloud URL: save_to_cloud={request.save_to_cloud}, confident_api_key={'***' if request.confident_api_key else None}")
            cloud_url = self._get_cloud_test_run_url() if request.save_to_cloud else None
            logger.info(f"Cloud URL result: {cloud_url}")
            
            return DeepEvalResponse(
                success=True,
                message=f"Successfully evaluated {test_case_count} test cases using {request.metric_type}",
                dataset_saved=True,
                dataset_location=dataset_location,
                test_case_count=test_case_count,
                dataset_reused=False,
                evaluation_results=evaluation_results,
                execution_time=execution_time,
                file_hash=response_file_hash,
                cloud_url=cloud_url
            )
            
        except Exception as e:
            logger.error(f"DeepEval evaluation failed: {str(e)}", exc_info=True)
            
            # Check if this is an authentication-related error
            error_str = str(e).lower()
            is_auth_error = any(keyword in error_str for keyword in [
                'login', 'auth', 'api key', 'credential', 'unauthorized', 'forbidden'
            ])
            
            if is_auth_error and request.save_to_cloud and request.confident_api_key:
                message = "Failed to authenticate with Confident AI cloud. Please check your API key."
                error_details = "Authentication failed - verify your Confident AI API key is correct and has proper permissions"
            else:
                message = f"DeepEval evaluation failed: {str(e)}"
                error_details = str(e)
            
            return DeepEvalResponse(
                success=False,
                message=message,
                dataset_saved=False,
                test_case_count=0,
                execution_time=time.time() - start_time,
                error_details=error_details
            )
    
    def evaluate_with_deepeval_async(self, request: DeepEvalRequest, websocket_manager, event_loop=None) -> DeepEvalResponse:
        """
        Create and evaluate a dataset using DeepEval with real-time progress updates via WebSocket.
        
        Args:
            request: DeepEval evaluation request
            websocket_manager: WebSocket manager for sending progress updates
            event_loop: The main event loop for scheduling async operations
            
        Returns:
            DeepEval evaluation response
        """
        import asyncio
        import threading
        
        def send_progress(stage: str, progress: int, message: str, **kwargs):
            """Helper to send progress updates via WebSocket"""
            try:
                # Create a message with progress information
                progress_message = {
                    "type": "deepeval_progress",
                    "stage": stage,
                    "progress": progress,
                    "message": message,
                    **kwargs
                }
                
                # Use the provided event loop or try to get the running one
                main_loop = event_loop
                if main_loop is None:
                    try:
                        main_loop = asyncio.get_running_loop()
                    except RuntimeError:
                        logger.warning("No asyncio event loop available, cannot send progress update")
                        return
                
                # Schedule the coroutine in the main event loop
                future = asyncio.run_coroutine_threadsafe(
                    websocket_manager.send_message(request.session_id, progress_message),
                    main_loop
                )
                
                # Wait for completion with a timeout to avoid blocking indefinitely
                try:
                    future.result(timeout=5.0)  # 5 second timeout
                except Exception as e:
                    logger.warning(f"Failed to send progress update: {str(e)}")
                
            except Exception as e:
                logger.warning(f"Failed to send progress update: {str(e)}")
        
        start_time = time.time()
        
        try:
            # Import DeepEval components and session manager
            from ..utils.create_dataset import DatasetBuilder, MetricType, ModelProvider
            from ..utils.deepeval_session_manager import deepeval_session_manager
            
            # Stage 1: Authentication/Setup
            if request.confident_api_key:
                send_progress("authentication", 10, "Verifying Confident AI cloud connection...")
            else:
                send_progress("authentication", 10, "Preparing local evaluation environment...")
            
            # Store API keys in session if requested
            if request.store_api_keys:
                # Store DeepEval API key
                if request.confident_api_key:
                    deepeval_session_manager.set_session_api_key(
                        request.session_id, 
                        request.confident_api_key
                    )
                
                # Store model API keys - determine which provider this is for
                provider = request.model_provider.lower()
                if provider == 'openai' and request.api_key:
                    deepeval_session_manager.set_session_model_api_keys(
                        request.session_id, openai_api_key=request.api_key
                    )
                elif provider == 'anthropic' and request.api_key:
                    deepeval_session_manager.set_session_model_api_keys(
                        request.session_id, anthropic_api_key=request.api_key
                    )
                elif provider == 'gemini' and request.api_key:
                    deepeval_session_manager.set_session_model_api_keys(
                        request.session_id, gemini_api_key=request.api_key
                    )
                elif provider == 'grok' and request.api_key:
                    deepeval_session_manager.set_session_model_api_keys(
                        request.session_id, grok_api_key=request.api_key
                    )
            
            # If no API key provided but we have one stored, use the stored key
            api_key_to_use = request.api_key
            if not api_key_to_use:
                stored_key = deepeval_session_manager.get_session_model_api_key(
                    request.session_id, request.model_provider.lower()
                )
                if stored_key:
                    api_key_to_use = stored_key
                    send_progress("authentication", 15, f"Using stored {request.model_provider} API key...")
            
            # Similarly for DeepEval API key
            confident_api_key_to_use = request.confident_api_key
            if not confident_api_key_to_use:
                stored_confident_key = deepeval_session_manager.get_session_api_key(request.session_id)
                if stored_confident_key:
                    confident_api_key_to_use = stored_confident_key
                    send_progress("authentication", 20, "Using stored Confident AI API key...")
            
            # Prepare environment for evaluation type
            preparation_success = deepeval_session_manager.prepare_for_evaluation(
                request.session_id,
                request.save_to_cloud
            )
            
            if not preparation_success:
                send_progress("authentication", 0, "Authentication failed", success=False)
                return DeepEvalResponse(
                    success=False,
                    message="Failed to prepare evaluation environment",
                    dataset_saved=False,
                    test_case_count=0,
                    execution_time=time.time() - start_time,
                    error_details="Session preparation failed - check API key configuration"
                )
            
            # Authentication complete
            if request.confident_api_key:
                send_progress("authentication", 100, "Confident AI cloud connection verified!")
            else:
                send_progress("authentication", 100, "Local evaluation environment ready")
            
            # Stage 2: Dataset Creation
            send_progress("dataset", 0, "Creating evaluation dataset from extraction results...")
            
            # Map request values to enum types
            try:
                metric_type = MetricType(request.metric_type.lower())
            except ValueError:
                send_progress("dataset", 0, f"Unsupported metric type: {request.metric_type}", success=False)
                return DeepEvalResponse(
                    success=False,
                    message=f"Unsupported metric type: {request.metric_type}",
                    dataset_saved=False,
                    test_case_count=0,
                    execution_time=time.time() - start_time,
                    error_details=f"Supported metrics: {[m.value for m in MetricType]}"
                )
            
            try:
                model_provider = ModelProvider(request.model_provider.lower())
            except ValueError:
                send_progress("dataset", 0, f"Unsupported model provider: {request.model_provider}", success=False)
                return DeepEvalResponse(
                    success=False,
                    message=f"Unsupported model provider: {request.model_provider}",
                    dataset_saved=False,
                    test_case_count=0,
                    execution_time=time.time() - start_time,
                    error_details=f"Supported providers: {[p.value for p in ModelProvider]}"
                )
            
            send_progress("dataset", 25, "Building dataset structure...")
            
            # Check if we need to recreate the dataset based on file changes
            from ..services.extraction_session import extraction_session_manager
            
            current_file_hash = None
            try:
                session_data = extraction_session_manager.get_extraction_data(request.session_id)
                if session_data:
                    # Calculate hash based on extraction claims data
                    claims_content = {
                        'extracted_claims': session_data.extracted_claims,
                        'reference_claims': session_data.reference_claims,
                        'model_combinations': session_data.model_combinations
                    }
                    file_content = str(claims_content).encode('utf-8')
                    current_file_hash = deepeval_session_manager.calculate_file_hash(file_content)
                    
                    # Check if dataset should be recreated
                    should_recreate, existing_dataset_info = deepeval_session_manager.should_recreate_dataset(
                        request.session_id, current_file_hash
                    )
                    
                    if not should_recreate and existing_dataset_info:
                        send_progress("dataset", 100, "Reusing existing dataset (file unchanged)")
                        
                        # Load existing dataset for evaluation - skip to evaluation stage
                        dataset_wrapper = DatasetBuilder(request.session_id, extraction_session_manager) \
                            .with_metric_type(metric_type) \
                            .with_model_config(
                                provider=model_provider,
                                model_name=request.model_name,
                                api_key=api_key_to_use,
                                temperature=0.0
                            ) \
                            .with_metric_config(
                                threshold=request.threshold,
                                include_reason=request.include_reason,
                                strict_mode=request.strict_mode
                            ) \
                            .build()
                        
                        # Jump to evaluation stage
                        send_progress("evaluation", 0, "Starting evaluation with existing dataset...")
                        evaluation_results = dataset_wrapper.evaluate()
                        send_progress("evaluation", 100, "Evaluation completed successfully!")
                        
                        # Serialize evaluation results to ensure JSON compatibility
                        serialized_results = self._serialize_evaluation_results(evaluation_results)
                        
                        # Try to get cloud URL if this was a cloud evaluation
                        logger.info(f"Checking for cloud URL: save_to_cloud={request.save_to_cloud}, confident_api_key={'***' if request.confident_api_key else None}")
                        cloud_url = self._get_cloud_test_run_url() if request.save_to_cloud else None
                        logger.info(f"Cloud URL result: {cloud_url}")
                        
                        return DeepEvalResponse(
                            success=True,
                            message="DeepEval evaluation completed successfully (reused existing dataset)",
                            dataset_saved=True,
                            dataset_location=existing_dataset_info.get('location'),
                            test_case_count=existing_dataset_info.get('test_case_count', 0),
                            dataset_reused=True,
                            evaluation_results=serialized_results,
                            execution_time=time.time() - start_time,
                            cloud_url=cloud_url,
                            file_hash=current_file_hash
                        )
                    
                    # Store the current file hash for future comparisons
                    deepeval_session_manager.set_session_file_hash(request.session_id, current_file_hash)
                    
            except Exception as e:
                logger.warning(f"Error checking dataset existence: {str(e)}")
                # Continue with normal flow if there's an error
            
            send_progress("dataset", 50, "Processing extraction data...")
            
            # Build and save dataset
            logger.info(f"Building DeepEval dataset for session {request.session_id}")
            dataset_wrapper, save_success = (
                DatasetBuilder(request.session_id)
                .with_metric_type(metric_type)
                .with_model_config(
                    provider=model_provider,
                    model_name=request.model_name,
                    api_key=api_key_to_use
                )
                .with_metric_config(
                    threshold=request.threshold,
                    include_reason=request.include_reason,
                    strict_mode=request.strict_mode
                )
                .build_and_save(
                     confident_api_key=confident_api_key_to_use if request.save_to_cloud else None,
                     alias=f"{request.dataset_alias}_{request.session_id}",
                     local_directory=request.local_directory,
                     force_local=not request.save_to_cloud
                 )
            )
            
            test_case_count = dataset_wrapper.get_test_case_count()
            dataset_location = request.dataset_alias if request.save_to_cloud else request.local_directory
            
            # Store dataset information in session manager if save was successful
            if save_success:
                deepeval_session_manager.set_session_dataset_info(
                    request.session_id,
                    f"{request.dataset_alias}_{request.session_id}",
                    dataset_location,
                    test_case_count
                )
            
            if not save_success:
                send_progress("dataset", 0, "Failed to save dataset", success=False)
                # Check if this was an authentication failure for cloud save
                if request.save_to_cloud and request.confident_api_key:
                    return DeepEvalResponse(
                        success=False,
                        message="Failed to authenticate with DeepEval cloud. Please check your API key.",
                        dataset_saved=False,
                        dataset_location=dataset_location,
                        test_case_count=test_case_count,
                        execution_time=time.time() - start_time,
                        error_details="Authentication failed - verify your DeepEval API key is correct"
                    )
                else:
                    return DeepEvalResponse(
                        success=False,
                        message="Dataset created but saving failed",
                        dataset_saved=False,
                        dataset_location=dataset_location,
                        test_case_count=test_case_count,
                        execution_time=time.time() - start_time,
                        error_details="Failed to save dataset to specified location"
                    )
            
            send_progress("dataset", 100, f"Dataset created successfully with {test_case_count} test cases")
            
            # Stage 3: Evaluation
            send_progress("evaluation", 0, f"Starting evaluation of {test_case_count} test cases...")
            logger.info(f"Starting evaluation of {test_case_count} test cases")
            
            # Add progress callback during evaluation if possible
            send_progress("evaluation", 25, "Initializing metric evaluation...")
            send_progress("evaluation", 50, "Processing test cases...")
            
            evaluation_results = dataset_wrapper.evaluate()
            
            send_progress("evaluation", 100, "Evaluation completed successfully!")
            
            execution_time = time.time() - start_time
            
            # Serialize evaluation results to ensure JSON compatibility
            serialized_results = self._serialize_evaluation_results(evaluation_results)
            
            # Try to get cloud URL if this was a cloud evaluation
            logger.info(f"Checking for cloud URL: save_to_cloud={request.save_to_cloud}, confident_api_key={'***' if request.confident_api_key else None}")
            cloud_url = self._get_cloud_test_run_url() if request.save_to_cloud else None
            logger.info(f"Cloud URL result: {cloud_url}")
            
            return DeepEvalResponse(
                success=True,
                message=f"Successfully evaluated {test_case_count} test cases using {request.metric_type}",
                dataset_saved=True,
                dataset_location=dataset_location,
                test_case_count=test_case_count,
                dataset_reused=False,
                evaluation_results=serialized_results,
                execution_time=execution_time,
                cloud_url=cloud_url,
                file_hash=current_file_hash
            )
            
        except Exception as e:
            logger.error(f"DeepEval evaluation failed: {str(e)}", exc_info=True)
            send_progress("error", 0, f"Evaluation failed: {str(e)}", success=False)
            
            # Check if this is an authentication-related error
            error_str = str(e).lower()
            is_auth_error = any(keyword in error_str for keyword in [
                'login', 'auth', 'api key', 'credential', 'unauthorized', 'forbidden'
            ])
            
            if is_auth_error and request.save_to_cloud and request.confident_api_key:
                message = "Failed to authenticate with Confident AI cloud. Please check your API key."
                error_details = "Authentication failed - verify your Confident AI API key is correct and has proper permissions"
            else:
                message = f"DeepEval evaluation failed: {str(e)}"
                error_details = str(e)
            
            return DeepEvalResponse(
                success=False,
                message=message,
                dataset_saved=False,
                test_case_count=0,
                execution_time=time.time() - start_time,
                error_details=error_details
            )

# Create global service instance
eval_service = EvalService() 