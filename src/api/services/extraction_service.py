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
        """Validate that dataset has required columns after field mapping is applied"""
        # Only 'post' column is required - 'normalized claim' is optional for referenceless metrics
        required_columns = ['post']
        missing_required = [col for col in required_columns if col not in df.columns]
        
        if missing_required:
            return f"Dataset must contain required column: {missing_required}. Found: {df.columns.tolist()}"
        
        # Log what columns we have
        has_reference_claims = 'normalized claim' in df.columns
        print(f"Dataset validation passed. Has reference claims: {has_reference_claims}")
        
        return None
    
    @staticmethod
    def apply_field_mapping_to_dataset(df: pd.DataFrame, field_mapping: Optional[Dict[str, Any]]) -> tuple[pd.DataFrame, Optional[str]]:
        """
        Apply field mapping to rename dataset columns to expected names.
        
        Args:
            df: Original dataframe with user column names
            field_mapping: Field mapping configuration from frontend
            
        Returns:
            Tuple of (renamed_dataframe, error_message)
        """
        if not field_mapping:
            # No field mapping provided, check if dataset already has correct columns
            required_columns = ['post']  # Only post is always required
            optional_columns = ['normalized claim']  # This is optional for referenceless metrics
            
            if 'post' in df.columns:
                print("No field mapping provided, but dataset has required 'post' column")
                return df, None
            else:
                return df, f"No field mapping provided and dataset doesn't have required 'post' column. Found: {df.columns.tolist()}"
        
        try:
            # Create a copy to avoid modifying the original
            df_renamed = df.copy()
            
            # Get the column mappings
            input_column = field_mapping.get('inputText')
            expected_output_column = field_mapping.get('expectedOutput')
            
            # Input column is always required
            if not input_column:
                return df, "Field mapping must specify inputText column"
            
            # Check if input column exists in the dataset
            if input_column not in df.columns:
                return df, f"Input column '{input_column}' not found in dataset. Available columns: {df.columns.tolist()}"
            
            # Check if expected output column exists (only if mapping is provided)
            if expected_output_column and expected_output_column not in df.columns:
                return df, f"Expected output column '{expected_output_column}' not found in dataset. Available columns: {df.columns.tolist()}"
            
            # Create column mapping dictionary
            column_mapping = {}
            
            # Always map input column to 'post'
            if input_column != 'post':
                column_mapping[input_column] = 'post'
            
            # Only map expected output if it's provided and different from target name
            if expected_output_column and expected_output_column != 'normalized claim':
                column_mapping[expected_output_column] = 'normalized claim'
            
            # Apply the column renaming
            if column_mapping:
                df_renamed = df_renamed.rename(columns=column_mapping)
                print(f"Applied column mapping: {column_mapping}")
                print(f"Original columns: {df.columns.tolist()}")
                print(f"Renamed columns: {df_renamed.columns.tolist()}")
            else:
                print("No column renaming needed - columns already have correct names")
            
            # Log whether we have reference claims or not
            has_reference_claims = 'normalized claim' in df_renamed.columns
            print(f"Dataset has reference claims: {has_reference_claims}")
            
            return df_renamed, None
            
        except Exception as e:
            return df, f"Error applying field mapping: {str(e)}"
    
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
            
            # Apply field mapping
            df, error_msg = ExtractionService.apply_field_mapping_to_dataset(df, extraction_data.field_mapping)
            if error_msg:
                progress_callback("error", {"message": error_msg})
                return None
            
            progress_callback("status", {"message": f"Applied field mapping. Dataset ready with columns: {df.columns.tolist()}"})
            
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
                refine_iters=extraction_data.refine_iterations,
                progress_callback=progress_callback,
                stop_event=stop_event,
                cross_refine_model=extraction_data.cross_refine_model,
                custom_prompt=extraction_data.custom_prompt,
                session_id=session_id
            )
            
            print(f"DEBUG: Type of combination_result: {type(combination_result)}, Value: {combination_result}")

            if combination_result:  # Only if not stopped
                combined_results_path, extracted_claims, reference_claims = combination_result

                # Prepare prompt information for storage - only store if custom prompt was used
                prompt_info = None
                if extraction_data.custom_prompt:
                    prompt_info = {
                        "is_custom": True,
                        "prompt_content": extraction_data.custom_prompt
                    }

                # Store extraction data in the session manager
                from .extraction_session import extraction_session_manager
                extraction_session_manager.store_extraction_data(
                    session_id=session_id,
                    extracted_claims=extracted_claims,
                    reference_claims=reference_claims,
                    model_combinations=[f"{extraction_data.models[0]}_{extraction_data.prompt_styles[0]}"], # Store model combination
                    prompt_info=prompt_info,
                    field_mapping=extraction_data.field_mapping
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

    @staticmethod
    def test_field_mapping():
        """Test function to validate field mapping functionality"""
        import pandas as pd
        
        print("Testing field mapping functionality...")
        
        # Test Case 1: Normal field mapping with both columns
        df1 = pd.DataFrame({
            'user_input': ['Post 1', 'Post 2'],
            'expected_claim': ['Claim 1', 'Claim 2'],
            'other_column': ['Other 1', 'Other 2']
        })
        field_mapping1 = {
            'inputText': 'user_input',
            'expectedOutput': 'expected_claim'
        }
        result_df1, error1 = ExtractionService.apply_field_mapping_to_dataset(df1, field_mapping1)
        print(f"Test 1 - Normal mapping: {'PASS' if not error1 and 'post' in result_df1.columns and 'normalized claim' in result_df1.columns else 'FAIL'}")
        if error1:
            print(f"Error: {error1}")
        
        # Test Case 2: Already correct column names
        df2 = pd.DataFrame({
            'post': ['Post 1', 'Post 2'],
            'normalized claim': ['Claim 1', 'Claim 2']
        })
        field_mapping2 = {
            'inputText': 'post',
            'expectedOutput': 'normalized claim'
        }
        result_df2, error2 = ExtractionService.apply_field_mapping_to_dataset(df2, field_mapping2)
        print(f"Test 2 - Already correct: {'PASS' if not error2 and 'post' in result_df2.columns and 'normalized claim' in result_df2.columns else 'FAIL'}")
        
        # Test Case 3: Missing column in mapping
        df3 = pd.DataFrame({
            'text': ['Post 1', 'Post 2'],
            'claim': ['Claim 1', 'Claim 2']
        })
        field_mapping3 = {
            'inputText': 'missing_column',
            'expectedOutput': 'claim'
        }
        result_df3, error3 = ExtractionService.apply_field_mapping_to_dataset(df3, field_mapping3)
        print(f"Test 3 - Missing column: {'PASS' if error3 and 'not found' in error3 else 'FAIL'}")
        
        # Test Case 4: Only input column (referenceless metrics)
        df4 = pd.DataFrame({
            'social_media_post': ['Post 1', 'Post 2'],
            'metadata': ['Meta 1', 'Meta 2']
        })
        field_mapping4 = {
            'inputText': 'social_media_post'
            # No expectedOutput - this is valid for referenceless metrics
        }
        result_df4, error4 = ExtractionService.apply_field_mapping_to_dataset(df4, field_mapping4)
        print(f"Test 4 - Referenceless only: {'PASS' if not error4 and 'post' in result_df4.columns and 'normalized claim' not in result_df4.columns else 'FAIL'}")
        if error4:
            print(f"Error: {error4}")
        
        # Test Case 5: No field mapping but correct post column
        df5 = pd.DataFrame({
            'post': ['Post 1', 'Post 2'],
            'other_data': ['Data 1', 'Data 2']
        })
        result_df5, error5 = ExtractionService.apply_field_mapping_to_dataset(df5, None)
        print(f"Test 5 - No mapping, correct post: {'PASS' if not error5 and 'post' in result_df5.columns else 'FAIL'}")
        
        # Test Case 6: No field mapping and wrong column names
        df6 = pd.DataFrame({
            'content': ['Post 1', 'Post 2'],
            'label': ['Claim 1', 'Claim 2']
        })
        result_df6, error6 = ExtractionService.apply_field_mapping_to_dataset(df6, None)
        print(f"Test 6 - No mapping, wrong columns: {'PASS' if error6 and 'post' in error6 else 'FAIL'}")
        
        print("Field mapping tests completed.")

# Uncomment to run tests:
# ExtractionService.test_field_mapping() 