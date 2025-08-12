"""
Hallucination metric calculation using DeepEval

This module provides hallucination evaluation capabilities using DeepEval's
HallucinationMetric for detecting factually incorrect information by comparing
the actual_output to the provided context.
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


class HallucinationConfig(BaseModel):
    """Configuration for hallucination metric calculation"""
    
    # Model configuration
    model_provider: str = Field(default="openai", description="Model provider (openai, gemini)")
    model_name: str = Field(default="gpt-4o", description="Name of the model to use for evaluation")
    api_key: str = Field(default="", description="API key for the model provider")
    
    # Metric configuration
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Hallucination threshold")
    include_reason: bool = Field(default=True, description="Include reasoning in results")
    strict_mode: bool = Field(default=False, description="Binary metric score: 0 for perfection, 1 otherwise")
    async_mode: bool = Field(default=True, description="Enable concurrent execution")
    verbose_mode: bool = Field(default=False, description="Print intermediate calculation steps")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="Model temperature (fixed at 0.0 for consistency)")
    
    # DeepEval configuration
    confident_api_key: Optional[str] = Field(default=None, description="Confident AI API key for cloud features")
    batch_size: int = Field(default=10, ge=1, le=100, description="Batch size for evaluation")
    
    # Performance configuration
    cache_enabled: bool = Field(default=True, description="Enable result caching")
    max_cache_size: int = Field(default=1000, description="Maximum cache entries")


@dataclass
class HallucinationResult:
    """Result container for hallucination evaluation"""
    score: float
    execution_time: float
    cached: bool = False
    detailed_results: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class HallucinationCalculator:
    """
    Calculator for hallucination metric using DeepEval.
    
    Detects factually incorrect information by comparing the model output 
    to the provided context. Uses LLM-as-a-judge to determine factual correctness.
    """
    
    def __init__(self, config: HallucinationConfig):
        """
        Initialize hallucination calculator.
        
        Args:
            config: Hallucination calculation configuration
        """
        self.config = config
        self._cache: Dict[str, float] = {}
        
        # Validate API key for non-free models
        if (config.model_name != 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' and 
            not config.api_key.strip()):
            raise ValueError(f"API key is required for model '{config.model_name}' with provider '{config.model_provider}'")
        
        self._model_provider = self._parse_model_provider(config.model_provider)
        logger.info(f"HallucinationCalculator initialized with {config.model_provider} model: {config.model_name}")
    
    def _parse_model_provider(self, provider_str: str) -> ModelProvider:
        """Parse model provider string to enum."""
        provider_map = {
            "openai": ModelProvider.OPENAI,
            "gemini": ModelProvider.GEMINI,
            "anthropic": ModelProvider.ANTHROPIC,
        }
        
        if provider_str.lower() not in provider_map:
            logger.warning(f"Unsupported model provider '{provider_str}', defaulting to OpenAI")
            return ModelProvider.OPENAI
        
        return provider_map[provider_str.lower()]
    
    def _create_cache_key(self, response_text: str, context: str) -> str:
        """Create a cache key for the given inputs."""
        if not self.config.cache_enabled:
            return None
        
        # Create a hash-based key
        import hashlib
        combined = f"{response_text}:{context}:{self.config.model_name}:{self.config.threshold}:{self.config.strict_mode}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _manage_cache(self) -> None:
        """Manage cache size by removing oldest entries."""
        if len(self._cache) > self.config.max_cache_size:
            # Remove oldest 20% of entries
            items_to_remove = len(self._cache) - int(self.config.max_cache_size * 0.8)
            for _ in range(items_to_remove):
                self._cache.pop(next(iter(self._cache)))
    
    def calculate_score(
        self, 
        response_text: str, 
        context: str,
        input_text: Optional[str] = None,
        return_detailed: bool = False
    ) -> Union[float, HallucinationResult]:
        """
        Calculate hallucination score for a single response-context pair.
        
        Args:
            response_text: The model's output to evaluate
            context: The context the response should be grounded in
            input_text: Optional input text (required for test case but not used in calculation)
            return_detailed: Whether to return detailed results
            
        Returns:
            Hallucination score (0-1) or detailed result object
        """
        start_time = time.time()
        
        # Input validation
        if not response_text or not response_text.strip():
            raise ValueError("Response text cannot be empty")
        
        if not context or not context.strip():
            raise ValueError("Context cannot be empty for hallucination evaluation")
        
        # Check cache
        cache_key = self._create_cache_key(response_text, context)
        if cache_key and cache_key in self._cache:
            cached_score = self._cache[cache_key]
            logger.debug("Hallucination score retrieved from cache")
            
            if return_detailed:
                return HallucinationResult(
                    score=cached_score,
                    execution_time=time.time() - start_time,
                    cached=True,
                    metadata={"cache_key": cache_key}
                )
            return cached_score
        
        try:
            # Create temporary session data for evaluation
            session_id = f"temp_hallucination_{int(time.time())}"
            
            # Store temporary data in session manager
            extraction_session_manager.store_extraction_data(
                session_id=session_id,
                extracted_claims=[response_text],
                reference_claims=[context],
                metadata={"metric_type": "hallucination", "temporary": True}
            )
            
            try:
                # Create dataset using the builder
                dataset = (DatasetBuilder(session_id)
                          .with_metric_type(MetricType.HALLUCINATION)
                          .with_model_config(
                              provider=self._model_provider,
                              model_name=self.config.model_name,
                              api_key=self.config.api_key,
                              temperature=self.config.temperature
                          )
                          .with_metric_config(
                              threshold=self.config.threshold,
                              include_reason=self.config.include_reason,
                              strict_mode=self.config.strict_mode
                          )
                          .build())
                
                # Run evaluation
                eval_results = dataset.evaluate(batch_size=1)
                
                # Extract score from results
                if eval_results and eval_results.get("results"):
                    # DeepEval results structure may vary, adapt as needed
                    first_result = eval_results["results"][0]
                    hallucination_score = getattr(first_result, 'score', 0.0)
                else:
                    logger.warning("No results returned from hallucination evaluation")
                    hallucination_score = 0.0
                
                # Cache the result
                if self.config.cache_enabled and cache_key:
                    self._cache[cache_key] = hallucination_score
                    self._manage_cache()
                
                execution_time = time.time() - start_time
                
                if return_detailed:
                    return HallucinationResult(
                        score=hallucination_score,
                        execution_time=execution_time,
                        cached=False,
                        detailed_results=eval_results.get("results"),
                        metadata={
                            "model_config": eval_results.get("model_config"),
                            "metric_config": eval_results.get("metric_config"),
                            "input_lengths": {
                                "response": len(response_text),
                                "context": len(context)
                            },
                            "config": self.config.dict()
                        }
                    )
                
                return hallucination_score
                
            finally:
                # Clean up temporary session
                extraction_session_manager.remove_session(session_id)
                
        except Exception as e:
            logger.error(f"Hallucination calculation failed: {str(e)}")
            raise ValueError(f"Failed to calculate hallucination score: {str(e)}")
    
    def calculate_batch(
        self, 
        response_texts: List[str], 
        contexts: List[str],
        input_texts: Optional[List[str]] = None,
        return_detailed: bool = False
    ) -> Union[List[float], List[HallucinationResult]]:
        """
        Calculate hallucination scores for multiple response-context pairs.
        
        Args:
            response_texts: List of model outputs to evaluate
            contexts: List of contexts the responses should be grounded in
            input_texts: Optional list of input texts (required for test cases but not used in calculation)
            return_detailed: Whether to return detailed results
            
        Returns:
            List of hallucination scores or detailed result objects
        """
        if len(response_texts) != len(contexts):
            raise ValueError("Response texts and contexts must have the same length")
        
        if input_texts is not None and len(input_texts) != len(response_texts):
            raise ValueError("Input texts length must match response texts length")
        
        if not response_texts:
            raise ValueError("Input lists cannot be empty")
        
        start_time = time.time()
        
        try:
            # Create temporary session data for batch evaluation
            session_id = f"temp_hallucination_batch_{int(time.time())}"
            
            # Store batch data in session manager
            extraction_session_manager.store_extraction_data(
                session_id=session_id,
                extracted_claims=response_texts,
                reference_claims=contexts,
                metadata={"metric_type": "hallucination", "temporary": True, "batch_size": len(response_texts)}
            )
            
            try:
                # Create dataset using the builder
                dataset = (DatasetBuilder(session_id)
                          .with_metric_type(MetricType.HALLUCINATION)
                          .with_model_config(
                              provider=self._model_provider,
                              model_name=self.config.model_name,
                              api_key=self.config.api_key,
                              temperature=self.config.temperature
                          )
                          .with_metric_config(
                              threshold=self.config.threshold,
                              include_reason=self.config.include_reason,
                              strict_mode=self.config.strict_mode
                          )
                          .build())
                
                # Run batch evaluation
                eval_results = dataset.evaluate(batch_size=self.config.batch_size)
                
                # Extract scores from results
                scores = []
                detailed_results = []
                
                if eval_results and eval_results.get("results"):
                    for result in eval_results["results"]:
                        score = getattr(result, 'score', 0.0)
                        scores.append(score)
                        
                        if return_detailed:
                            detailed_results.append(HallucinationResult(
                                score=score,
                                execution_time=(time.time() - start_time) / len(response_texts),
                                cached=False,
                                detailed_results=[result],
                                metadata={
                                    "batch_index": len(scores) - 1,
                                    "config": self.config.dict()
                                }
                            ))
                else:
                    logger.warning("No results returned from batch hallucination evaluation")
                    scores = [0.0] * len(response_texts)
                    if return_detailed:
                        detailed_results = [HallucinationResult(score=0.0, execution_time=0.0) 
                                          for _ in response_texts]
                
                return detailed_results if return_detailed else scores
                
            finally:
                # Clean up temporary session
                extraction_session_manager.remove_session(session_id)
                
        except Exception as e:
            logger.error(f"Batch hallucination calculation failed: {str(e)}")
            raise ValueError(f"Failed to calculate batch hallucination scores: {str(e)}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the cache state."""
        return {
            "cache_enabled": self.config.cache_enabled,
            "cache_size": len(self._cache),
            "max_cache_size": self.config.max_cache_size,
            "cache_hit_ratio": getattr(self, '_cache_hits', 0) / max(getattr(self, '_cache_attempts', 1), 1)
        }
    
    def clear_cache(self) -> None:
        """Clear the calculation cache."""
        self._cache.clear()
        logger.info("Hallucination calculator cache cleared")
