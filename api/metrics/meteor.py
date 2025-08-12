import logging
import time
from functools import wraps
from typing import List, Dict, Any, Optional, Union
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.translate.meteor_score import meteor_score
from pydantic import BaseModel, field_validator

# Configure logging
logger = logging.getLogger(__name__)

class MeteorConfig(BaseModel):
    """Configuration for METEOR score calculation"""
    alpha: float = 0.9
    beta: float = 3.0
    gamma: float = 0.5
    preprocess: bool = True
    cache_enabled: bool = True
    max_cache_size: int = 1000
    
    @field_validator('alpha', 'beta', 'gamma')
    @classmethod
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError("Alpha, beta, and gamma must be positive")
        return v
    
    @field_validator('max_cache_size')
    @classmethod
    def validate_cache_size(cls, v):
        if v < 0:
            raise ValueError("Cache size must be non-negative")
        return v

class MeteorResult(BaseModel):
    """Result container for METEOR score calculation"""
    score: float
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
            
            if isinstance(result, MeteorResult):
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

class MeteorCalculator:
    """
    Professional METEOR score calculator with configuration, caching, and validation.
    
    Designed for API SDK usage with proper error handling, performance monitoring,
    and extensibility.
    """
    
    def __init__(self, config: Optional[MeteorConfig] = None):
        """
        Initialize METEOR calculator.
        
        Args:
            config: Configuration object for METEOR calculation
        """
        self.config = config or MeteorConfig()
        self._cache: Dict[str, float] = {}
        self._nltk_initialized = False
        self._initialize_nltk()
    
    def _initialize_nltk(self) -> None:
        """Initialize NLTK dependencies"""
        try:
            # Download required NLTK data
            nltk.download('punkt_tab', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            wordnet.ensure_loaded()
            self._nltk_initialized = True
            logger.info("NLTK dependencies initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NLTK dependencies: {str(e)}")
            raise RuntimeError(f"NLTK initialization failed: {str(e)}")
    
    def _get_cache_key(self, response_text: str, reference_text: str) -> str:
        """Generate cache key for text pair"""
        return f"{hash(response_text)}:{hash(reference_text)}"
    
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
                       return_detailed: bool = False) -> Union[float, MeteorResult]:
        """
        Calculate METEOR score between response text and reference text.
        
        Args:
            response_text: The generated/predicted text
            reference_text: The reference/ground truth text
            return_detailed: Whether to return detailed result object
            
        Returns:
            METEOR score (float) or detailed result object
            
        Raises:
            TypeError: If inputs are not strings
            RuntimeError: If NLTK is not properly initialized
            ValueError: If calculation fails
        """
        if not self._nltk_initialized:
            raise RuntimeError("NLTK not properly initialized")
        
        # Check cache
        cache_key = self._get_cache_key(response_text, reference_text) if self.config.cache_enabled else None
        cached_score = None
        
        if cache_key and cache_key in self._cache:
            cached_score = self._cache[cache_key]
            logger.debug("Score retrieved from cache")
            
            if return_detailed:
                return MeteorResult(
                    score=cached_score,
                    execution_time=0.0,
                    cached=True,
                    metadata={"cache_key": cache_key}
                )
            return cached_score
        
        try:
            # Preprocess if enabled
            if self.config.preprocess:
                response_text = response_text.strip()
                reference_text = reference_text.strip()
            
            # Tokenize
            response_tokens = word_tokenize(response_text)
            reference_tokens = word_tokenize(reference_text)
            
            # Calculate METEOR score
            score = meteor_score([response_tokens], reference_tokens,
                               alpha=self.config.alpha,
                               beta=self.config.beta,
                               gamma=self.config.gamma)
            
            # Cache result
            if self.config.cache_enabled and cache_key:
                self._cache[cache_key] = score
                self._manage_cache()
            
            if return_detailed:
                return MeteorResult(
                    score=score,
                    execution_time=0.0,  # Will be set by decorator
                    cached=False,
                    metadata={
                        "response_tokens_count": len(response_tokens),
                        "reference_tokens_count": len(reference_tokens),
                        "config": self.config.dict()
                    }
                )
            
            return score
            
        except Exception as e:
            logger.error(f"METEOR calculation failed: {str(e)}")
            raise ValueError(f"Failed to calculate METEOR score: {str(e)}")
    
    @validate_inputs
    @performance_monitor
    def calculate_batch(self, response_texts: List[str], reference_texts: List[str],
                       return_detailed: bool = False) -> Union[List[float], List[MeteorResult]]:
        """
        Calculate METEOR scores for a batch of text pairs.
        
        Args:
            response_texts: List of generated/predicted texts
            reference_texts: List of reference/ground truth texts
            return_detailed: Whether to return detailed result objects
            
        Returns:
            List of METEOR scores or detailed result objects
            
        Raises:
            ValueError: If input lists have different lengths
        """
        if len(response_texts) != len(reference_texts):
            raise ValueError("Response and reference text lists must have the same length")
        
        results = []
        cache_hits = 0
        
        for i, (response, reference) in enumerate(zip(response_texts, reference_texts)):
            try:
                result = self.calculate_score(response, reference, return_detailed=return_detailed)
                if return_detailed and result.cached:
                    cache_hits += 1
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to calculate score for pair {i}: {str(e)}")
                # Return 0.0 for failed calculations or re-raise based on config
                if return_detailed:
                    results.append(MeteorResult(score=0.0, execution_time=0.0, 
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
        config_dict = self.config.dict()
        config_dict.update(kwargs)
        self.config = MeteorConfig(**config_dict)
        logger.info(f"Configuration updated: {kwargs}")

# Convenience functions for backward compatibility
def calculate_meteor_score(response_text: str, reference_text: str) -> float:
    """
    Calculate METEOR score between response text and reference text.
    
    Args:
        response_text: The generated/predicted text
        reference_text: The reference/ground truth text
        
    Returns:
        float: METEOR score between 0 and 1
    """
    calculator = MeteorCalculator()
    return calculator.calculate_score(response_text, reference_text)

def calculate_meteor_score_batch(response_texts: List[str], reference_texts: List[str]) -> List[float]:
    """
    Calculate METEOR scores for a batch of text pairs.
    
    Args:
        response_texts: List of generated/predicted texts
        reference_texts: List of reference/ground truth texts
        
    Returns:
        List[float]: List of METEOR scores
    """
    calculator = MeteorCalculator()
    return calculator.calculate_batch(response_texts, reference_texts) 