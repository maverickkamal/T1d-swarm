""" T1D Insight Orchestrator Agent"""

from google.adk.agents import SequentialAgent
from google.adk.agents.callback_context import CallbackContext

from .subagents.ambient_context_simulator_agent.agent import AmbientContextSimulatorAgent
from .subagents.refinement_loop_agent.agent import RefinementLoopAgent
from .subagents.simulated_cgm_feed_agent.agent import SimulatedCGMFeedAgent
from .subagents.insight_presenter_agent.agent import InsightPresenterAgent
from .tools import generate_scenario, get_scenario_details

# Global variable to store the selected scenario from frontend
_selected_scenario = None

def set_global_scenario(scenario: dict):
    """Set the global scenario to be used by the agent"""
    global _selected_scenario
    _selected_scenario = scenario

def get_global_scenario():
    """Get the globally stored scenario"""
    global _selected_scenario
    return _selected_scenario

def setup_before_agent_call(callback_context: CallbackContext):
    print("Setting up before agent call")

    if "scenario" not in callback_context.state:
        # Try to get the scenario from global storage
        selected_scenario = get_global_scenario()
        
        if selected_scenario:
            scenario = get_scenario_details(selected_scenario['scenario_id'], selected_scenario['custom_text'])
            print(f"Using scenario from frontend: {scenario}")
        else:
            # Fallback to generating a scenario if none selected from frontend
            scenario = generate_scenario()
            print(f"No scenario from frontend, generated: {scenario}")
        
        callback_context.state["scenario"] = scenario

t1d_swarm = SequentialAgent(
    name='T1dInsightOrchestratorAgent',
    description='Orchestrates the flow of data and tasks between specialized sub-agents',
    sub_agents=[
        SimulatedCGMFeedAgent,
        AmbientContextSimulatorAgent,
        RefinementLoopAgent,
        InsightPresenterAgent
    ],
    before_agent_callback=setup_before_agent_call
)

root_agent = t1d_swarm