import logging
import time
from functools import wraps
from typing import List, Dict, Any, Optional, Union
import nltk
from rouge_score import rouge_scorer
from pydantic import BaseModel, field_validator

# Configure logging
logger = logging.getLogger(__name__)

class RougeConfig(BaseModel):
    """Configuration for ROUGE score calculation"""
    rouge_types: List[str] = ['rouge1', 'rouge2', 'rougeL']
    use_stemmer: bool = True
    split_summaries: bool = False
    tokenizer: Optional[str] = None
    default_rouge_type: str = 'rougeL'
    cache_enabled: bool = True
    max_cache_size: int = 1000
    
    @field_validator('rouge_types')
    @classmethod
    def validate_rouge_types(cls, v):
        valid_types = ['rouge1', 'rouge2', 'rougeL', 'rougeLsum']
        if not v or not isinstance(v, list):
            raise ValueError("rouge_types must be a non-empty list")
        for rouge_type in v:
            if rouge_type not in valid_types:
                raise ValueError(f"Invalid ROUGE type: {rouge_type}. Valid types: {valid_types}")
        return v
    
    @field_validator('default_rouge_type')
    @classmethod
    def validate_default_rouge_type(cls, v, info):
        if hasattr(info, 'data') and 'rouge_types' in info.data and v not in info.data['rouge_types']:
            raise ValueError("default_rouge_type must be in rouge_types list")
        return v
    
    @field_validator('max_cache_size')
    @classmethod
    def validate_cache_size(cls, v):
        if v < 0:
            raise ValueError("Cache size must be non-negative")
        return v

class RougeResult(BaseModel):
    """Result container for ROUGE score calculation"""
    score: float
    scores_by_type: Dict[str, Dict[str, float]]
    execution_time: float
    cached: bool = False
    metadata: Optional[Dict[str, Any]] = None

def validate_inputs(func):
    """Decorator to validate input texts"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if len(args) >= 2:
            response_text, reference_text = args[0], args[1]
        else:
            response_text = kwargs.get('response_text')
            reference_text = kwargs.get('reference_text')
        
        if not isinstance(response_text, str) or not isinstance(reference_text, str):
            raise TypeError("Both response_text and reference_text must be strings")
        
        if not response_text.strip() or not reference_text.strip():
            logger.warning("Empty or whitespace-only text provided")
        
        return func(self, *args, **kwargs)
    return wrapper

def performance_monitor(func):
    """Decorator to monitor performance"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        try:
            result = func(self, *args, **kwargs)
            execution_time = time.time() - start_time
            
            if isinstance(result, RougeResult):
                result.execution_time = execution_time
            elif isinstance(result, dict) and 'execution_time' in result:
                result['execution_time'] = execution_time
            
            logger.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {str(e)}")
            raise
    return wrapper

class RougeCalculator:
    """
    Professional ROUGE score calculator with configuration, caching, and validation.
    
    Designed for API SDK usage with proper error handling, performance monitoring,
    and extensibility.
    """
    
    def __init__(self, config: Optional[RougeConfig] = None):
        """
        Initialize ROUGE calculator.
        
        Args:
            config: Configuration object for ROUGE calculation
        """
        self.config = config or RougeConfig()
        self._cache: Dict[str, tuple] = {}
        self._scorer = None
        self._initialize_scorer()
    
    def _initialize_scorer(self) -> None:
        """Initialize the ROUGE scorer"""
        try:
            self._scorer = rouge_scorer.RougeScorer(
                self.config.rouge_types, 
                use_stemmer=self.config.use_stemmer,
                split_summaries=self.config.split_summaries,
                tokenizer=self.config.tokenizer
            )
            logger.info(f"ROUGE scorer initialized with types: {self.config.rouge_types}")
        except Exception as e:
            logger.error(f"Failed to initialize ROUGE scorer: {str(e)}")
            raise RuntimeError(f"ROUGE scorer initialization failed: {str(e)}")
    
    def _get_cache_key(self, response_text: str, reference_text: str) -> str:
        """Generate cache key for text pair"""
        return f"{hash(response_text)}:{hash(reference_text)}:{hash(str(self.config.dict()))}"
    
    def _manage_cache(self) -> None:
        """Manage cache size to prevent memory issues"""
        if len(self._cache) > self.config.max_cache_size:
            # Remove oldest entries (simple FIFO)
            excess_count = len(self._cache) - self.config.max_cache_size
            keys_to_remove = list(self._cache.keys())[:excess_count]
            for key in keys_to_remove:
                del self._cache[key]
            logger.debug(f"Cache cleaned: removed {excess_count} entries")
    
    @validate_inputs
    @performance_monitor
    def calculate_score(self, response_text: str, reference_text: str, 
                       rouge_type: Optional[str] = None, return_detailed: bool = False) -> Union[float, RougeResult]:
        """
        Calculate ROUGE score between response text and reference text.
        
        Args:
            response_text: The generated/predicted text
            reference_text: The reference/ground truth text
            rouge_type: Specific ROUGE type to return (defaults to config.default_rouge_type)
            return_detailed: Whether to return detailed result object
            
        Returns:
            ROUGE score (float) or detailed result object
            
        Raises:
            TypeError: If inputs are not strings
            RuntimeError: If scorer is not properly initialized
            ValueError: If calculation fails or invalid rouge_type
        """
        if self._scorer is None:
            raise RuntimeError("ROUGE scorer not properly initialized")
        
        # Use default rouge type if not specified
        rouge_type = rouge_type or self.config.default_rouge_type
        
        if rouge_type not in self.config.rouge_types:
            raise ValueError(f"Rouge type {rouge_type} not in configured types: {self.config.rouge_types}")
        
        # Check cache
        cache_key = self._get_cache_key(response_text, reference_text) if self.config.cache_enabled else None
        
        if cache_key and cache_key in self._cache:
            cached_score, cached_all_scores = self._cache[cache_key]
            logger.debug("Score retrieved from cache")
            
            if return_detailed:
                return RougeResult(
                    score=cached_score.get(rouge_type, 0.0),
                    scores_by_type=cached_all_scores,
                    execution_time=0.0,
                    cached=True,
                    metadata={"cache_key": cache_key}
                )
            return cached_score.get(rouge_type, 0.0)
        
        try:
            # Calculate ROUGE scores
            scores = self._scorer.score(str(reference_text), response_text)
            
            # Extract scores for all types
            all_scores = {}
            rouge_f1_scores = {}
            
            for rtype in self.config.rouge_types:
                if rtype in scores:
                    all_scores[rtype] = {
                        'precision': scores[rtype].precision,
                        'recall': scores[rtype].recall,
                        'fmeasure': scores[rtype].fmeasure
                    }
                    rouge_f1_scores[rtype] = scores[rtype].fmeasure
            
            # Cache result
            if self.config.cache_enabled and cache_key:
                self._cache[cache_key] = (rouge_f1_scores, all_scores)
                self._manage_cache()
            
            if return_detailed:
                return RougeResult(
                    score=rouge_f1_scores.get(rouge_type, 0.0),
                    scores_by_type=all_scores,
                    execution_time=0.0,  # Will be set by decorator
                    cached=False,
                    metadata={
                        "rouge_type": rouge_type,
                        "rouge_types": self.config.rouge_types,
                        "use_stemmer": self.config.use_stemmer,
                        "input_lengths": {
                            "response": len(response_text),
                            "reference": len(reference_text)
                        },
                        "config": self.config.dict()
                    }
                )
            
            return rouge_f1_scores.get(rouge_type, 0.0)
            
        except Exception as e:
            logger.error(f"ROUGE calculation failed: {str(e)}")
            raise ValueError(f"Failed to calculate ROUGE score: {str(e)}")
    
    @validate_inputs
    @performance_monitor
    def calculate_batch(self, response_texts: List[str], reference_texts: List[str],
                       rouge_type: Optional[str] = None, return_detailed: bool = False) -> Union[List[float], List[RougeResult]]:
        """
        Calculate ROUGE scores for a batch of text pairs.
        
        Args:
            response_texts: List of generated/predicted texts
            reference_texts: List of reference/ground truth texts
            rouge_type: Specific ROUGE type to return (defaults to config.default_rouge_type)
            return_detailed: Whether to return detailed result objects
            
        Returns:
            List of ROUGE scores or detailed result objects
            
        Raises:
            ValueError: If input lists have different lengths
        """
        if len(response_texts) != len(reference_texts):
            raise ValueError("Response and reference text lists must have the same length")
        
        results = []
        cache_hits = 0
        
        for i, (response, reference) in enumerate(zip(response_texts, reference_texts)):
            try:
                result = self.calculate_score(response, reference, rouge_type=rouge_type, return_detailed=return_detailed)
                if return_detailed and result.cached:
                    cache_hits += 1
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to calculate score for pair {i}: {str(e)}")
                if return_detailed:
                    results.append(RougeResult(score=0.0, scores_by_type={}, execution_time=0.0, 
                                             metadata={"error": str(e)}))
                else:
                    results.append(0.0)
        
        logger.info(f"Batch calculation completed: {len(results)} pairs, {cache_hits} cache hits")
        return results
    
    def clear_cache(self) -> None:
        """Clear the calculation cache"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self._cache),
            "max_cache_size": self.config.max_cache_size,
            "cache_enabled": self.config.cache_enabled
        }
    
    def update_config(self, **kwargs) -> None:
        """Update configuration parameters"""
        old_rouge_types = self.config.rouge_types
        old_use_stemmer = self.config.use_stemmer
        
        config_dict = self.config.dict()
        config_dict.update(kwargs)
        self.config = RougeConfig(**config_dict)
        
        # Reinitialize scorer if critical parameters changed
        if (self.config.rouge_types != old_rouge_types or 
            self.config.use_stemmer != old_use_stemmer):
            self._initialize_scorer()
        
        logger.info(f"Configuration updated: {kwargs}")

# Convenience functions for backward compatibility
def calculate_rouge_score(response_text: str, reference_text: str, rouge_type: str = 'rouge-l') -> float:
    """
    Calculate ROUGE score between response text and reference text.
    
    Args:
        response_text: The generated/predicted text
        reference_text: The reference/ground truth text
        rouge_type: Type of ROUGE score ('rouge-1', 'rouge-2', 'rouge-l')
        
    Returns:
        float: ROUGE score between 0 and 1
    """
    # Map old naming convention to new
    rouge_type_mapping = {
        'rouge-1': 'rouge1',
        'rouge-2': 'rouge2', 
        'rouge-l': 'rougeL',
        'rouge-lsum': 'rougeLsum'
    }
    
    mapped_type = rouge_type_mapping.get(rouge_type.lower(), rouge_type)
    
    # Create config with the specified rouge type
    config = RougeConfig(
        rouge_types=[mapped_type],
        default_rouge_type=mapped_type
    )
    calculator = RougeCalculator(config=config)
    return calculator.calculate_score(response_text, reference_text, rouge_type=mapped_type)

def calculate_rouge_score_batch(response_texts: List[str], reference_texts: List[str], rouge_type: str = 'rouge-l') -> List[float]:
    """
    Calculate ROUGE scores for a batch of text pairs.
    
    Args:
        response_texts: List of generated/predicted texts
        reference_texts: List of reference/ground truth texts
        rouge_type: Type of ROUGE score ('rouge-1', 'rouge-2', 'rouge-l')
        
    Returns:
        List[float]: List of ROUGE scores
    """
    # Map old naming convention to new
    rouge_type_mapping = {
        'rouge-1': 'rouge1',
        'rouge-2': 'rouge2',
        'rouge-l': 'rougeL',
        'rouge-lsum': 'rougeLsum'
    }
    
    mapped_type = rouge_type_mapping.get(rouge_type.lower(), rouge_type)
    
    # Create config with the specified rouge type
    config = RougeConfig(
        rouge_types=[mapped_type],
        default_rouge_type=mapped_type
    )
    calculator = RougeCalculator(config=config)
    return calculator.calculate_batch(response_texts, reference_texts, rouge_type=mapped_type)
