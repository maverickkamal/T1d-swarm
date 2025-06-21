from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tracker import ProgressTracker

def setup_sse_routes(app: FastAPI, progress_tracker: "ProgressTracker"):
    """Add SSE routes to the FastAPI app"""
    
    @app.get("/stream-progress/{session_id}")
    async def stream_agent_progress(session_id: str):
        """
        Server-Sent Events endpoint for real-time agent progress
        
        Usage from frontend:
        const eventSource = new EventSource('/stream-progress/' + sessionId);
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
    
    @app.delete("/stream-progress/{session_id}")
    async def cleanup_progress_session(session_id: str):
        """Cleanup endpoint to free resources when session ends"""
        progress_tracker.cleanup_session(session_id)
        return {"message": f"Session {session_id} cleaned up"}
    
    print("✅ SSE progress endpoints registered: /stream-progress/{session_id}") 