import json

from google.adk.agents import LlmAgent
from dotenv import load_dotenv

from .prompts import risk_forecaster_prompts, RiskForecastOutput

load_dotenv()



MODEL_NAME = "gemini-2.5-pro-preview-05-06"

# --- Configure Llm Agent --- 

GlycemicRiskForecasterAgent = LlmAgent(
    model=MODEL_NAME,
    name="GlycemicRiskForecasterAgent",
    description="Generates glycemic risk forecasts based on CGM and context data.",
    instruction=risk_forecaster_prompts,
    output_schema=RiskForecastOutput,
    output_key="risk_forecast",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)
