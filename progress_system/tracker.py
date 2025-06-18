import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, Any, Union
from dataclasses import dataclass

@dataclass
class ProgressEvent:
    event_type: str
    agent_name: str
    message: str
    timestamp: str
    session_id: str
    data: Optional[Dict[str, Any]] = None
    level: int = 0  # For nested agents (0=root, 1=subagent, 2=sub-subagent)
    icon: str = "🔄"

class ProgressTracker:
    def __init__(self):
        self.session_queues: Dict[str, asyncio.Queue] = {}
        self.active_sessions: set = set()
        
    async def emit_event(self, session_id: str, event_data: Union[Dict[str, Any], str], agent_name: str = None, 
                        message: str = None, data: Optional[Dict[str, Any]] = None, 
                        level: int = 0, icon: str = "🔄", parent_agent: str = None):
        """
        Emit a progress event to the session queue
        Supports both new frontend format (dict) and legacy format (individual params)
        """
        
        # Handle new frontend format (dict input)
        if isinstance(event_data, dict):
            final_event = {
                "session_id": event_data.get("session_id", session_id),
                "agent_name": event_data.get("agent_name", "UnknownAgent"),
                "event_type": event_data.get("event_type", "agent_progress"),
                "timestamp": event_data.get("timestamp", datetime.utcnow().isoformat()),
                "data": event_data.get("data", {}),
            }
            
            # Add optional fields
            if "parent_agent" in event_data:
                final_event["parent_agent"] = event_data["parent_agent"]
                
        # Handle legacy format (individual parameters)
        else:
            final_event = {
                "session_id": session_id,
                "agent_name": agent_name or "UnknownAgent",
                "event_type": event_data,  # event_data is event_type in legacy format
                "timestamp": datetime.utcnow().isoformat(),
                "data": data or {},
            }
            
            if parent_agent:
                final_event["parent_agent"] = parent_agent
                
            # Add legacy fields for backward compatibility
            if message:
                final_event["data"]["message"] = message
            if icon:
                final_event["data"]["icon"] = icon
            if level is not None:
                final_event["data"]["level"] = level
        
        # Ensure session queue exists
        if session_id not in self.session_queues:
            self.session_queues[session_id] = asyncio.Queue()
            
        await self.session_queues[session_id].put(final_event)
        
        # Log event
        agent_name_display = final_event.get("agent_name", "Unknown")
        event_type = final_event.get("event_type", "unknown")
        message_display = final_event.get("data", {}).get("message", "")
        icon_display = final_event.get("data", {}).get("icon", "📡")
        print(f"📡 [{session_id}] {icon_display} {agent_name_display}: {event_type} - {message_display}")
        
    async def get_events_stream(self, session_id: str):
        """Generator for SSE events for a specific session - Frontend format"""
        self.active_sessions.add(session_id)
        
        # Create queue if it doesn't exist
        if session_id not in self.session_queues:
            self.session_queues[session_id] = asyncio.Queue()
            
        try:
            # Send initial connection event
            connection_event = {
                "session_id": session_id,
                "agent_name": "ProgressTracker",
                "event_type": "connection",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"message": "Progress tracking connected"}
            }
            yield f"data: {json.dumps(connection_event)}\n\n"
            
            # If there are already events in the queue, send them immediately
            # This handles the case where events were emitted before SSE connection
            pending_events = []
            while not self.session_queues[session_id].empty():
                try:
                    pending_event = self.session_queues[session_id].get_nowait()
                    pending_events.append(pending_event)
                except asyncio.QueueEmpty:
                    break
            
            # Send all pending events
            for event in pending_events:
                yield f"data: {json.dumps(event)}\n\n"
            
            # Stream events from the queue
            while session_id in self.active_sessions:
                try:
                    # Wait for event with timeout
                    event = await asyncio.wait_for(
                        self.session_queues[session_id].get(), 
                        timeout=30.0
                    )
                    
                    # Send event in frontend-expected format
                    yield f"data: {json.dumps(event)}\n\n"
                    
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    heartbeat_event = {
                        "session_id": session_id,
                        "agent_name": "ProgressTracker",
                        "event_type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": {}
                    }
                    yield f"data: {json.dumps(heartbeat_event)}\n\n"
                    
        except asyncio.CancelledError:
            pass
        finally:
            # Cleanup when client disconnects
            self.active_sessions.discard(session_id)
            if session_id in self.session_queues:
                # Clear any remaining events
                while not self.session_queues[session_id].empty():
                    try:
                        self.session_queues[session_id].get_nowait()
                    except asyncio.QueueEmpty:
                        break
                        
    def cleanup_session(self, session_id: str):
        """Clean up resources for a session"""
        self.active_sessions.discard(session_id)
        if session_id in self.session_queues:
            del self.session_queues[session_id]

# Agent event types
class EventType:
    AGENT_START = "agent_start"
    AGENT_PROGRESS = "agent_progress"
    AGENT_COMPLETE = "agent_complete"
    AGENT_ERROR = "agent_error"
    DATA_GENERATED = "data_generated"
    LOOP_ITERATION = "loop_iteration"
    VERIFICATION_START = "verification_start"
    VERIFICATION_COMPLETE = "verification_complete"
    ERROR = "error"
    SYSTEM_STATUS = "system_status"

# Agent configurations with icons and messages
AGENT_CONFIG = {
    "T1dInsightOrchestratorAgent": {
        "icon": "🎯",
        "start_message": "Starting T1D analysis orchestration...",
        "complete_message": "T1D analysis complete!",
        "level": 0
    },
    "AmbientContextSimulatorAgent": {
        "icon": "🧠",
        "start_message": "Analyzing ambient context...",
        "complete_message": "Context analysis complete",
        "level": 1
    },
    "SimulatedCGMFeedAgent": {
        "icon": "📊",
        "start_message": "Generating CGM data...",
        "complete_message": "CGM data generated",
        "level": 1
    },
    "RefinementLoopAgent": {
        "icon": "🔄",
        "start_message": "Starting refinement loop...",
        "complete_message": "Refinement loop complete",
        "level": 1
    },
    "GlycemicRiskForecastAgent": {
        "icon": "📈",
        "start_message": "Forecasting glycemic risk...",
        "complete_message": "Risk forecast generated",
        "level": 2
    },
    "ForecastVerifierAgent": {
        "icon": "🔍",
        "start_message": "Verifying forecast accuracy...",
        "complete_message": "Forecast verification complete",
        "level": 2
    },
    "LoopExitAgent": {
        "icon": "🎯",
        "start_message": "Checking exit conditions...",
        "complete_message": "Loop exit evaluation complete",
        "level": 2
    },
    "InsightPresenterAgent": {
        "icon": "📝",
        "start_message": "Preparing insights presentation...",
        "complete_message": "Insights ready!",
        "level": 1
    }
} 