import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, Any, Union
from dataclasses import dataclass
from collections import deque

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
    """
    Manages real-time progress tracking for agent execution sessions.
    
    Uses asyncio queues for thread-safe event distribution to connected clients.
    Implements memory-conscious session management to prevent unbounded growth.
    
    Time Complexity Analysis:
    - emit_event: O(1) - Queue put operation
    - get_events_stream: O(1) per event yielded
    - Session management: O(1) for add/remove operations
    """
    
    def __init__(self, max_events_per_session: int = 1000):
        # Using bounded queues to prevent memory leaks
        # Time Complexity: O(1) for queue operations
        self.session_queues: Dict[str, asyncio.Queue] = {}
        self.active_sessions: set = set()
        self.max_events_per_session = max_events_per_session
        
    async def emit_event(self, session_id: str, event_data: Union[Dict[str, Any], str], agent_name: str = None, 
                        message: str = None, data: Optional[Dict[str, Any]] = None, 
                        level: int = 0, icon: str = "🔄", parent_agent: str = None):
        """
        Emit a progress event to the session queue.
        
        Supports both new frontend format (dict) and legacy format (individual params).
        Automatically manages queue size to prevent memory exhaustion.
        
        Args:
            session_id: Unique identifier for the session
            event_data: Event data (dict for new format, str for legacy)
            agent_name: Name of the agent generating the event
            message: Human-readable message
            data: Additional event data
            level: Nesting level for hierarchical agents
            icon: Display icon for the event
            parent_agent: Name of parent agent (for nested execution)
            
        Time Complexity: O(1) - Queue operations are constant time
        Space Complexity: O(1) per event, bounded by max_events_per_session
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
        
        # Ensure session queue exists with bounded size
        if session_id not in self.session_queues:
            # Using maxsize to prevent unbounded memory growth
            self.session_queues[session_id] = asyncio.Queue(maxsize=self.max_events_per_session)
            
        # Handle queue overflow gracefully
        try:
            await self.session_queues[session_id].put(final_event)
        except asyncio.QueueFull:
            # Remove oldest event and add new one (FIFO behavior)
            try:
                self.session_queues[session_id].get_nowait()
                await self.session_queues[session_id].put(final_event)
                print(f"⚠️ Session {session_id} queue overflow - removed oldest event")
            except asyncio.QueueEmpty:
                pass  # Queue somehow became empty, just continue
        
        # Log event for debugging
        agent_name_display = final_event.get("agent_name", "Unknown")
        event_type = final_event.get("event_type", "unknown")
        message_display = final_event.get("data", {}).get("message", "")
        icon_display = final_event.get("data", {}).get("icon", "📡")
        print(f"📡 [{session_id}] {icon_display} {agent_name_display}: {event_type} - {message_display}")
        
    async def get_events_stream(self, session_id: str):
        """
        Generator for SSE events for a specific session - Frontend format.
        
        Provides real-time streaming of agent progress events with automatic
        heartbeat and graceful error handling.
        
        Args:
            session_id: Unique session identifier
            
        Yields:
            str: SSE-formatted event data
            
        Time Complexity: O(1) per event - constant time event processing
        Memory Complexity: O(k) where k is bounded by max_events_per_session
        """
        self.active_sessions.add(session_id)
        
        # Create bounded queue if it doesn't exist
        if session_id not in self.session_queues:
            self.session_queues[session_id] = asyncio.Queue(maxsize=self.max_events_per_session)
            
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
            
            # Send any pending events that accumulated before SSE connection
            # O(k) where k is the number of pending events (bounded)
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
            
            # Stream events from the queue with heartbeat mechanism
            while session_id in self.active_sessions:
                try:
                    # Wait for event with timeout to enable heartbeat
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
            # Cleanup when client disconnects - O(1) operations
            self._cleanup_session_resources(session_id)
                        
    def _cleanup_session_resources(self, session_id: str):
        """
        Clean up resources for a session to prevent memory leaks.
        
        Removes session from active tracking and clears associated queue.
        Called automatically when SSE connection closes.
        
        Args:
            session_id: Session to clean up
            
        Time Complexity: O(k) where k is remaining events in queue
        """
        self.active_sessions.discard(session_id)
        if session_id in self.session_queues:
            # Clear any remaining events to free memory
            while not self.session_queues[session_id].empty():
                try:
                    self.session_queues[session_id].get_nowait()
                except asyncio.QueueEmpty:
                    break
            # Remove the queue reference
            del self.session_queues[session_id]
                        
    def cleanup_session(self, session_id: str):
        """
        Manual cleanup for external session management.
        
        Args:
            session_id: Session identifier to clean up
            
        Time Complexity: O(k) where k is remaining events in queue
        """
        self._cleanup_session_resources(session_id)

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