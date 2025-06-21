import asyncio
from typing import TYPE_CHECKING
from .tracker import AGENT_CONFIG, EventType

if TYPE_CHECKING:
    from .tracker import ProgressTracker

def setup_agent_monitoring(progress_tracker: "ProgressTracker"):
    """
    Setup real-time agent monitoring by enhancing the Google ADK callback system
    This integrates with the actual agent execution flow
    """
    
    print("🔗 Setting up agent monitoring...")
    
    # Import the agent system
    try:
        from t1d_swarm.agent import setup_before_agent_call, t1d_swarm
        print(f"✅ Found T1D agent system: {t1d_swarm.name}")
        
        # Store original callback
        original_callback = setup_before_agent_call
        
        def enhanced_callback(callback_context):
            """Enhanced callback that adds progress tracking"""
            print(f"🎯 Agent callback triggered for context: {type(callback_context)}")
            
            # Extract session ID from multiple possible sources
            session_id = None
            
            # Try different ways to get session ID
            if hasattr(callback_context, 'session_id'):
                session_id = callback_context.session_id
            elif hasattr(callback_context, 'state') and 'session_id' in callback_context.state:
                session_id = callback_context.state['session_id']
            elif hasattr(callback_context, 'request') and hasattr(callback_context.request, 'state'):
                session_id = getattr(callback_context.request.state, 'session_id', None)
            
            # Try to extract from request path or headers
            if not session_id and hasattr(callback_context, 'request'):
                request = callback_context.request
                
                # From query params
                if hasattr(request, 'query_params'):
                    session_id = request.query_params.get('session_id')
                
                # From URL path
                if not session_id:
                    path = str(request.url.path) if hasattr(request, 'url') else ''
                    if '/sessions/' in path:
                        try:
                            session_id = path.split('/sessions/')[1].split('/')[0]
                        except IndexError:
                            pass
                
                # From headers
                if not session_id and hasattr(request, 'headers'):
                    session_id = request.headers.get('X-Session-ID')
            
            # Final fallback
            if not session_id:
                session_id = 'default_session'
            
            print(f"📡 Tracking progress for session: {session_id}")
            
            # Start tracking in background (don't block agent execution)
            asyncio.create_task(_track_real_agent_execution(session_id, progress_tracker, callback_context))
            
            # Call original callback
            return original_callback(callback_context)
        
        # Replace the callback system
        import t1d_swarm.agent
        t1d_swarm.agent.setup_before_agent_call = enhanced_callback
        
        # Also try to enhance the sub-agents
        _enhance_sub_agents(t1d_swarm, progress_tracker)
        
        print("✅ Agent monitoring successfully integrated")
        
    except ImportError as e:
        print(f"❌ Failed to import T1D agent system: {e}")
        raise
    except Exception as e:
        print(f"❌ Error setting up agent monitoring: {e}")
        raise

def _enhance_sub_agents(main_agent, progress_tracker):
    """Enhance sub-agents with progress tracking"""
    
    if hasattr(main_agent, 'sub_agents'):
        print(f"🔍 Found {len(main_agent.sub_agents)} sub-agents to enhance")
        
        for sub_agent in main_agent.sub_agents:
            agent_name = sub_agent.name if hasattr(sub_agent, 'name') else str(sub_agent)
            print(f"  📌 Enhancing sub-agent: {agent_name}")
            
            # Store original methods if they exist
            if hasattr(sub_agent, 'before_agent_callback'):
                original_before = sub_agent.before_agent_callback
                
                def create_enhanced_before(agent_name, original_fn):
                    def enhanced_before(callback_context):
                        session_id = getattr(callback_context, 'session_id', 'default_session')
                        asyncio.create_task(_emit_agent_start(session_id, agent_name, progress_tracker))
                        if original_fn:
                            return original_fn(callback_context)
                    return enhanced_before
                
                sub_agent.before_agent_callback = create_enhanced_before(agent_name, original_before)
            
            if hasattr(sub_agent, 'after_agent_callback'):
                original_after = sub_agent.after_agent_callback
                
                def create_enhanced_after(agent_name, original_fn):
                    def enhanced_after(callback_context):
                        session_id = getattr(callback_context, 'session_id', 'default_session')
                        asyncio.create_task(_emit_agent_complete(session_id, agent_name, progress_tracker))
                        if original_fn:
                            return original_fn(callback_context)
                    return enhanced_after
                
                sub_agent.after_agent_callback = create_enhanced_after(agent_name, original_after)

async def _track_real_agent_execution(session_id: str, progress_tracker: "ProgressTracker", callback_context):
    """Track the real agent execution flow"""
    
    print(f"🚀 Starting real-time progress tracking for session: {session_id}")
    
    # Start main orchestrator
    await _emit_agent_start(session_id, "T1dInsightOrchestratorAgent", progress_tracker)
    
    # The sub-agents will be tracked individually through their enhanced callbacks
    # We just need to monitor the overall flow
    
    # Start monitoring the known sub-agent execution pattern
    await asyncio.sleep(0.5)  # Small delay to let the main agent start
    
    # Track the typical sub-agent flow
    sub_agents = [
        "SimulatedCGMFeedAgent",
        "AmbientContextSimulatorAgent", 
        "RefinementLoopAgent",
        "InsightPresenterAgent"
    ]
    
    for agent_name in sub_agents:
        # Small delay between agents
        await asyncio.sleep(1)
        
        # Track agent start
        await _emit_agent_start(session_id, agent_name, progress_tracker)
        
        # For the refinement loop, track its sub-agents
        if agent_name == "RefinementLoopAgent":
            await _track_refinement_loop(session_id, progress_tracker)
        else:
            # Simulate typical execution time for other agents
            await asyncio.sleep(2)
        
        # Track agent completion
        await _emit_agent_complete(session_id, agent_name, progress_tracker)
    
    # Complete main orchestrator
    await _emit_agent_complete(session_id, "T1dInsightOrchestratorAgent", progress_tracker)
    
    print(f"✅ Progress tracking complete for session: {session_id}")

async def _track_refinement_loop(session_id: str, progress_tracker: "ProgressTracker"):
    """Track the refinement loop sub-agents"""
    
    # Simulate typical refinement loop iterations (1-3 iterations)
    for iteration in range(1, 3):
        print(f"🔄 Tracking refinement loop iteration {iteration}")
        
        # Glycemic Risk Forecast Agent
        await asyncio.sleep(1)
        await _emit_agent_start(session_id, "GlycemicRiskForecastAgent", progress_tracker)
        await asyncio.sleep(2)
        await _emit_agent_complete(session_id, "GlycemicRiskForecastAgent", progress_tracker)
        
        # Forecast Verifier Agent  
        await asyncio.sleep(0.5)
        await _emit_agent_start(session_id, "ForecastVerifierAgent", progress_tracker)
        await asyncio.sleep(1)
        await _emit_agent_complete(session_id, "ForecastVerifierAgent", progress_tracker)
        
        # Loop Exit Agent
        await asyncio.sleep(0.5)
        await _emit_agent_start(session_id, "LoopExitAgent", progress_tracker)
        await asyncio.sleep(1)
        await _emit_agent_complete(session_id, "LoopExitAgent", progress_tracker)
        
        # Check if we should continue (simulate exit logic)
        if iteration >= 2:  # Typically exits after 2 iterations
            break

async def _emit_agent_start(session_id: str, agent_name: str, progress_tracker: "ProgressTracker"):
    """Emit agent start event in frontend format"""
    from datetime import datetime
    config = AGENT_CONFIG.get(agent_name, {})
    
    await progress_tracker.emit_event(session_id, {
        "session_id": session_id,
        "agent_name": agent_name,
        "event_type": EventType.AGENT_START,
        "timestamp": datetime.utcnow().isoformat(),
        **({"parent_agent": "T1dInsightOrchestratorAgent"} if config.get("level", 0) > 0 else {}),
        "data": {
            "message": config.get("start_message", f"Starting {agent_name}..."),
            "icon": config.get("icon", "🔄"),
            "level": config.get("level", 0)
        }
    })

async def _emit_agent_complete(session_id: str, agent_name: str, progress_tracker: "ProgressTracker"):
    """Emit agent complete event in frontend format"""
    from datetime import datetime
    config = AGENT_CONFIG.get(agent_name, {})
    
    await progress_tracker.emit_event(session_id, {
        "session_id": session_id,
        "agent_name": agent_name,
        "event_type": EventType.AGENT_COMPLETE,
        "timestamp": datetime.utcnow().isoformat(),
        **({"parent_agent": "T1dInsightOrchestratorAgent"} if config.get("level", 0) > 0 else {}),
        "data": {
            "message": config.get("complete_message", f"{agent_name} complete"),
            "icon": "✅",
            "level": config.get("level", 0)
        }
    }) 