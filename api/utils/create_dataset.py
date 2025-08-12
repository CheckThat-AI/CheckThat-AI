"""
Dataset Creation Utilities for DeepEval Integration

This module provides a professional, type-safe interface for creating DeepEval datasets
from extraction session data. Designed for SDK usage with industry-standard patterns.

Example Usage:
    ```python
    # Create dataset from session data
    dataset = (DatasetBuilder(session_id="sess_123")
              .with_metric_type(MetricType.FAITHFULNESS)
              .with_model_config(model="gpt-4", api_key="sk-...")
              .with_field_mapping(input_field="question", output_field="answer")
              .build())
    
    # Evaluate dataset
    results = dataset.evaluate()
    ```
"""

import logging
import re
import os
import time
import pandas as pd
from typing import List, Optional, Dict, Any, Union, Literal
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from deepeval.models import GPTModel, GeminiModel, AnthropicModel
from deepeval.metrics import (
    FaithfulnessMetric, 
    HallucinationMetric,
    AnswerRelevancyMetric
)

from ..services.extraction_session import ExtractionSessionManager, ExtractionData

logger = logging.getLogger(__name__)


class DeepEvalManager:
    """Manager for DeepEval cloud operations including authentication and dataset storage."""
    
    @staticmethod
    def login_to_confident_ai(confident_api_key: str) -> bool:
        """
        Login to Confident AI cloud using the provided API key.
        
        Args:
            confident_api_key: Confident AI API key
            
        Returns:
            True if login was successful, False otherwise
        """
        try:
            import deepeval
            
            # Use the proper DeepEval login method
            deepeval.login_with_confident_api_key(confident_api_key)
            logger.info("Successfully authenticated with Confident AI using API key")
            return True
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Confident AI: {str(e)}")
            return False
    

    
    @staticmethod
    def save_dataset_to_cloud(dataset: EvaluationDataset, alias: str = "MyDataset") -> bool:
        """
        Save dataset to Confident AI cloud.
        
        Args:
            dataset: The dataset to save
            alias: Alias for the dataset
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Verify we have test cases to save
            if not dataset.test_cases or len(dataset.test_cases) == 0:
                logger.error("Cannot save empty dataset to cloud")
                return False
            
            logger.info(f"Attempting to save {len(dataset.test_cases)} test cases to Confident AI cloud")
            
            # For referenceless metrics, we need to auto-convert test cases to goldens
            # since Confident AI cloud requires goldens to save datasets
            dataset.push(alias=alias, auto_convert_test_cases_to_goldens=True)
            logger.info(f"Successfully saved dataset to Confident AI cloud with alias: {alias}")
            return True
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error saving dataset to cloud: {error_msg}")
            
            # Check for specific authentication errors
            if "login" in error_msg.lower() or "auth" in error_msg.lower():
                logger.error("Authentication issue detected. Please check your Confident AI API key.")
            
            return False
    
    @staticmethod
    def save_dataset_locally(dataset: EvaluationDataset, directory: str = "./deepeval-test-dataset") -> bool:
        """
        Save dataset locally as CSV.
        
        Args:
            dataset: The dataset to save
            directory: Directory to save the dataset
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(directory, exist_ok=True)
            
            dataset.save_as(
                file_type="csv",
                directory=directory,
                include_test_cases=True
            )
            logger.info(f"Successfully saved dataset locally to: {directory}")
            return True
        except Exception as e:
            logger.error(f"Error saving dataset locally: {str(e)}")
            return False
    
    @staticmethod
    def load_dataset_from_cloud(alias: str = "MyDataset") -> Optional[EvaluationDataset]:
        """
        Load dataset from Confident AI cloud.
        
        Args:
            alias: Alias of the dataset to load
            
        Returns:
            Loaded dataset or None if failed
        """
        try:
            dataset = EvaluationDataset()
            dataset.pull(alias=alias)
            logger.info(f"Successfully loaded dataset from Confident AI cloud with alias: {alias}")
            return dataset
        except Exception as e:
            logger.error(f"Error loading dataset from cloud: {str(e)}")
            return None
    
    @staticmethod
    def load_dataset_from_csv(
        file_path: str,
        input_col_name: str = "input",
        actual_output_col_name: str = "actual_output",
        expected_output_col_name: Optional[str] = "expected_output",
        context_col_name: Optional[str] = "context",
        context_col_delimiter: str = ";",
        retrieval_context_col_name: Optional[str] = "retrieval_context",
        retrieval_context_col_delimiter: str = ";"
    ) -> Optional[EvaluationDataset]:
        """
        Load dataset from local CSV file.
        
        Args:
            file_path: Path to the CSV file
            input_col_name: Name of the input column
            actual_output_col_name: Name of the actual output column
            expected_output_col_name: Name of the expected output column (optional)
            context_col_name: Name of the context column (optional)
            context_col_delimiter: Delimiter for context column
            retrieval_context_col_name: Name of the retrieval context column (optional)
            retrieval_context_col_delimiter: Delimiter for retrieval context column
            
        Returns:
            Loaded dataset or None if failed
        """
        try:
            dataset = EvaluationDataset()
            
            # Check if expected output is available
            if expected_output_col_name:
                # Add as test cases (with expected output)
                dataset.add_test_cases_from_csv_file(
                    file_path=file_path,
                    input_col_name=input_col_name,
                    actual_output_col_name=actual_output_col_name,
                    expected_output_col_name=expected_output_col_name,
                    context_col_name=context_col_name,
                    context_col_delimiter=context_col_delimiter,
                    retrieval_context_col_name=retrieval_context_col_name,
                    retrieval_context_col_delimiter=retrieval_context_col_delimiter
                )
            else:
                # Add as goldens (without expected output)
                dataset.add_goldens_from_csv_file(
                    file_path=file_path,
                    input_col_name=input_col_name
                )
            
            logger.info(f"Successfully loaded dataset from CSV: {file_path}")
            return dataset
        except Exception as e:
            logger.error(f"Error loading dataset from CSV: {str(e)}")
            return None


class MetricType(Enum):
    """Supported referenceless metric types for DeepEval evaluation."""
    FAITHFULNESS = "faithfulness"
    HALLUCINATION = "hallucination"
    ANSWER_RELEVANCY = "answer_relevancy"


class ModelProvider(Enum):
    """Supported model providers for DeepEval evaluation."""
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


@dataclass
class ModelConfig:
    """Configuration for evaluation model."""
    provider: ModelProvider
    model_name: str
    api_key: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.api_key or not self.api_key.strip():
            raise ValueError("API key is required and cannot be empty")
        
        if self.temperature < 0 or self.temperature > 1:
            raise ValueError("Temperature must be between 0 and 1")


@dataclass
class FieldMapping:
    """Mapping configuration for dataset fields."""
    input_field: str = "input"
    output_field: str = "actual_output"
    context_field: Optional[str] = "context"
    retrieval_context_field: Optional[str] = "retrieval_context"
    
    def __post_init__(self):
        """Validate field mapping."""
        if not self.input_field or not self.output_field:
            raise ValueError("Input and output fields are required")


@dataclass
class MetricConfig:
    """Configuration for metric evaluation."""
    threshold: float = 0.7
    include_reason: bool = True
    strict_mode: bool = False
    
    def __post_init__(self):
        """Validate metric configuration."""
        if not 0 <= self.threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")


class TextProcessor:
    """
    Utility class for text processing and cleaning.
    
    Updated to meet faithfulness metric requirements:
    - Context and retrieval_context must be lists of cleaned, de-duplicated sentences
    - Improved sentence splitting for social media posts
    - Better handling of various text formats and structures
    """
    
    @staticmethod
    def clean_text(text: Union[str, List[str]]) -> List[str]:
        """
        Clean text by removing duplicate sentences and normalizing whitespace.
        Specifically designed for social media posts to handle various sentence structures.
        
        Args:
            text: Input text as string or list of strings
            
        Returns:
            List of unique, cleaned sentences
        """
        import re
        
        if isinstance(text, list):
            sentences = text
        else:
            # Handle None or empty text
            if not text or pd.isna(text):
                return []
            
            text_str = str(text).strip()
            if not text_str:
                return []
            
            # Split string into sentences with improved handling for social media content
            # Handle common sentence endings, but also consider line breaks and multiple spaces
            sentences = re.split(r'(?<=[.!?])\s+|(?<=\n)\s*|(?<=\.\.\.)\s+', text_str)
            
            # Additional splitting for sentences that might not have proper punctuation
            # Split on multiple consecutive spaces or tabs (common in social media)
            temp_sentences = []
            for sentence in sentences:
                # Further split on multiple spaces (2 or more) which often indicate sentence breaks in social media
                sub_sentences = re.split(r'\s{2,}', sentence)
                temp_sentences.extend(sub_sentences)
            sentences = temp_sentences
        
        # Clean and deduplicate sentences
        seen = set()
        unique_sentences = []
        for sentence in sentences:
            # Clean whitespace and normalize
            cleaned = sentence.strip()
            # Remove sentences that are too short (likely fragments) or empty
            if cleaned and len(cleaned) > 3:
                # Normalize for deduplication (case-insensitive comparison)
                normalized_for_comparison = cleaned.lower().strip()
                if normalized_for_comparison not in seen:
                    seen.add(normalized_for_comparison)
                    unique_sentences.append(cleaned)
        
        return unique_sentences
    
    @staticmethod
    def validate_text_data(data: List[Dict[str, Any]], field_mapping: FieldMapping) -> None:
        """
        Validate that required fields exist in the data.
        
        Args:
            data: List of data records
            field_mapping: Field mapping configuration
            
        Raises:
            ValueError: If required fields are missing
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        required_fields = [field_mapping.input_field, field_mapping.output_field]
        
        for i, record in enumerate(data):
            for field in required_fields:
                if field not in record:
                    raise ValueError(f"Required field '{field}' missing in record {i}")
                if not record[field]:
                    raise ValueError(f"Required field '{field}' is empty in record {i}")


class MetricFactory:
    """Factory for creating DeepEval metric instances."""
    
    @staticmethod
    def create_metric(metric_type: MetricType, model_config: ModelConfig, metric_config: MetricConfig):
        """
        Create a DeepEval metric instance.
        
        Args:
            metric_type: Type of metric to create
            model_config: Model configuration
            metric_config: Metric configuration
            
        Returns:
            Configured DeepEval metric instance
            
        Raises:
            ValueError: If metric type is not supported
        """
        # Create model instance
        if model_config.provider == ModelProvider.OPENAI:
            model = GPTModel(
                model=model_config.model_name,
                _openai_api_key=model_config.api_key,
                temperature=model_config.temperature
            )
        elif model_config.provider == ModelProvider.GEMINI:
            model = GeminiModel(
                model_name=model_config.model_name,
                api_key=model_config.api_key,
                temperature=model_config.temperature
            )
        elif model_config.provider == ModelProvider.ANTHROPIC:
            model = AnthropicModel(
                model=model_config.model_name,
                _anthropic_api_key=model_config.api_key,
                temperature=model_config.temperature
            )
        else:
            raise ValueError(f"Unsupported model provider: {model_config.provider}")
        
        # Create metric instance
        metric_kwargs = {
            "model": model,
            "threshold": metric_config.threshold,
            "include_reason": metric_config.include_reason
        }
        
        # Add strict_mode for metrics that support it
        if metric_type in [MetricType.HALLUCINATION, MetricType.ANSWER_RELEVANCY]:
            metric_kwargs["strict_mode"] = metric_config.strict_mode
        
        if metric_type == MetricType.FAITHFULNESS:
            return FaithfulnessMetric(**metric_kwargs)
        elif metric_type == MetricType.HALLUCINATION:
            return HallucinationMetric(**metric_kwargs)
        elif metric_type == MetricType.ANSWER_RELEVANCY:
            return AnswerRelevancyMetric(**metric_kwargs)
        else:
            raise ValueError(f"Unsupported metric type: {metric_type}")


class EvaluationDatasetWrapper:
    """
    Wrapper for DeepEval EvaluationDataset with additional functionality.
    
    This class provides a clean interface for dataset operations and evaluation
    while maintaining compatibility with DeepEval's native dataset format.
    """
    
    def __init__(
        self,
        dataset: EvaluationDataset,
        metric_type: MetricType,
        model_config: ModelConfig,
        metric_config: MetricConfig,
        confident_api_key: Optional[str] = None,
        force_local: bool = False
    ):
        """
        Initialize the dataset wrapper.
        
        Args:
            dataset: DeepEval dataset instance
            metric_type: Type of metric for evaluation
            model_config: Model configuration
            metric_config: Metric configuration
            confident_api_key: Confident AI API key for cloud features (optional)
            force_local: If True, force local evaluation even if API key is provided
        """
        self.dataset = dataset
        self.metric_type = metric_type
        self.model_config = model_config
        self.metric_config = metric_config
        self.confident_api_key = confident_api_key
        self.force_local = force_local
        self._metric = None
    
    @property
    def metric(self):
        """Lazy-load the metric instance."""
        if self._metric is None:
            self._metric = MetricFactory.create_metric(
                self.metric_type, 
                self.model_config, 
                self.metric_config
            )
        return self._metric
    
    def evaluate(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Evaluate the dataset using the configured metric.
        
        Args:
            batch_size: Number of test cases to process in each batch
            
        Returns:
            Dictionary containing evaluation results and metadata
        """
        try:
            import json
            import os
            import re
            import sys
            import io
            from contextlib import redirect_stdout, redirect_stderr
            from deepeval import evaluate
            # Use session manager for authentication control
            from .deepeval_session_manager import deepeval_session_manager
            
            # Only authenticate if cloud features are requested and not forced local
            if self.confident_api_key and not self.force_local:
                logger.info("Authenticating with Confident AI for cloud evaluation")
                auth_success = DeepEvalManager.login_to_confident_ai(self.confident_api_key)
                if not auth_success:
                    logger.warning("Failed to authenticate with Confident AI - proceeding with local evaluation")
            else:
                logger.info("Running local evaluation (no cloud authentication)")
                # Ensure we're in clean local state
                deepeval_session_manager._clear_deepeval_auth()
            
            test_cases = self.dataset.test_cases
            total_batches = (len(test_cases) + batch_size - 1) // batch_size
            
            logger.info(f"Starting evaluation: {len(test_cases)} test cases in {total_batches} batches")
            
            # Capture stdout/stderr to extract cloud URL
            captured_output = io.StringIO()
            captured_errors = io.StringIO()
            cloud_url = None
            
            # Process in batches to avoid memory issues
            all_results = []
            for i in range(0, len(test_cases), batch_size):
                batch = test_cases[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} test cases)")
                
                # Capture output during evaluation to extract cloud URL
                try:
                    with redirect_stdout(captured_output), redirect_stderr(captured_errors):
                        batch_results = evaluate(test_cases=batch, metrics=[self.metric])
                        all_results.extend(batch_results if isinstance(batch_results, list) else [batch_results])
                except Exception as eval_error:
                    # If redirection fails, fall back to normal evaluation
                    logger.warning(f"Output capture failed, proceeding with normal evaluation: {str(eval_error)}")
                    batch_results = evaluate(test_cases=batch, metrics=[self.metric])
                    all_results.extend(batch_results if isinstance(batch_results, list) else [batch_results])
            
            # Extract cloud URL from captured output
            combined_output = captured_output.getvalue() + captured_errors.getvalue()
            url_patterns = [
                r'View results on (https://app\.confident-ai\.com/[^\s]+)',
                r'✓ Done.*View results on (https://app\.confident-ai\.com/[^\s]+)',
                r'(https://app\.confident-ai\.com/project/[^/]+/evaluation/test-runs/[^/\s]+/[^\s]*)',
                r'(https://app\.confident-ai\.com/project/[^/]+/evaluation/test-runs/[^/\s]+)'
            ]
            
            for pattern in url_patterns:
                match = re.search(pattern, combined_output)
                if match:
                    cloud_url = match.group(1)
                    logger.info(f"Extracted cloud URL from DeepEval output: {cloud_url}")
                    break
            
            if not cloud_url and combined_output:
                logger.debug(f"No cloud URL found in captured output: {combined_output[:500]}...")  # Log first 500 chars
            
            # Try to read the latest test run results for detailed metrics
            detailed_metrics = None
            try:
                latest_test_run_path = os.path.join(os.getcwd(), ".deepeval", ".latest_test_run.json")
                if os.path.exists(latest_test_run_path):
                    with open(latest_test_run_path, 'r') as f:
                        test_run_data = json.load(f)
                        if 'testRunData' in test_run_data:
                            detailed_metrics = test_run_data['testRunData']
                            logger.info("Successfully loaded detailed DeepEval metrics from .latest_test_run.json")
            except Exception as e:
                logger.warning(f"Could not load detailed metrics from .latest_test_run.json: {str(e)}")
            
            # Extract metric scores from detailed metrics if available
            metric_scores = None
            if detailed_metrics and 'metricsScores' in detailed_metrics:
                metrics_scores = detailed_metrics['metricsScores']
                if metrics_scores and len(metrics_scores) > 0:
                    metric_data = metrics_scores[0]  # Take the first metric (should match our metric_type)
                    metric_scores = {
                        "metric_name": metric_data.get("metric", self.metric_type.value),
                        "scores": metric_data.get("scores", []),
                        "passes": metric_data.get("passes", 0),
                        "fails": metric_data.get("fails", 0),
                        "errors": metric_data.get("errors", 0),
                        "total_tests": len(metric_data.get("scores", [])),
                        "pass_rate": (metric_data.get("passes", 0) / len(metric_data.get("scores", [1]))) * 100,
                        "average_score": sum(metric_data.get("scores", [])) / len(metric_data.get("scores", [1])) if metric_data.get("scores") else 0
                    }
            
            return {
                "metric_type": self.metric_type.value,
                "total_test_cases": len(test_cases),
                "batches_processed": total_batches,
                "batch_size": batch_size,
                "results": all_results,
                "detailed_metrics": detailed_metrics,
                "metric_scores": metric_scores,
                "cloud_url": cloud_url,
                "model_config": {
                    "provider": self.model_config.provider.value,
                    "model_name": self.model_config.model_name,
                    "temperature": self.model_config.temperature
                },
                "metric_config": {
                    "threshold": self.metric_config.threshold,
                    "include_reason": self.metric_config.include_reason,
                    "strict_mode": self.metric_config.strict_mode
                }
            }
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            # Check if this is a cloud-related error but evaluation actually succeeded
            error_str = str(e).lower()
            if ("api key not found" in error_str or "unauthorized" in error_str) and 'all_results' in locals() and all_results:
                # The evaluation succeeded but cloud upload failed
                logger.warning("Evaluation completed but cloud upload failed - treating as success")
                
                # Try to get detailed metrics even after error
                detailed_metrics = None
                metric_scores = None
                try:
                    latest_test_run_path = os.path.join(os.getcwd(), ".deepeval", ".latest_test_run.json")
                    if os.path.exists(latest_test_run_path):
                        with open(latest_test_run_path, 'r') as f:
                            test_run_data = json.load(f)
                            if 'testRunData' in test_run_data:
                                detailed_metrics = test_run_data['testRunData']
                                
                        # Extract metric scores if available
                        if detailed_metrics and 'metricsScores' in detailed_metrics:
                            metrics_scores = detailed_metrics['metricsScores']
                            if metrics_scores and len(metrics_scores) > 0:
                                metric_data = metrics_scores[0]
                                metric_scores = {
                                    "metric_name": metric_data.get("metric", self.metric_type.value),
                                    "scores": metric_data.get("scores", []),
                                    "passes": metric_data.get("passes", 0),
                                    "fails": metric_data.get("fails", 0),
                                    "errors": metric_data.get("errors", 0),
                                    "total_tests": len(metric_data.get("scores", [])),
                                    "pass_rate": (metric_data.get("passes", 0) / len(metric_data.get("scores", [1]))) * 100,
                                    "average_score": sum(metric_data.get("scores", [])) / len(metric_data.get("scores", [1])) if metric_data.get("scores") else 0
                                }
                except Exception as metrics_error:
                    logger.warning(f"Could not load detailed metrics after cloud error: {metrics_error}")
                
                return {
                    "metric_type": self.metric_type.value,
                    "total_test_cases": len(test_cases),
                    "batches_processed": total_batches,
                    "batch_size": batch_size,
                    "results": all_results,
                    "detailed_metrics": detailed_metrics,
                    "metric_scores": metric_scores,
                    "cloud_url": cloud_url if 'cloud_url' in locals() else None,
                    "model_config": {
                        "provider": self.model_config.provider.value,
                        "model_name": self.model_config.model_name,
                        "temperature": self.model_config.temperature
                    },
                    "metric_config": {
                        "threshold": self.metric_config.threshold,
                        "include_reason": self.metric_config.include_reason,
                        "strict_mode": self.metric_config.strict_mode
                    },
                    "warning": "Evaluation completed successfully but cloud upload failed"
                }
            raise ValueError(f"Failed to evaluate dataset: {str(e)}")
    
    def get_test_case_count(self) -> int:
        """Get the number of test cases in the dataset."""
        return len(self.dataset.test_cases)
    
    def get_sample_test_case(self, index: int = 0) -> Optional[Dict[str, Any]]:
        """
        Get a sample test case for inspection.
        
        Args:
            index: Index of the test case to retrieve
            
        Returns:
            Dictionary representation of the test case
        """
        if not self.dataset.test_cases or index >= len(self.dataset.test_cases):
            return None
        
        test_case = self.dataset.test_cases[index]
        return {
            "input": test_case.input,
            "actual_output": test_case.actual_output,
            "retrieval_context": test_case.retrieval_context
        }

    def save_dataset(self, confident_api_key: Optional[str] = None, alias: str = "MyDataset", local_directory: str = "./deepeval-test-dataset", force_local: bool = False) -> bool:
        """
        Save the dataset either to Confident AI cloud or locally.
        
        Args:
            confident_api_key: Confident AI API key for cloud storage (optional)
            alias: Alias for cloud storage
            local_directory: Directory for local storage
            force_local: If True, save locally even if API key is provided
            
        Returns:
            True if save was successful, False otherwise
        """
        if confident_api_key and not force_local:
            # Login to Confident AI and save to cloud
            logger.info("Attempting to save dataset to Confident AI cloud")
            
            # Try to login first
            login_success = DeepEvalManager.login_to_confident_ai(confident_api_key)
            if login_success:
                logger.info("Successfully authenticated with Confident AI cloud")
                # Try to save to cloud
                cloud_save_success = DeepEvalManager.save_dataset_to_cloud(self.dataset, alias)
                if cloud_save_success:
                    logger.info("Successfully saved dataset to Confident AI cloud")
                    return True
                else:
                    logger.error("Cloud save failed after successful authentication, falling back to local save")
            else:
                logger.error("Failed to authenticate with Confident AI cloud, falling back to local save")
                # Don't fallback to local if cloud was explicitly requested
                # This ensures the UI gets proper feedback about authentication failures
                return False
        
        # Save locally (either as fallback or primary choice)
        if force_local:
            logger.info("Saving dataset locally (forced local mode)")
        else:
            logger.info("Saving dataset locally")
        return DeepEvalManager.save_dataset_locally(self.dataset, local_directory)
    
    @classmethod
    def load_dataset(
        cls, 
        confident_api_key: Optional[str] = None,
        alias: str = "MyDataset",
        csv_file_path: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
        model_config: Optional[ModelConfig] = None,
        metric_config: Optional[MetricConfig] = None
    ) -> Optional['EvaluationDatasetWrapper']:
        """
        Load a dataset from Confident AI cloud or local CSV file.
        
        Args:
            confident_api_key: Confident AI API key for cloud access (optional)
            alias: Alias for cloud dataset
            csv_file_path: Path to local CSV file
            metric_type: Metric type for the wrapper
            model_config: Model configuration for the wrapper
            metric_config: Metric configuration for the wrapper
            
        Returns:
            EvaluationDatasetWrapper instance or None if failed
        """
        dataset = None
        
        if confident_api_key:
            # Login to Confident AI and load from cloud
            logger.info("Attempting to load dataset from Confident AI cloud")
            if DeepEvalManager.login_to_confident_ai(confident_api_key):
                dataset = DeepEvalManager.load_dataset_from_cloud(alias)
            else:
                logger.error("Failed to login to Confident AI")
                return None
        elif csv_file_path:
            # Load from local CSV
            logger.info(f"Loading dataset from local CSV: {csv_file_path}")
            dataset = DeepEvalManager.load_dataset_from_csv(csv_file_path)
        else:
            logger.error("Either confident_api_key or csv_file_path must be provided")
            return None
        
        if dataset and metric_type and model_config and metric_config:
            return cls(dataset, metric_type, model_config, metric_config)
        else:
            logger.error("Failed to load dataset or missing configuration parameters")
            return None


class DatasetBuilder:
    """
    Builder class for creating DeepEval evaluation datasets.
    
    This class provides a fluent interface for configuring and building
    evaluation datasets from extraction results. It supports both session-based
    and file-based data sources for maximum flexibility.
    """
    
    def __init__(self, session_id: str, session_manager: Optional[ExtractionSessionManager] = None):
        """
        Initialize the builder with a session ID.
        
        Args:
            session_id: ID of the extraction session (used for file paths and fallback)
            session_manager: Optional session manager instance
        """
        self.session_id = session_id
        self.session_manager = session_manager
        self._metric_type: Optional[MetricType] = None
        self._model_config: Optional[ModelConfig] = None
        self._field_mapping: FieldMapping = FieldMapping()
        self._metric_config: MetricConfig = MetricConfig()
        self._confident_api_key: Optional[str] = None
    
    def with_metric_type(self, metric_type: MetricType) -> 'DatasetBuilder':
        """Set the metric type for evaluation."""
        self._metric_type = metric_type
        return self
    
    def with_model_config(
        self, 
        provider: ModelProvider, 
        model_name: str, 
        api_key: str,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> 'DatasetBuilder':
        """Set the model configuration."""
        self._model_config = ModelConfig(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return self
    
    def with_field_mapping(
        self,
        input_field: str = "input",
        output_field: str = "actual_output",
        context_field: Optional[str] = "context",
        retrieval_context_field: Optional[str] = "retrieval_context"
    ) -> 'DatasetBuilder':
        """Set the field mapping configuration."""
        self._field_mapping = FieldMapping(
            input_field=input_field,
            output_field=output_field,
            context_field=context_field,
            retrieval_context_field=retrieval_context_field
        )
        return self
    
    def with_metric_config(
        self,
        threshold: float = 0.7,
        include_reason: bool = True,
        strict_mode: bool = False
    ) -> 'DatasetBuilder':
        """Set the metric configuration."""
        self._metric_config = MetricConfig(
            threshold=threshold,
            include_reason=include_reason,
            strict_mode=strict_mode
        )
        return self
    
    def with_confident_api_key(self, api_key: str) -> 'DatasetBuilder':
        """Set the Confident AI API key for cloud features."""
        self._confident_api_key = api_key
        return self
    
    def build(self) -> EvaluationDatasetWrapper:
        """
        Build the evaluation dataset.
        
        Returns:
            Configured EvaluationDatasetWrapper instance
            
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        # Validate required configurations
        if not self._metric_type:
            raise ValueError("Metric type is required")
        
        if not self._model_config:
            raise ValueError("Model configuration is required")
        
        # Try to create test cases from CSV files first (session-independent)
        test_cases = self._create_test_cases_from_csv()
        
        # If CSV approach fails, fall back to session-based approach
        if not test_cases:
            logger.info("CSV files not found or invalid, falling back to session-based approach")
        
        # Get session data
        if not self.session_manager:
            from ..services.extraction_session import extraction_session_manager
            self.session_manager = extraction_session_manager
        
        extraction_data = self.session_manager.get_extraction_data(self.session_id)
        if not extraction_data:
            raise ValueError(f"Session {self.session_id} not found and no valid CSV files available")
            
        # Create test cases from session data
        test_cases = self._create_test_cases_from_stored_claims(extraction_data)
        
        if not test_cases:
            raise ValueError("No test cases could be created from available data sources")
        
        # Create DeepEval dataset
        dataset = EvaluationDataset()
        dataset.test_cases = test_cases
        
        logger.info(f"Created dataset with {len(test_cases)} test cases for metric {self._metric_type.value}")
        
        return EvaluationDatasetWrapper(
            dataset=dataset,
            metric_type=self._metric_type,
            model_config=self._model_config,
            metric_config=self._metric_config,
            confident_api_key=getattr(self, '_confident_api_key', None),
            force_local=getattr(self, '_force_local', False)
        )
    
    def build_and_save(
        self, 
        confident_api_key: Optional[str] = None, 
        alias: str = "MyDataset", 
        local_directory: str = "./deepeval-test-dataset",
        force_local: bool = False
    ) -> tuple[EvaluationDatasetWrapper, bool]:
        """
        Build the evaluation dataset and automatically save it.
        
        Args:
            confident_api_key: Confident AI API key for cloud storage (optional)
            alias: Alias for cloud storage
            local_directory: Directory for local storage
            force_local: If True, save locally even if API key is provided
            
        Returns:
            Tuple of (EvaluationDatasetWrapper instance, save_success)
            
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        # Store authentication parameters for the wrapper
        self._confident_api_key = confident_api_key
        self._force_local = force_local
        
        # Build the dataset
        wrapper = self.build()
        
        # Save the dataset
        save_success = wrapper.save_dataset(
            confident_api_key=confident_api_key,
            alias=alias,
            local_directory=local_directory,
            force_local=force_local
        )
        
        if save_success:
            logger.info(f"Dataset successfully built and saved {'locally (forced)' if force_local else 'to cloud' if confident_api_key else 'locally'}")
        else:
            logger.warning("Dataset built but saving failed")
        
        return wrapper, save_success
    
    def _create_test_cases_from_csv(self) -> List[LLMTestCase]:
        """
        Create LLMTestCase instances from CSV files (session-specific but session-independent).
        
        Returns:
            List of LLMTestCase instances, empty list if CSV files not available
        """
        test_cases = []
        
        # Read the actual extraction results CSV file to get the new column structure
        import os
        import pandas as pd
        
        # Get the results directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), "data", "results")
        
        try:
            df = None
            source_file = None
            
            # Try session-specific files first (most reliable approach)
            session_specific_paths = [
                # Session-specific combined results file
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), "data", f"inference_results_{self.session_id}.csv"),
                # Session-specific results directory file
                os.path.join(results_dir, f"inference_results_{self.session_id}.csv"),
            ]
            
            for path in session_specific_paths:
                if os.path.exists(path):
                    df = pd.read_csv(path)
                    source_file = path
                    logger.info(f"Reading session-specific extraction results from: {path}")
                    break
            
            # If no session-specific files found, try to find files that might contain session data
            if df is None and os.path.exists(results_dir):
                # Look for CSV files that might contain our session's data
                csv_files = [f for f in os.listdir(results_dir) if f.endswith('.csv') and 'inference_results' in f]
                
                for csv_file in csv_files:
                    file_path = os.path.join(results_dir, csv_file)
                    try:
                        temp_df = pd.read_csv(file_path)
                        # Check if this file contains data that might be from our session
                        # (This is a heuristic - ideally CSV files should include session_id column)
                        if not temp_df.empty and 'input' in temp_df.columns and 'actual_output' in temp_df.columns:
                            # Check if the file was created recently (within reasonable time of session)
                            file_mtime = os.path.getmtime(file_path)
                            current_time = time.time()
                            # If file is less than 24 hours old, it might be relevant
                            if current_time - file_mtime < 86400:  # 24 hours in seconds
                                df = temp_df
                                source_file = file_path
                                logger.info(f"Using recent extraction results file: {file_path}")
                                break
                    except Exception as e:
                        logger.debug(f"Could not read CSV file {csv_file}: {str(e)}")
                        continue
            
            # Final fallback: try the global combined results file (least reliable for multi-user)
            if df is None:
                combined_results_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), "data", "inference_results.csv")
                if os.path.exists(combined_results_path):
                    df = pd.read_csv(combined_results_path)
                    source_file = combined_results_path
                    logger.warning(f"Using global results file (may contain mixed user data): {combined_results_path}")
            
            if df is None:
                logger.warning(f"No CSV files found for session {self.session_id}")
                return []
            
            # Validate that the required columns exist
            required_columns = ['input', 'actual_output', 'context', 'retrieval_context']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.warning(f"Missing columns in results file {source_file}: {missing_columns}")
                return []
            
            # Filter by session_id if the column exists (best case scenario)
            if 'session_id' in df.columns:
                session_df = df[df['session_id'] == self.session_id]
                if not session_df.empty:
                    df = session_df
                    logger.info(f"Filtered to {len(df)} rows for session {self.session_id}")
                else:
                    logger.warning(f"No data found for session {self.session_id} in {source_file}")
                    return []
            else:
                logger.warning(f"No session_id column in {source_file} - using all data (potential data leakage risk)")
            
            # Create test cases from the CSV data
            for _, row in df.iterrows():
                # Process context and retrieval_context as lists of cleaned, de-duplicated sentences
                context_data = None
                retrieval_context_data = None
                
                if pd.notna(row['context']):
                    context_str = str(row['context'])
                    if context_str.strip():
                        # Convert context to a list of cleaned, de-duplicated sentences
                        context_data = TextProcessor.clean_text(context_str)
                
                if pd.notna(row['retrieval_context']):
                    retrieval_context_str = str(row['retrieval_context'])
                    if retrieval_context_str.strip():
                        # Convert retrieval_context to a list of cleaned, de-duplicated sentences
                        retrieval_context_data = TextProcessor.clean_text(retrieval_context_str)
                
                test_case = LLMTestCase(
                    input=str(row['input']),
                    actual_output=str(row['actual_output']),
                    expected_output=None,  # No expected output for referenceless metrics
                    context=context_data,
                    retrieval_context=retrieval_context_data
                )
                test_cases.append(test_case)
            
            logger.info(f"Created {len(test_cases)} test cases from CSV results for session {self.session_id}")
            return test_cases
            
        except Exception as e:
            logger.error(f"Error reading extraction results CSV for session {self.session_id}: {str(e)}")
            return []
    
    def _create_test_cases_from_stored_claims(self, extraction_data: ExtractionData) -> List[LLMTestCase]:
        """
        Fallback method to create test cases from stored claims data.
        
        Args:
            extraction_data: Extraction session data
            
        Returns:
            List of LLMTestCase instances
        """
        test_cases = []
        
        # Get prompt information from stored data (only for custom prompts now)
        prompt_info = extraction_data.prompt_info or {}
        
        # Determine the prompt content to use as input
        if prompt_info.get('is_custom') and prompt_info.get('prompt_content'):
            # Use the stored custom prompt content
            base_prompt = prompt_info['prompt_content']
        else:
            # Use the same instruction as the extraction process for consistency
            # Import here to avoid circular imports
            try:
                from ..utils.prompts import instruction
                base_prompt = instruction.strip()
            except ImportError:
                # Fallback if import fails
                base_prompt = "Identify the decontextualized, stand-alone, and verifiable central claim in the given post:"
        
        # Create test cases using the stored extracted and reference claims
        for i, (extracted_claim, reference_claim) in enumerate(
            zip(extraction_data.extracted_claims, extraction_data.reference_claims)
        ):
            # Construct the full input prompt with the reference claim as the source text
            test_input = f"{base_prompt} {reference_claim}"
            
            # Process reference_claim as both context and retrieval_context
            # Convert to lists of cleaned, de-duplicated sentences from the social media post
            retrieval_context = TextProcessor.clean_text(reference_claim)
            context_data = TextProcessor.clean_text(reference_claim) if reference_claim and reference_claim.strip() else None
            
            test_case = LLMTestCase(
                input=test_input,
                actual_output=extracted_claim,
                expected_output=None,  # No expected output for referenceless metrics
                context=context_data,
                retrieval_context=retrieval_context
            )
            test_cases.append(test_case)
        
        logger.info(f"Created {len(test_cases)} test cases from stored claims with prompt: {base_prompt[:50] if base_prompt else 'None'}...")
        return test_cases
    
    def _create_test_cases(self, extraction_data: ExtractionData) -> List[LLMTestCase]:
        """
        Legacy method - now just calls the CSV-based approach for consistency.
        
        Args:
            extraction_data: Extraction session data (for fallback only)
            
        Returns:
            List of LLMTestCase instances
        """
        # Try CSV first
        test_cases = self._create_test_cases_from_csv()
        
        # Fall back to stored claims if CSV fails
        if not test_cases:
            logger.info("CSV approach failed, using stored claims data")
            test_cases = self._create_test_cases_from_stored_claims(extraction_data)
        
        return test_cases




# Convenience factory functions for common use cases

def create_faithfulness_dataset(
    session_id: str,
    model_provider: ModelProvider,
    model_name: str,
    api_key: str,
    threshold: float = 0.7
) -> EvaluationDatasetWrapper:
    """
    Convenience function to create a faithfulness evaluation dataset.
    
    Args:
        session_id: Extraction session ID
        model_provider: Model provider (OpenAI, Gemini, etc.)
        model_name: Name of the model to use
        api_key: API key for the model
        threshold: Evaluation threshold (default: 0.7)
        
    Returns:
        Configured EvaluationDatasetWrapper for faithfulness evaluation
    """
    return (DatasetBuilder(session_id)
            .with_metric_type(MetricType.FAITHFULNESS)
            .with_model_config(model_provider, model_name, api_key)
            .with_metric_config(threshold=threshold)
            .build())


def create_hallucination_dataset(
    session_id: str,
    model_provider: ModelProvider,
    model_name: str,
    api_key: str,
    threshold: float = 0.7
) -> EvaluationDatasetWrapper:
    """
    Convenience function to create a hallucination evaluation dataset.
    
    Args:
        session_id: Extraction session ID
        model_provider: Model provider (OpenAI, Gemini, etc.)
        model_name: Name of the model to use
        api_key: API key for the model
        threshold: Evaluation threshold (default: 0.7)
        
    Returns:
        Configured EvaluationDatasetWrapper for hallucination evaluation
    """
    return (DatasetBuilder(session_id)
            .with_metric_type(MetricType.HALLUCINATION)
            .with_model_config(model_provider, model_name, api_key)
            .with_metric_config(threshold=threshold)
            .build())


def create_answer_relevancy_dataset(
    session_id: str,
    model_provider: ModelProvider,
    model_name: str,
    api_key: str,
    threshold: float = 0.5
) -> EvaluationDatasetWrapper:
    """
    Convenience function to create an answer relevancy evaluation dataset.
    
    Args:
        session_id: Session ID containing extraction data
        model_provider: Model provider for evaluation
        model_name: Model name to use
        api_key: API key for the model provider
        threshold: Answer relevancy threshold (default: 0.5)
        
    Returns:
        Configured EvaluationDatasetWrapper ready for evaluation
    """
    return (
        DatasetBuilder(session_id)
        .with_metric_type(MetricType.ANSWER_RELEVANCY)
        .with_model_config(
            provider=model_provider,
            model_name=model_name,
            api_key=api_key
        )
        .with_metric_config(threshold=threshold)
        .build()
    )


# Export main classes and functions for SDK usage
__all__ = [
    'MetricType',
    'ModelProvider', 
    'ModelConfig',
    'FieldMapping',
    'MetricConfig',
    'DatasetBuilder',
    'EvaluationDatasetWrapper',
    'MetricFactory',
    'TextProcessor',
    'create_faithfulness_dataset',
    'create_hallucination_dataset',
    'create_answer_relevancy_dataset'
]
    