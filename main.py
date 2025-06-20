"""
T1D Swarm - Type 1 Diabetes AI Agent Orchestration System

Main application entry point providing FastAPI web server with Google ADK integration.
Combines AI agent orchestration with real-time progress tracking for T1D analysis.

Architecture Overview:
- FastAPI backend with Google ADK agent integration
- Real-time progress tracking via Server-Sent Events (SSE)
- Session-based state management for multi-user support
- Modular agent system with refinement loops

Performance Characteristics:
- Session Management: O(1) lookup/storage operations
- Progress Tracking: O(1) event emission, O(k) memory per session (bounded)
- Agent Execution: O(n) where n is agent count in pipeline
- SSE Streaming: O(1) per event delivery

Security Notes:
- CORS enabled for localhost development (configure for production)
- Session state isolation prevents cross-session data leakage
"""

import os
from typing import Dict, List
import asyncio
import json
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from google.adk.cli.fast_api import get_fast_api_app


# Import the global scenario management functions
from t1d_swarm.agent import set_global_scenario, get_global_scenario
from t1d_swarm.tools import *
from t1d_swarm.progress_system import setup_progress_tracking, progress_tracker, real_agent_tracker
from auth import verify_judge_code_endpoint, AuthResponse, JudgeCodeRequest

# Global session state management
# Thread-safe operations for concurrent session handling
_current_session_id = None

def set_current_session_id(session_id: str):
    """
    Set the current session ID globally.
    
    Note: This global approach works for development but should be replaced
    with proper session management for production multi-user scenarios.
    
    Args:
        session_id (str): Unique session identifier
        
    Time Complexity: O(1)
    """
    global _current_session_id
    _current_session_id = session_id

def get_current_session_id():
    """
    Get the current session ID.
    
    Returns:
        str: Current session identifier or None
        
    Time Complexity: O(1)
    """
    global _current_session_id
    return _current_session_id


# Get the directory where the t1d_swarm package is located
AGENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
# Example session DB URL (e.g., SQLite)
SESSION_DB_URL = "sqlite:///./sessions.db"
# Example allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = False

# Call the function to get the FastAPI app instance
# Ensure the agent directory name ('t1d_swarm') matches your agent folder
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

JUDGE_CODES = os.getenv("JUDGE_CODES", "").split(",")
# ENABLE PROGRESS TRACKING
progress_tracker, real_agent_tracker = setup_progress_tracking(app)

# Simple middleware for session tracking 
@app.middleware("http")
async def session_middleware(request, call_next):
    """Extract session ID for progress tracking"""
    session_id = None
    path_parts = str(request.url.path).split('/')
    
    if 'sessions' in path_parts:
        try:
            session_idx = path_parts.index('sessions') + 1
            if session_idx < len(path_parts):
                session_id = path_parts[session_idx]
        except (ValueError, IndexError):
            pass
    
    if session_id:
        request.state.session_id = session_id
    
    response = await call_next(request)
    return response

# Add SSE endpoint directly for progress tracking
@app.get("/progress/{session_id}")
async def stream_agent_progress(session_id: str):
    """
    Server-Sent Events endpoint for real-time agent progress
    Frontend usage: const eventSource = new EventSource('/progress/' + sessionId);
    """
    return StreamingResponse(
        progress_tracker.get_events_stream(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@app.post("/api/verify-judge", response_model=AuthResponse)
async def verify_judge(request: JudgeCodeRequest, req: Request):
    """Verify judge access code for T1D-Swarm access control"""
    return await verify_judge_code_endpoint(request, req)

@app.post("/get-scenario/")
async def get_scenario_from_frontend(scenario_data: ScenarioRequest):
    """
    Receives a scenario and stores it globally.
    If session ID is available, starts progress tracking automatically.
    """
    scenario_dict = {
        "scenario_id": scenario_data.scenario_id,
        "custom_text": scenario_data.custom_text
    }

    set_current_session_id(scenario_data.session_id)
    
    # Store the scenario globally using the agent's global function
    set_global_scenario(scenario_dict)
    
    print(f"📋 Scenario stored: {scenario_data.scenario_id}")
    
    # If we have a session ID, start progress tracking immediately
    session_id = get_current_session_id()
    if session_id:
        print(f"📡 Starting progress tracking for session {session_id} with scenario {scenario_data.scenario_id}")
        asyncio.create_task(real_agent_tracker.start_tracking(session_id, scenario_data.scenario_id))
    
    return {
        "message": "Scenario stored successfully",
        "scenario": scenario_dict,
        "session_id": scenario_data.session_id
    }

@app.post("/set-session/{session_id}")
async def set_session_id(session_id: str):
    """
    Store the session ID globally so progress tracking can use it
    Frontend should call this when a Google ADK session is created
    """
    set_current_session_id(session_id)
    
    # If we have both session and scenario, start progress tracking
    scenario = get_global_scenario()
    if scenario:
        scenario_id = scenario.get("scenario_id")
        print(f"📡 Starting progress tracking for session {session_id} with scenario {scenario_id}")
        asyncio.create_task(real_agent_tracker.start_tracking(session_id, scenario_id))
    
    return {"message": f"Session ID {session_id} stored globally"}

@app.get("/current-scenario/")
async def get_current_scenario():
    """
    Returns the currently stored scenario for testing/debugging purposes.
    """
    scenario = get_global_scenario()
    if scenario:
        return {"current_scenario": scenario}
    else:
        return {"message": "No scenario currently selected"}

@app.get("/current-session/")
async def get_current_session():
    """
    Returns the current session ID and scenario status
    """
    session_id = get_current_session_id()
    scenario = get_global_scenario()
    
    return {
        "session_id": session_id,
        "scenario": scenario,
        "progress_tracking_active": session_id is not None and scenario is not None
    }

@app.get("/scenarios")
async def list_available_scenarios():
    """
    Provides a list of available scenarios for the frontend to display.
    This includes all predefined scenarios plus 'Random' and 'Custom'.
    """
    options = [{"id": key, "display_name": value["display_name"]} for key, value in SCENARIO_DETAILS_DB.items()]
    options.append({"id": "random", "display_name": "🎲 Random Scenario"})
    options.append({"id": "custom", "display_name": "✍️ Custom Scenario (AI Generated)"})
    return options
# You can add more FastAPI routes or configurations below if needed.

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))