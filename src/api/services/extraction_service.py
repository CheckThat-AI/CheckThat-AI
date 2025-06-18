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
from ..utils.extract import start_extraction
from ..models.requests import ExtractionStartRequest

class ExtractionService:
    """Service for handling extraction logic"""
    
    @staticmethod
    def validate_extraction_data(data: ExtractionStartRequest) -> Optional[str]:
        """Validate extraction request data"""
        if not data.models or not data.prompt_styles or not data.file_data:
            return "Missing required extraction data"
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
    def run_extraction_with_progress(
        session_id: str, 
        extraction_data: ExtractionStartRequest, 
        progress_callback: Callable[[str, Dict[str, Any]], None], 
        stop_event: threading.Event
    ) -> Optional[Dict[str, float]]:
        """
        Run extraction with progress updates
        """
        try:
            # Send initial status
            progress_callback("status", {"message": "Starting extraction...", "progress": 0})
            
            # Validate extraction data
            error_msg = ExtractionService.validate_extraction_data(extraction_data)
            if error_msg:
                progress_callback("error", {"message": error_msg})
                return None
            
            # Set API keys
            ExtractionService.set_api_keys(extraction_data.api_keys)
            
            # Load dataset
            df, error_msg = ExtractionService.load_dataset_from_file_data(extraction_data.file_data)
            if error_msg:
                progress_callback("error", {"message": error_msg})
                return None
            
            progress_callback("status", {"message": f"Loaded dataset with {len(df)} rows"})
            
            # Validate dataset columns
            error_msg = ExtractionService.validate_dataset_columns(df)
            if error_msg:
                progress_callback("error", {"message": error_msg})
                return None
            
            # Run extraction
            progress_callback("status", {"message": "Running extraction...", "progress": 0})
            
            combination_result = start_extraction(
                model=extraction_data.models[0],
                prompt_style=extraction_data.prompt_styles[0],
                input_data=df,
                refine_iters=extraction_data.self_refine_iterations,
                progress_callback=progress_callback,
                stop_event=stop_event,
                cross_refine_model=extraction_data.cross_refine_model
            )
            
            print(f"DEBUG: Type of combination_result: {type(combination_result)}, Value: {combination_result}")

            if combination_result:  # Only if not stopped
                combined_results_path, extracted_claims, reference_claims = combination_result

                # Store extraction data in the session manager
                from .extraction_session import extraction_session_manager
                extraction_session_manager.store_extraction_data(
                    session_id=session_id,
                    extracted_claims=extracted_claims,
                    reference_claims=reference_claims,
                    model_combinations=[f"{extraction_data.models[0]}_{extraction_data.prompt_styles[0]}"] # Store model combination
                )

                # Read the CSV file content to send to frontend
                try:
                    df = pd.read_csv(combined_results_path)
                    file_data = {
                        "file_path": combined_results_path,
                        "file_name": "inference_results.csv",
                        "data": df.to_dict('records'),  # Convert to list of dictionaries
                        "columns": list(df.columns)
                    }
                except Exception as e:
                    print(f"Error reading CSV file: {e}")
                    file_data = None

                progress_callback("complete", {
                    "message": "Extraction completed successfully",
                    "scores": {"overall_score": 0.0}, # Placeholder or actual score if calculated in start_extraction
                    "file_data": file_data
                })
                return {"overall_score": 0.0}
            else:
                progress_callback("status", {"message": "Extraction was stopped"})
                return None
            
        except Exception as e:
            progress_callback("error", {"message": f"Extraction failed: {str(e)}"})
            print(f"Error in extraction: {str(e)}")
            import traceback
            traceback.print_exc()
            return None 