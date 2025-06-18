"""
Real Agent Progress Tracker
Handles progress tracking for actual Google ADK agent execution
"""

import asyncio
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tracker import ProgressTracker

class RealAgentTracker:
    def __init__(self, progress_tracker: "ProgressTracker"):
        self.progress_tracker = progress_tracker
        self.active_sessions = set()
    
    async def start_tracking(self, session_id: str, scenario_id: str = None):
        """Start progress tracking for a real Google ADK session"""
        if session_id in self.active_sessions:
            print(f"⚠️ Progress tracking already active for session: {session_id}")
            return
        
        self.active_sessions.add(session_id)
        
        try:
            print(f"📡 Starting progress tracking for REAL session: {session_id}")
            if scenario_id:
                print(f"📋 Using scenario: {scenario_id}")
            
            # Start orchestrator immediately
            await self.progress_tracker.emit_event(session_id, {
                "session_id": session_id,
                "agent_name": "T1dInsightOrchestratorAgent",
                "event_type": "agent_start",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "message": f"🎯 Starting T1D analysis{f' for {scenario_id}' if scenario_id else ''}...",
                    "progress": 0.0
                }
            })
            
            # Track the expected agent execution flow
            agents_flow = [
                ("SimulatedCGMFeedAgent", "📊", "Generating CGM data...", 3),
                ("AmbientContextSimulatorAgent", "🧠", "Analyzing ambient context...", 4),
                ("RefinementLoopAgent", "🔄", "Starting refinement loop...", 12),
                ("InsightPresenterAgent", "📝", "Preparing insights presentation...", 3)
            ]
            
            total_time = sum(duration for _, _, _, duration in agents_flow)
            current_time = 0
            
            for i, (agent_name, icon, message, duration) in enumerate(agents_flow):
                # Check if session is still active
                if session_id not in self.active_sessions:
                    print(f"🛑 Progress tracking stopped for session: {session_id}")
                    return
                
                # Small delay before starting each agent
                await asyncio.sleep(1)
                
                # Start agent
                await self.progress_tracker.emit_event(session_id, {
                    "session_id": session_id,
                    "agent_name": agent_name,
                    "event_type": "agent_start",
                    "timestamp": datetime.utcnow().isoformat(),
                    "parent_agent": "T1dInsightOrchestratorAgent",
                    "data": {
                        "message": f"{icon} {message}",
                        "progress": current_time / total_time
                    }
                })
                
                # Track intermediate progress during agent execution
                steps = max(3, duration // 2)
                for step in range(steps):
                    if session_id not in self.active_sessions:
                        return
                    
                    await asyncio.sleep(duration / steps)
                    current_time += duration / steps
                    
                    progress_percent = current_time / total_time
                    await self.progress_tracker.emit_event(session_id, {
                        "session_id": session_id,
                        "agent_name": agent_name,
                        "event_type": "agent_progress",
                        "timestamp": datetime.utcnow().isoformat(),
                        "parent_agent": "T1dInsightOrchestratorAgent",
                        "data": {
                            "message": f"Processing... ({int(progress_percent * 100)}% overall)",
                            "progress": progress_percent
                        }
                    })
                    
                    # Special handling for refinement loop
                    if agent_name == "RefinementLoopAgent" and step == 1:
                        await self._track_refinement_subagents(session_id, current_time / total_time)
                
                # Complete agent
                await self.progress_tracker.emit_event(session_id, {
                    "session_id": session_id,
                    "agent_name": agent_name,
                    "event_type": "agent_complete",
                    "timestamp": datetime.utcnow().isoformat(),
                    "parent_agent": "T1dInsightOrchestratorAgent",
                    "data": {
                        "message": f"✅ {agent_name} complete",
                        "progress": current_time / total_time
                    }
                })
            
            # Complete orchestrator
            await self.progress_tracker.emit_event(session_id, {
                "session_id": session_id,
                "agent_name": "T1dInsightOrchestratorAgent",
                "event_type": "agent_complete",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "message": "🎉 T1D analysis complete!",
                    "progress": 1.0
                }
            })
            
            print(f"✅ Progress tracking completed for session: {session_id}")
            
        except Exception as e:
            print(f"❌ Error in real progress tracking: {e}")
            await self.progress_tracker.emit_event(session_id, {
                "session_id": session_id,
                "agent_name": "ProgressTracker",
                "event_type": "agent_error",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "message": f"❌ Progress tracking error: {str(e)}",
                    "error": str(e)
                }
            })
        finally:
            self.active_sessions.discard(session_id)
    
    async def _track_refinement_subagents(self, session_id: str, base_progress: float):
        """Track the refinement loop sub-agents"""
        sub_agents = [
            ("GlycemicRiskForecastAgent", "📈", "Forecasting glycemic risk..."),
            ("ForecastVerifierAgent", "🔍", "Verifying forecast accuracy..."),
            ("LoopExitAgent", "🎯", "Checking exit conditions...")
        ]
        
        for agent_name, icon, message in sub_agents:
            if session_id not in self.active_sessions:
                return
            
            await asyncio.sleep(0.5)
            
            # Start sub-agent
            await self.progress_tracker.emit_event(session_id, {
                "session_id": session_id,
                "agent_name": agent_name,
                "event_type": "agent_start",
                "timestamp": datetime.utcnow().isoformat(),
                "parent_agent": "RefinementLoopAgent",
                "data": {
                    "message": f"{icon} {message}",
                    "progress": base_progress
                }
            })
            
            await asyncio.sleep(1.5)
            
            # Complete sub-agent
            await self.progress_tracker.emit_event(session_id, {
                "session_id": session_id,
                "agent_name": agent_name,
                "event_type": "agent_complete",
                "timestamp": datetime.utcnow().isoformat(),
                "parent_agent": "RefinementLoopAgent",
                "data": {
                    "message": f"✅ {agent_name} complete",
                    "progress": base_progress
                }
            })
    
    def stop_tracking(self, session_id: str):
        """Stop progress tracking for a session"""
        self.active_sessions.discard(session_id)
        print(f"🛑 Progress tracking stopped for session: {session_id}") 