from google.adk.agents import LoopAgent

from .subagents.glycemic_risk_forecast_agent.agent import GlycemicRiskForecasterAgent
from .subagents.forecast_verifier.agent import ForecastVerifierAgent
from .subagents.loop_exit_agent.agent import LoopExitAgent


RefinementLoopAgent = LoopAgent(    
    name="RefinementLoopAgent",
    sub_agents=[
        GlycemicRiskForecasterAgent,
        ForecastVerifierAgent,
        LoopExitAgent,
    ],
    max_iterations=3
)

