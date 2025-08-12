"""
Answer Relevancy metric calculation using DeepEval

This module provides answer relevancy evaluation capabilities using DeepEval's
AnswerRelevancyMetric for measuring how relevant the actual_output of your LLM 
application is compared to the provided input.
"""

import logging
import time
from typing import List, Union, Optional, Dict, Any
from dataclasses import dataclass

from pydantic import BaseModel, Field

from ..utils.create_dataset import (
    DatasetBuilder, MetricType, ModelProvider, ModelConfig, MetricConfig,
    EvaluationDatasetWrapper
)
from ..services.extraction_session import extraction_session_manager

logger = logging.getLogger(__name__)


class AnswerRelevancyConfig(BaseModel):
    """Configuration for Answer Relevancy metric calculation."""
    
    # Model configuration
    model_provider: ModelProvider = Field(default=ModelProvider.OPENAI, description="LLM provider for evaluation")
    model_name: str = Field(default="gpt-4o", description="Model name to use for evaluation")
    api_key: str = Field(description="API key for the model provider")
    
    # Metric configuration
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum passing threshold")
    include_reason: bool = Field(default=True, description="Whether to include reasoning in output")
    strict_mode: bool = Field(default=False, description="Binary scoring mode (1 or 0)")
    async_mode: bool = Field(default=True, description="Enable concurrent execution")
    verbose_mode: bool = Field(default=False, description="Print intermediate steps")
    
    # Performance settings
    timeout_seconds: int = Field(default=120, description="Timeout for metric calculation")
    max_retries: int = Field(default=3, description="Maximum number of retries on failure")


@dataclass
class AnswerRelevancyResult:
    """Result of Answer Relevancy metric calculation."""
    
    # Core results
    score: float
    reason: Optional[str] = None
    
    # Metadata
    test_case_count: int = 0
    execution_time: float = 0.0
    dataset_saved: bool = False
    dataset_location: Optional[str] = None
    
    # Performance metrics
    success_rate: float = 0.0
    failed_cases: int = 0
    average_score: float = 0.0
    
    # Error handling
    errors: List[str] = None
    
    def __post_init__(self):
        """Initialize errors list if None."""
        if self.errors is None:
            self.errors = []


class AnswerRelevancyCalculator:
    """Calculator for Answer Relevancy metric using DeepEval."""
    
    def __init__(self, config: AnswerRelevancyConfig):
        """
        Initialize the Answer Relevancy calculator.
        
        Args:
            config: Configuration for the calculator
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def calculate_score(
        self, 
        response_text: str, 
        reference_text: str = None, 
        input_text: str = None,
        return_detailed: bool = False
    ) -> Union[float, AnswerRelevancyResult]:
        """
        Calculate Answer Relevancy score for a single text pair.
        
        Args:
            response_text: The actual output from the LLM
            reference_text: Not used for Answer Relevancy (referenceless metric)
            input_text: The input/question for relevancy evaluation
            return_detailed: Whether to return detailed results
            
        Returns:
            Float score or detailed AnswerRelevancyResult
        """
        start_time = time.time()
        
        try:
            if not input_text:
                raise ValueError("input_text is required for Answer Relevancy evaluation")
            
            # Create temporary session for single calculation
            temp_session_id = f"temp_answer_relevancy_{int(time.time())}"
            
            # Store temporary data
            extraction_session_manager.store_extraction_data(
                session_id=temp_session_id,
                extracted_claims=[response_text],
                reference_claims=[input_text],  # Use input as reference for dataset creation
                model_combinations=[{"model": "temp", "method": "direct"}]
            )
            
            # Create dataset and evaluate
            dataset_wrapper, save_success = (
                DatasetBuilder(temp_session_id)
                .with_metric_type(MetricType.ANSWER_RELEVANCY)
                .with_model_config(
                    provider=self.config.model_provider,
                    model_name=self.config.model_name,
                    api_key=self.config.api_key
                )
                .with_metric_config(
                    threshold=self.config.threshold,
                    include_reason=self.config.include_reason,
                    strict_mode=self.config.strict_mode
                )
                .build_and_save(local_directory="./temp-answer-relevancy", force_local=True)
            )
            
            if not save_success:
                raise RuntimeError("Failed to create evaluation dataset")
            
            # Run evaluation
            evaluation_results = dataset_wrapper.evaluate()
            
            # Extract results
            test_results = evaluation_results.test_results if hasattr(evaluation_results, 'test_results') else []
            
            if not test_results:
                raise RuntimeError("No evaluation results obtained")
            
            # Get first result (single test case)
            first_result = test_results[0]
            score = getattr(first_result, 'score', 0.0)
            reason = getattr(first_result, 'reason', None) if self.config.include_reason else None
            
            execution_time = time.time() - start_time
            
            # Clean up temporary session
            extraction_session_manager.clear_session(temp_session_id)
            
            if return_detailed:
                return AnswerRelevancyResult(
                    score=score,
                    reason=reason,
                    test_case_count=1,
                    execution_time=execution_time,
                    dataset_saved=save_success,
                    success_rate=1.0,
                    average_score=score
                )
            
            return score
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Answer Relevancy calculation failed: {str(e)}"
            self.logger.error(error_msg)
            
            # Clean up on error
            try:
                extraction_session_manager.clear_session(temp_session_id)
            except:
                pass
            
            if return_detailed:
                return AnswerRelevancyResult(
                    score=0.0,
                    execution_time=execution_time,
                    errors=[error_msg],
                    failed_cases=1
                )
            
            raise Exception(error_msg)
    
    def calculate_batch(
        self, 
        response_texts: List[str], 
        reference_texts: List[str] = None,
        input_texts: List[str] = None,
        return_detailed: bool = False
    ) -> Union[List[float], AnswerRelevancyResult]:
        """
        Calculate Answer Relevancy scores for multiple text pairs.
        
        Args:
            response_texts: List of actual outputs from the LLM
            reference_texts: Not used for Answer Relevancy (referenceless metric)
            input_texts: List of inputs/questions for relevancy evaluation
            return_detailed: Whether to return detailed results
            
        Returns:
            List of float scores or detailed AnswerRelevancyResult
        """
        start_time = time.time()
        
        try:
            if not input_texts:
                raise ValueError("input_texts are required for Answer Relevancy evaluation")
                
            if len(response_texts) != len(input_texts):
                raise ValueError("response_texts and input_texts must have the same length")
            
            # Create temporary session for batch calculation
            temp_session_id = f"temp_batch_answer_relevancy_{int(time.time())}"
            
            # Store temporary data
            extraction_session_manager.store_extraction_data(
                session_id=temp_session_id,
                extracted_claims=response_texts,
                reference_claims=input_texts,  # Use inputs as references for dataset creation
                model_combinations=[{"model": "temp", "method": "batch"}] * len(response_texts)
            )
            
            # Create dataset and evaluate
            dataset_wrapper, save_success = (
                DatasetBuilder(temp_session_id)
                .with_metric_type(MetricType.ANSWER_RELEVANCY)
                .with_model_config(
                    provider=self.config.model_provider,
                    model_name=self.config.model_name,
                    api_key=self.config.api_key
                )
                .with_metric_config(
                    threshold=self.config.threshold,
                    include_reason=self.config.include_reason,
                    strict_mode=self.config.strict_mode
                )
                .build_and_save(local_directory="./temp-batch-answer-relevancy", force_local=True)
            )
            
            if not save_success:
                raise RuntimeError("Failed to create evaluation dataset")
            
            # Run evaluation
            evaluation_results = dataset_wrapper.evaluate()
            
            # Extract results
            test_results = evaluation_results.test_results if hasattr(evaluation_results, 'test_results') else []
            
            scores = []
            reasons = []
            errors = []
            failed_cases = 0
            
            for i, result in enumerate(test_results):
                try:
                    score = getattr(result, 'score', 0.0)
                    reason = getattr(result, 'reason', None) if self.config.include_reason else None
                    scores.append(score)
                    reasons.append(reason)
                except Exception as e:
                    scores.append(0.0)
                    reasons.append(None)
                    errors.append(f"Case {i}: {str(e)}")
                    failed_cases += 1
            
            execution_time = time.time() - start_time
            success_rate = (len(scores) - failed_cases) / len(scores) if scores else 0.0
            average_score = sum(scores) / len(scores) if scores else 0.0
            
            # Clean up temporary session
            extraction_session_manager.clear_session(temp_session_id)
            
            if return_detailed:
                return AnswerRelevancyResult(
                    score=average_score,
                    test_case_count=len(response_texts),
                    execution_time=execution_time,
                    dataset_saved=save_success,
                    success_rate=success_rate,
                    failed_cases=failed_cases,
                    average_score=average_score,
                    errors=errors
                )
            
            return scores
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Batch Answer Relevancy calculation failed: {str(e)}"
            self.logger.error(error_msg)
            
            # Clean up on error
            try:
                extraction_session_manager.clear_session(temp_session_id)
            except:
                pass
            
            if return_detailed:
                return AnswerRelevancyResult(
                    score=0.0,
                    execution_time=execution_time,
                    errors=[error_msg],
                    failed_cases=len(response_texts) if response_texts else 0
                )
            
            raise Exception(error_msg)
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information."""
        return {
            "cache_enabled": False,
            "cache_size": 0,
            "hit_rate": 0.0
        }
    
    def clear_cache(self) -> int:
        """Clear cache and return number of cleared entries."""
        return 0


# Convenience functions for backward compatibility
def calculate_answer_relevancy_score(
    response_text: str,
    input_text: str,
    model_provider: ModelProvider = ModelProvider.OPENAI,
    model_name: str = "gpt-4o",
    api_key: str = "",
    threshold: float = 0.5,
    include_reason: bool = True,
    return_detailed: bool = False
) -> Union[float, AnswerRelevancyResult]:
    """
    Convenience function to calculate Answer Relevancy score.
    
    Args:
        response_text: The actual output from the LLM
        input_text: The input/question for relevancy evaluation
        model_provider: LLM provider for evaluation
        model_name: Model name to use for evaluation
        api_key: API key for the model provider
        threshold: Minimum passing threshold
        include_reason: Whether to include reasoning in output
        return_detailed: Whether to return detailed results
        
    Returns:
        Float score or detailed AnswerRelevancyResult
    """
    config = AnswerRelevancyConfig(
        model_provider=model_provider,
        model_name=model_name,
        api_key=api_key,
        threshold=threshold,
        include_reason=include_reason
    )
    
    calculator = AnswerRelevancyCalculator(config)
    return calculator.calculate_score(
        response_text=response_text,
        input_text=input_text,
        return_detailed=return_detailed
    )


def calculate_answer_relevancy_score_batch(
    response_texts: List[str],
    input_texts: List[str],
    model_provider: ModelProvider = ModelProvider.OPENAI,
    model_name: str = "gpt-4o",
    api_key: str = "",
    threshold: float = 0.5,
    include_reason: bool = True,
    return_detailed: bool = False
) -> Union[List[float], AnswerRelevancyResult]:
    """
    Convenience function to calculate Answer Relevancy scores for multiple pairs.
    
    Args:
        response_texts: List of actual outputs from the LLM
        input_texts: List of inputs/questions for relevancy evaluation
        model_provider: LLM provider for evaluation
        model_name: Model name to use for evaluation
        api_key: API key for the model provider
        threshold: Minimum passing threshold
        include_reason: Whether to include reasoning in output
        return_detailed: Whether to return detailed results
        
    Returns:
        List of float scores or detailed AnswerRelevancyResult
    """
    config = AnswerRelevancyConfig(
        model_provider=model_provider,
        model_name=model_name,
        api_key=api_key,
        threshold=threshold,
        include_reason=include_reason
    )
    
    calculator = AnswerRelevancyCalculator(config)
    return calculator.calculate_batch(
        response_texts=response_texts,
        input_texts=input_texts,
        return_detailed=return_detailed
    )
