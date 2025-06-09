""" T1D Insight Orchestrator Agent"""

from google.adk.agents import SequentialAgent
from google.adk.agents.callback_context import CallbackContext

from .subagents.ambient_context_simulator_agent.agent import AmbientContextSimulatorAgent
from .subagents.refinement_loop_agent.agent import RefinementLoopAgent
from .subagents.simulated_cgm_feed_agent.agent import SimulatedCGMFeedAgent
from .subagents.insight_presenter_agent.agent import InsightPresenterAgent
from .tools import generate_scenario

def setup_before_agent_call(callback_context: CallbackContext):
    print("Setting up before agent call")

    if "scenario" not in callback_context.state:
        scenario = generate_scenario()
        callback_context.state["scenario"] = scenario
        print(f"Generated scenario: {scenario}")

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