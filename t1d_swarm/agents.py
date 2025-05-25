""" T1D Insight Orchestrator Agent"""

from google.adk.agents import SequentialAgent

from .subagents.ambient_context_simulator_agent import AmbientContextSimulatorAgent
from .subagents.glycemic_risk_forcaster_agent import GlycemicRiskForecasterAgent
from .subagents.simulated_cgm_feed_agent import SimulatedCGMFeedAgent

t1d_swarm = SequentialAgent(
    name='T1dInsightOrchestratorAgent',
    description='Orchestrates the flow of data and tasks between specialized sub-agents',
    sub_agents=[
        AmbientContextSimulatorAgent(),
        GlycemicRiskForecasterAgent(),
        SimulatedCGMFeedAgent(),
    ]
)

root_agent = t1d_swarm