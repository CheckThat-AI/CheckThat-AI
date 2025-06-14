import os
import sys
import time
import threading
import asyncio
import pandas as pd
import io
import base64
from pathlib import Path
from typing import Dict, Any, Optional, Callable

# Import from the utils folder that's now inside the api folder
from ..utils.evaluate import start_evaluation
from ..models.requests import EvaluationStartRequest

class EvaluationService:
    """Service for handling evaluation logic"""
    
    @staticmethod
    def validate_evaluation_data(data: EvaluationStartRequest) -> Optional[str]:
        """Validate evaluation request data"""
        if not data.models or not data.prompt_styles or not data.file_data:
            return "Missing required evaluation data"
        return None
    
    @staticmethod
    def load_dataset_from_file_data(file_data: Dict[str, str]) -> tuple[pd.DataFrame, Optional[str]]:
        """Load dataset from base64 encoded file data"""
        try:
            # Decode file data
            file_content = base64.b64decode(file_data['content'])
            file_name = file_data['name']
            
            if file_name.endswith('.csv'):
                df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
            elif file_name.endswith('.json'):
                df = pd.read_json(io.StringIO(file_content.decode('utf-8')))
            elif file_name.endswith('.jsonl'):
                df = pd.read_json(io.StringIO(file_content.decode('utf-8')), lines=True)
            else:
                return None, "Unsupported file format"
            
            return df, None
            
        except Exception as e:
            return None, f"Error loading dataset: {str(e)}"
    
    @staticmethod
    def validate_dataset_columns(df: pd.DataFrame) -> Optional[str]:
        """Validate that dataset has required columns"""
        required_columns = ['post', 'normalized claim']
        if not all(col in df.columns for col in required_columns):
            return f"Dataset must contain columns: {required_columns}. Found: {df.columns.tolist()}"
        return None
    
    @staticmethod
    def set_api_keys(api_keys: Dict[str, str]):
        """Set API keys as environment variables"""
        for provider, api_key in api_keys.items():
            if api_key:
                os.environ[f"{provider.upper()}_API_KEY"] = api_key
    
    @staticmethod
    def run_evaluation_with_progress(
        session_id: str, 
        evaluation_data: EvaluationStartRequest, 
        progress_callback: Callable[[str, Dict[str, Any]], None], 
        stop_event: threading.Event
    ) -> Optional[Dict[str, float]]:
        """
        Run evaluation with progress updates
        """
        try:
            # Send initial status
            progress_callback("status", {"message": "Starting evaluation...", "progress": 0})
            
            # Validate evaluation data
            error_msg = EvaluationService.validate_evaluation_data(evaluation_data)
            if error_msg:
                progress_callback("error", {"message": error_msg})
                return None
            
            # Set API keys
            EvaluationService.set_api_keys(evaluation_data.api_keys)
            
            # Load dataset
            df, error_msg = EvaluationService.load_dataset_from_file_data(evaluation_data.file_data)
            if error_msg:
                progress_callback("error", {"message": error_msg})
                return None
            
            progress_callback("status", {"message": f"Loaded dataset with {len(df)} rows"})
            
            # Validate dataset columns
            error_msg = EvaluationService.validate_dataset_columns(df)
            if error_msg:
                progress_callback("error", {"message": error_msg})
                return None
            
            # Run evaluation
            progress_callback("status", {"message": "Running evaluation...", "progress": 0})
            
            combination_scores = start_evaluation(
                models=evaluation_data.models,
                prompt_styles=evaluation_data.prompt_styles,
                input_data=df,
                refine_iters=evaluation_data.self_refine_iterations,
                progress_callback=progress_callback,
                stop_event=stop_event,
                cross_refine_model=evaluation_data.cross_refine_model
            )
            
            if combination_scores:  # Only if not stopped
                progress_callback("complete", {
                    "message": "Evaluation completed successfully",
                    "scores": combination_scores
                })
                return combination_scores
            else:
                progress_callback("status", {"message": "Evaluation was stopped"})
                return None
            
        except Exception as e:
            progress_callback("error", {"message": f"Evaluation failed: {str(e)}"})
            print(f"Error in evaluation: {str(e)}")
            import traceback
            traceback.print_exc()
            return None 