import asyncio
import threading
import time
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..models.requests import EvaluationStartRequest, WebSocketMessage
from ..services.websocket_manager import websocket_manager
from ..services.evaluation_service import EvaluationService

router = APIRouter(prefix="/ws", tags=["evaluation"])

@router.websocket("/evaluation/{session_id}")
async def websocket_evaluation(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time evaluation progress updates
    """
    await websocket_manager.connect(websocket, session_id)
    
    try:
        while True:
            # Wait for messages from client
            message = await websocket.receive_json()
            
            if message.get("type") == "start_evaluation":
                # Parse evaluation data
                evaluation_data = EvaluationStartRequest(**message.get("data", {}))
                
                # Create stop event for this evaluation
                stop_event = websocket_manager.create_stop_event(session_id)
                
                # Start evaluation in background thread
                thread = threading.Thread(
                    target=run_evaluation_with_progress,
                    args=(session_id, evaluation_data, stop_event)
                )
                thread.start()
                
            elif message.get("type") == "stop_evaluation":
                # Signal to stop the evaluation
                websocket_manager.stop_evaluation(session_id)
                await websocket_manager.send_message(session_id, {
                    "type": "status",
                    "data": {"message": "Stopping evaluation..."}
                })
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id)

def run_evaluation_with_progress(
    session_id: str, 
    evaluation_data: EvaluationStartRequest, 
    stop_event: threading.Event
):
    """
    Run evaluation with progress updates sent via WebSocket
    """
    # Batched logging system
    log_batch = []
    last_flush_time = time.time()
    BATCH_SIZE = 10
    FLUSH_INTERVAL = 2.0
    
    def sync_send_update(update_type: str, data: Dict[str, Any]):
        try:
            # Check if stop event is set before sending updates
            if stop_event and stop_event.is_set():
                return
            
            # Handle different update types
            if update_type in ["progress", "status", "error", "complete"]:
                # Send immediately
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    websocket_manager.send_message(session_id, {
                        "type": update_type,
                        "data": data
                    })
                )
                loop.close()
            elif update_type == "log":
                # Batch log messages
                nonlocal log_batch, last_flush_time
                
                # Filter out verbose logs
                log_type = data.get("type", "")
                if log_type in ["debug", "feedback_detail", "iteration_start", "iteration_end"]:
                    return
                
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
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                websocket_manager.send_message(session_id, {
                    "type": "log_batch",
                    "data": {"messages": log_batch.copy()}
                })
            )
            loop.close()
            log_batch.clear()
        except Exception as e:
            print(f"Error flushing logs: {e}")
    
    def final_flush():
        """Flush any remaining logs at the end"""
        if log_batch:
            flush_logs()
    
    try:
        # Run evaluation with progress callback
        result = EvaluationService.run_evaluation_with_progress(
            session_id=session_id,
            evaluation_data=evaluation_data,
            progress_callback=sync_send_update,
            stop_event=stop_event
        )
        
        # Flush any remaining logs
        final_flush()
        
    except Exception as e:
        final_flush()
        sync_send_update("error", {"message": f"Evaluation failed: {str(e)}"})
        print(f"Error in evaluation thread: {str(e)}")
    finally:
        final_flush() 