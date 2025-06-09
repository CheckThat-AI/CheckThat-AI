import asyncio
import threading
from typing import Dict, Any
from fastapi import WebSocket

class WebSocketManager:
    """Manages WebSocket connections and evaluation state"""
    
    def __init__(self):
        self.active_evaluations: Dict[str, Dict[str, Any]] = {}
        self.evaluation_stop_events: Dict[str, threading.Event] = {}
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        print(f"WebSocket connected for session: {session_id}")
    
    def disconnect(self, session_id: str):
        """Handle WebSocket disconnection"""
        print(f"WebSocket disconnected for session: {session_id}")
        
        # Clean up evaluation state
        if session_id in self.evaluation_stop_events:
            self.evaluation_stop_events[session_id].set()
            del self.evaluation_stop_events[session_id]
        
        if session_id in self.active_evaluations:
            del self.active_evaluations[session_id]
        
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send a message to a specific WebSocket connection"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                if websocket.client_state.name == 'CONNECTED':
                    await websocket.send_json(message)
            except Exception as e:
                print(f"Error sending WebSocket message to {session_id}: {e}")
    
    def create_stop_event(self, session_id: str) -> threading.Event:
        """Create and store a stop event for an evaluation"""
        stop_event = threading.Event()
        self.evaluation_stop_events[session_id] = stop_event
        return stop_event
    
    def stop_evaluation(self, session_id: str):
        """Signal to stop an evaluation"""
        if session_id in self.evaluation_stop_events:
            self.evaluation_stop_events[session_id].set()
    
    def is_connected(self, session_id: str) -> bool:
        """Check if a session is connected"""
        return session_id in self.active_connections

# Global instance
websocket_manager = WebSocketManager() 