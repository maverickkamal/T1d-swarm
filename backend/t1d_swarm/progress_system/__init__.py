from .tracker import ProgressTracker
from .agent_wrapper import setup_agent_monitoring
from .real_agent_tracker import RealAgentTracker

# Global progress tracker instance
progress_tracker = ProgressTracker()
real_agent_tracker = RealAgentTracker(progress_tracker)

def setup_progress_tracking(app):
    """Setup progress tracking system with the FastAPI app"""
    
    # Try to setup agent monitoring with the actual Google ADK callback system
    try:
        setup_agent_monitoring(progress_tracker)
        print("✅ Progress tracking integrated with agent callback system")
    except Exception as e:
        print(f"⚠️  Could not setup agent monitoring: {e}")
        
    print("✅ Progress tracking system initialized")
    
    return progress_tracker, real_agent_tracker

__all__ = ['setup_progress_tracking', 'progress_tracker', 'real_agent_tracker'] 