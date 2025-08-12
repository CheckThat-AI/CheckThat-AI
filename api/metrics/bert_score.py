import logging
import time
from functools import wraps
from typing import List, Dict, Any, Optional, Union
from bert_score import score
from pydantic import BaseModel, field_validator

# Configure logging
logger = logging.getLogger(__name__)

class BertConfig(BaseModel):
    """Configuration for BERT score calculation"""
    language: str = "en"
    model_type: Optional[str] = None
    num_layers: Optional[int] = None
    verbose: bool = False
    idf: bool = False
    device: Optional[str] = None
    batch_size: int = 64
    nthreads: int = 4
    all_layers: bool = False
    cache_enabled: bool = True
    max_cache_size: int = 1000
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Language must be a non-empty string")
        return v
    
    @field_validator('batch_size', 'nthreads')
    @classmethod
    def validate_positive_int(cls, v):
        if v <= 0:
            raise ValueError("Batch size and nthreads must be positive integers")
        return v
    
    @field_validator('max_cache_size')
    @classmethod
    def validate_cache_size(cls, v):
        if v < 0:
            raise ValueError("Cache size must be non-negative")
        return v

class BertResult(BaseModel):
    """Result container for BERT score calculation"""
    score: float
    precision: float
    recall: float
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
            
            if isinstance(result, BertResult):
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

class BertCalculator:
    """
    Professional BERT score calculator with configuration, caching, and validation.
    
    Designed for API SDK usage with proper error handling, performance monitoring,
    and extensibility.
    """
    
    def __init__(self, config: Optional[BertConfig] = None):
        """
        Initialize BERT calculator.
        
        Args:
            config: Configuration object for BERT calculation
        """
        self.config = config or BertConfig()
        self._cache: Dict[str, tuple] = {}
        logger.info("BERT calculator initialized")
    
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
                       return_detailed: bool = False) -> Union[float, BertResult]:
        """
        Calculate BERT score between response text and reference text.
        
        Args:
            response_text: The generated/predicted text
            reference_text: The reference/ground truth text
            return_detailed: Whether to return detailed result object
            
        Returns:
            BERT score (float) or detailed result object
            
        Raises:
            TypeError: If inputs are not strings
            ValueError: If calculation fails
        """
        # Check cache
        cache_key = self._get_cache_key(response_text, reference_text) if self.config.cache_enabled else None
        
        if cache_key and cache_key in self._cache:
            cached_result = self._cache[cache_key]
            logger.debug("Score retrieved from cache")
            
            if return_detailed:
                return BertResult(
                    score=cached_result[2],  # F1 score
                    precision=cached_result[0],
                    recall=cached_result[1],
                    execution_time=0.0,
                    cached=True,
                    metadata={"cache_key": cache_key}
                )
            return cached_result[2]  # F1 score
        
        try:
            # Calculate BERT score
            P, R, F1 = score(
                [response_text], 
                [reference_text], 
                lang=self.config.language,
                verbose=self.config.verbose,
                idf=self.config.idf,
                device=self.config.device,
                batch_size=self.config.batch_size,
                nthreads=self.config.nthreads,
                all_layers=self.config.all_layers,
                model_type=self.config.model_type,
                num_layers=self.config.num_layers
            )
            
            precision_val = P.mean().item()
            recall_val = R.mean().item()
            f1_val = F1.mean().item()
            
            # Cache result
            if self.config.cache_enabled and cache_key:
                self._cache[cache_key] = (precision_val, recall_val, f1_val)
                self._manage_cache()
            
            if return_detailed:
                return BertResult(
                    score=f1_val,
                    precision=precision_val,
                    recall=recall_val,
                    execution_time=0.0,  # Will be set by decorator
                    cached=False,
                    metadata={
                        "config": self.config.dict(),
                        "input_lengths": {
                            "response": len(response_text),
                            "reference": len(reference_text)
                        }
                    }
                )
            
            return f1_val
            
        except Exception as e:
            logger.error(f"BERT calculation failed: {str(e)}")
            raise ValueError(f"Failed to calculate BERT score: {str(e)}")
    
    @validate_inputs
    @performance_monitor
    def calculate_batch(self, response_texts: List[str], reference_texts: List[str],
                       return_detailed: bool = False) -> Union[List[float], List[BertResult]]:
        """
        Calculate BERT scores for a batch of text pairs.
        
        Args:
            response_texts: List of generated/predicted texts
            reference_texts: List of reference/ground truth texts
            return_detailed: Whether to return detailed result objects
            
        Returns:
            List of BERT scores or detailed result objects
            
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
                if return_detailed:
                    results.append(BertResult(score=0.0, precision=0.0, recall=0.0, 
                                            execution_time=0.0, metadata={"error": str(e)}))
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
        self.config = BertConfig(**config_dict)
        logger.info(f"Configuration updated: {kwargs}")

# Convenience functions for backward compatibility
def calculate_bert_score(response_text: str, reference_text: str) -> float:
    """
    Calculate BERT score between response text and reference text.
    
    Args:
        response_text: The generated/predicted text
        reference_text: The reference/ground truth text
        
    Returns:
        float: BERT score between 0 and 1
    """
    calculator = BertCalculator()
    return calculator.calculate_score(response_text, reference_text)

def calculate_bert_score_batch(response_texts: List[str], reference_texts: List[str]) -> List[float]:
    """
    Calculate BERT scores for a batch of text pairs.
    
    Args:
        response_texts: List of generated/predicted texts
        reference_texts: List of reference/ground truth texts
        
    Returns:
        List[float]: List of BERT scores
    """
    calculator = BertCalculator()
    return calculator.calculate_batch(response_texts, reference_texts) 