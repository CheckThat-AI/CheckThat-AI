import logging
import time
from functools import wraps
from typing import List, Dict, Any, Optional, Union
from sentence_transformers import SentenceTransformer, util
from pydantic import BaseModel, field_validator

# Configure logging
logger = logging.getLogger(__name__)

class CosineSimilarityConfig(BaseModel):
    """Configuration for cosine similarity calculation"""
    model_name: str = 'all-MiniLM-L6-v2'
    device: Optional[str] = None
    normalize_embeddings: bool = True
    batch_size: int = 32
    show_progress_bar: bool = False
    convert_to_tensor: bool = True
    cache_enabled: bool = True
    max_cache_size: int = 1000
    model_cache: bool = True
    
    @field_validator('model_name')
    @classmethod
    def validate_model_name(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Model name must be a non-empty string")
        return v
    
    @field_validator('batch_size')
    @classmethod
    def validate_batch_size(cls, v):
        if v <= 0:
            raise ValueError("Batch size must be positive")
        return v
    
    @field_validator('max_cache_size')
    @classmethod
    def validate_cache_size(cls, v):
        if v < 0:
            raise ValueError("Cache size must be non-negative")
        return v

class CosineSimilarityResult(BaseModel):
    """Result container for cosine similarity calculation"""
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
            
            if isinstance(result, CosineSimilarityResult):
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

class CosineSimilarityCalculator:
    """
    Professional cosine similarity calculator with configuration, caching, and validation.
    
    Designed for API SDK usage with proper error handling, performance monitoring,
    and extensibility.
    """
    
    def __init__(self, config: Optional[CosineSimilarityConfig] = None):
        """
        Initialize cosine similarity calculator.
        
        Args:
            config: Configuration object for cosine similarity calculation
        """
        self.config = config or CosineSimilarityConfig()
        self._cache: Dict[str, float] = {}
        self._model_cache: Dict[str, SentenceTransformer] = {}
        self._model = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the sentence transformer model"""
        try:
            if self.config.model_cache and self.config.model_name in self._model_cache:
                self._model = self._model_cache[self.config.model_name]
                logger.debug(f"Loaded cached model: {self.config.model_name}")
            else:
                self._model = SentenceTransformer(
                    self.config.model_name, 
                    device=self.config.device
                )
                if self.config.model_cache:
                    self._model_cache[self.config.model_name] = self._model
                logger.info(f"Initialized SentenceTransformer model: {self.config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize SentenceTransformer model: {str(e)}")
            raise RuntimeError(f"Model initialization failed: {str(e)}")
    
    def _get_cache_key(self, response_text: str, reference_text: str) -> str:
        """Generate cache key for text pair"""
        return f"{hash(response_text)}:{hash(reference_text)}:{self.config.model_name}"
    
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
                       return_detailed: bool = False) -> Union[float, CosineSimilarityResult]:
        """
        Calculate cosine similarity between response text and reference text.
        
        Args:
            response_text: The generated/predicted text
            reference_text: The reference/ground truth text
            return_detailed: Whether to return detailed result object
            
        Returns:
            Cosine similarity score (float) or detailed result object
            
        Raises:
            TypeError: If inputs are not strings
            RuntimeError: If model is not properly initialized
            ValueError: If calculation fails
        """
        if self._model is None:
            raise RuntimeError("Model not properly initialized")
        
        # Check cache
        cache_key = self._get_cache_key(response_text, reference_text) if self.config.cache_enabled else None
        
        if cache_key and cache_key in self._cache:
            cached_score = self._cache[cache_key]
            logger.debug("Score retrieved from cache")
            
            if return_detailed:
                return CosineSimilarityResult(
                    score=cached_score,
                    execution_time=0.0,
                    cached=True,
                    metadata={"cache_key": cache_key}
                )
            return cached_score
        
        try:
            # Generate embeddings
            response_embedding = self._model.encode(
                response_text, 
                convert_to_tensor=self.config.convert_to_tensor,
                normalize_embeddings=self.config.normalize_embeddings,
                batch_size=self.config.batch_size,
                show_progress_bar=self.config.show_progress_bar
            )
            reference_embedding = self._model.encode(
                reference_text, 
                convert_to_tensor=self.config.convert_to_tensor,
                normalize_embeddings=self.config.normalize_embeddings,
                batch_size=self.config.batch_size,
                show_progress_bar=self.config.show_progress_bar
            )
            
            # Calculate cosine similarity
            cos_sim = util.cos_sim(response_embedding, reference_embedding)
            similarity_score = cos_sim.item()
            
            # Cache result
            if self.config.cache_enabled and cache_key:
                self._cache[cache_key] = similarity_score
                self._manage_cache()
            
            if return_detailed:
                return CosineSimilarityResult(
                    score=similarity_score,
                    execution_time=0.0,  # Will be set by decorator
                    cached=False,
                    metadata={
                        "model_name": self.config.model_name,
                        "input_lengths": {
                            "response": len(response_text),
                            "reference": len(reference_text)
                        },
                        "config": self.config.dict()
                    }
                )
            
            return similarity_score
            
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {str(e)}")
            raise ValueError(f"Failed to calculate cosine similarity: {str(e)}")
    
    @validate_inputs
    @performance_monitor
    def calculate_batch(self, response_texts: List[str], reference_texts: List[str],
                       return_detailed: bool = False) -> Union[List[float], List[CosineSimilarityResult]]:
        """
        Calculate cosine similarity for a batch of text pairs.
        
        Args:
            response_texts: List of generated/predicted texts
            reference_texts: List of reference/ground truth texts
            return_detailed: Whether to return detailed result objects
            
        Returns:
            List of cosine similarity scores or detailed result objects
            
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
                    results.append(CosineSimilarityResult(score=0.0, execution_time=0.0, 
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
            "cache_enabled": self.config.cache_enabled,
            "model_cache_size": len(self._model_cache)
        }
    
    def update_config(self, **kwargs) -> None:
        """Update configuration parameters"""
        old_model_name = self.config.model_name
        config_dict = self.config.dict()
        config_dict.update(kwargs)
        self.config = CosineSimilarityConfig(**config_dict)
        
        # Reinitialize model if model_name changed
        if self.config.model_name != old_model_name:
            self._initialize_model()
        
        logger.info(f"Configuration updated: {kwargs}")

# Convenience functions for backward compatibility
def calculate_cosine_similarity(response_text: str, reference_text: str) -> float:
    """
    Calculate cosine similarity between response text and reference text.
    
    Args:
        response_text: The generated/predicted text
        reference_text: The reference/ground truth text
        
    Returns:
        float: Cosine similarity between 0 and 1
    """
    calculator = CosineSimilarityCalculator()
    return calculator.calculate_score(response_text, reference_text)

def calculate_cosine_similarity_batch(response_texts: List[str], reference_texts: List[str]) -> List[float]:
    """
    Calculate cosine similarity for a batch of text pairs.
    
    Args:
        response_texts: List of generated/predicted texts
        reference_texts: List of reference/ground truth texts
        
    Returns:
        List[float]: List of cosine similarity scores
    """
    calculator = CosineSimilarityCalculator()
    return calculator.calculate_batch(response_texts, reference_texts)