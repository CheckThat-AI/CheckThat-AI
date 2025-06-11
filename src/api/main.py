from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import pandas as pd
import os
import sys
import json
import asyncio
import threading
from pathlib import Path
from fastapi.responses import StreamingResponse

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.utils.get_model_response import get_model_response
from src.utils.prompts import sys_prompt, few_shot_CoT_prompt
from src.utils.evaluate import start_evaluation

app = FastAPI(
    title="Claim Extraction and Normaization",
    description="API for the CLEF 2025 CheckThat Lab Task 2",
    version="1.0.0"
)

try:
    ENV_TYPE = os.getenv("ENV_TYPE", "dev")  # Default to dev if not set
except Exception as e:
    print(f"Error getting ENV_TYPE: {e}")
    ENV_TYPE = "dev"  # Default to dev on error
    
if ENV_TYPE == "dev":
    ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
else:
    ORIGINS = ["https://nikhil-kadapala.github.io", "https://www.claimnorm.com", "https:claimnorm.com"]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Global state for active evaluations
active_evaluations: Dict[str, Dict[str, Any]] = {}
evaluation_stop_events: Dict[str, threading.Event] = {}

# Pydantic models
class HealthCheck(BaseModel):
    status: str
    version: str

class EvalRequest(BaseModel):
    model: str
    prompt_style: str
    refine_iterations: int = 0
    eval_method: Optional[str] = None
    custom_prompt: Optional[str] = None
    api_key: Optional[str] = None
    cross_refine_model: Optional[str] = None

class ChatRequest(BaseModel):
    user_query: str
    model: str
    api_key: Optional[str] = None

@app.get("/", response_model=HealthCheck)
async def root():
    """
    Root endpoint that returns the API health status
    """
    return HealthCheck(status="healthy", version="1.0.0")

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint
    """
    return HealthCheck(status="healthy", version="1.0.0")

@app.post("/chat")
async def chat_interface(request: ChatRequest):
    """
    Endpoint to normalize a single claim from the user provided text
    """
    try:
        print("Received request:", request.model_dump_json(indent=4))

        valid_models = [
            "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            "claude-3.7-sonnet-latest",
            "gpt-4o-2024-11-20",
            "gpt-4.1-2025-04-14",
            "gpt-4.1-nano-2025-04-14",
            "gemini-2.5-pro-preview-05-06",
            "gemini-2.5-flash-preview-04-17",
            "grok-3-latest"
        ]
        
        API_PROVIDER: Optional[str] = None
        
        if request.model not in valid_models:
            print(f"Invalid model: {request.model}")
            raise HTTPException(status_code=400, detail=f"Invalid model. Must be one of: {', '.join(valid_models)}")
        
        if request.model in ["gpt-4o-2024-11-20", "gpt-4.1-2025-04-14", "gpt-4.1-nano-2025-04-14", "grok-3-latest"]:
            API_PROVIDER = "OPENAI"
        elif request.model in ["claude-3.7-sonnet-latest"]:
            API_PROVIDER = "ANTHROPIC"
        elif request.model in ["gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-04-17"]:
            API_PROVIDER = "GEMINI"
        else:
            API_PROVIDER = "TOGETHER"
        
        if request.api_key:
            os.environ[f"{API_PROVIDER}_API_KEY"] = request.api_key

        def stream_response():
            for chunk in get_model_response(
                model=request.model,
                user_prompt=f"{few_shot_CoT_prompt}\n\n{request.user_query}",
                sys_prompt=sys_prompt,
                gen_type="chat"
            ):
                yield chunk

        return StreamingResponse(stream_response(), media_type="text/plain")

    except Exception as e:
        print("Error in chat_interface:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/evaluation/{session_id}")
async def websocket_evaluation(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time evaluation progress updates
    """
    await websocket.accept()
    print(f"WebSocket connected for session: {session_id}")
    
    try:
        while True:
            # Wait for messages from client or send periodic updates
            message = await websocket.receive_json()
            
            if message.get("type") == "start_evaluation":
                # Start evaluation in a separate thread
                evaluation_data = message.get("data", {})
                
                # Create stop event for this evaluation
                stop_event = threading.Event()
                evaluation_stop_events[session_id] = stop_event
                
                # Start evaluation in background thread
                thread = threading.Thread(
                    target=run_evaluation_with_progress,
                    args=(session_id, evaluation_data, websocket, stop_event)
                )
                thread.start()
                
            elif message.get("type") == "stop_evaluation":
                # Signal to stop the evaluation
                if session_id in evaluation_stop_events:
                    evaluation_stop_events[session_id].set()
                    await websocket.send_json({
                        "type": "status",
                        "data": {"message": "Stopping evaluation..."}
                    })
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session: {session_id}")
        # Clean up
        if session_id in evaluation_stop_events:
            evaluation_stop_events[session_id].set()
            del evaluation_stop_events[session_id]
        if session_id in active_evaluations:
            del active_evaluations[session_id]

def run_evaluation_with_progress(session_id: str, evaluation_data: dict, websocket: WebSocket, stop_event: threading.Event):
    """
    Run evaluation with progress updates sent via WebSocket
    """
    import asyncio
    import time
    from threading import Lock
    
    # Batched logging system
    log_batch = []
    log_batch_lock = Lock()
    last_flush_time = time.time()
    BATCH_SIZE = 10  # Send logs when we have 10+ messages
    FLUSH_INTERVAL = 2.0  # Send logs every 2 seconds regardless
    
    async def send_update(update_type: str, data: dict):
        try:
            # Check if WebSocket is still open before sending
            if websocket.client_state.name == 'CONNECTED':
                await websocket.send_json({
                    "type": update_type,
                    "data": data
                })
        except Exception as e:
            print(f"Error sending WebSocket update: {e}")
    
    def sync_send_update(update_type: str, data: dict):
        try:
            # Check if stop event is set before sending updates
            if stop_event and stop_event.is_set():
                return
            
            # Handle different update types
            if update_type == "progress" or update_type == "status" or update_type == "error" or update_type == "complete":
                # Send progress, status, error, and completion messages immediately
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(send_update(update_type, data))
                loop.close()
            elif update_type == "log":
                # Batch log messages
                nonlocal log_batch, last_flush_time
                
                # Filter out verbose logs - only keep important ones
                log_type = data.get("type", "")
                if log_type in ["debug", "feedback_detail", "iteration_start", "iteration_end"]:
                    return  # Skip verbose logs
                
                with log_batch_lock:
                    log_batch.append(data)
                    current_time = time.time()
                    
                    # Flush if batch is full or enough time has passed
                    if len(log_batch) >= BATCH_SIZE or (current_time - last_flush_time) >= FLUSH_INTERVAL:
                        flush_logs()
                        last_flush_time = current_time
        except Exception as e:
            print(f"Error in sync_send_update: {e}")
    
    def flush_logs():
        """Send batched logs immediately"""
        nonlocal log_batch
        if not log_batch:
            return
            
        try:
            # Send all batched logs as a single message
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(send_update("log_batch", {"messages": log_batch.copy()}))
            loop.close()
            log_batch.clear()
        except Exception as e:
            print(f"Error flushing logs: {e}")
    
    def final_flush():
        """Flush any remaining logs at the end"""
        with log_batch_lock:
            if log_batch:
                flush_logs()
    
    try:
        # Send initial status
        sync_send_update("status", {"message": "Starting evaluation...", "progress": 0})
        # Parse evaluation data
        models = evaluation_data.get('models', [])
        prompt_styles = evaluation_data.get('prompt_styles', [])
        file_data = evaluation_data.get('file_data')
        self_refine_iterations = evaluation_data.get('self_refine_iterations', 0)
        api_keys = evaluation_data.get('api_keys', {})
        cross_refine_model = evaluation_data.get('cross_refine_model', None)
        field_mapping = evaluation_data.get('field_mapping', None)
        eval_metric = evaluation_data.get('eval_metric', None)
        
        if not models or not prompt_styles or not file_data:
            sync_send_update("error", {"message": "Missing required evaluation data"})
            return
        
        # Set API keys
        for provider, api_key in api_keys.items():
            if api_key:
                os.environ[f"{provider.upper()}_API_KEY"] = api_key
        
        # Load dataset from file data
        try:
            import io
            import base64
            
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
                sync_send_update("error", {"message": "Unsupported file format"})
                return
                
            sync_send_update("status", {"message": f"Loaded dataset with {len(df)} rows"})
            
        except Exception as e:
            sync_send_update("error", {"message": f"Error loading dataset: {str(e)}"})
            return
        
        # Validate required columns
        required_columns = ['post', 'normalized claim']
        if not all(col in df.columns for col in required_columns):
            sync_send_update("error", {"message": f"Dataset must contain columns: {required_columns}. Found: {df.columns.tolist()}"})
            return
        
        # Create progress callback
        def progress_callback(update_type: str, data: dict):
            sync_send_update(update_type, data)
        
        # Run evaluation with progress updates
        sync_send_update("status", {"message": "Running evaluation...", "progress": 0})
        
        combination_scores = start_evaluation(
            models=models,
            prompt_styles=prompt_styles,
            input_data=df,
            refine_iters=self_refine_iterations,
            progress_callback=progress_callback,
            stop_event=stop_event,
            cross_refine_model=cross_refine_model,
            field_mapping=field_mapping,
            eval_metric=eval_metric
        )
        
        # Flush any remaining logs
        final_flush()
        
        if combination_scores:  # Only if not stopped
            sync_send_update("complete", {
                "message": "Evaluation completed successfully",
                "scores": combination_scores
            })
        else:
            sync_send_update("status", {"message": "Evaluation was stopped"})
        
    except Exception as e:
        final_flush()  # Flush logs even on error
        sync_send_update("error", {"message": f"Evaluation failed: {str(e)}"})
        print(f"Error in evaluation: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        final_flush()  # Final flush
        if session_id in evaluation_stop_events:
            del evaluation_stop_events[session_id]
        if session_id in active_evaluations:
            del active_evaluations[session_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
