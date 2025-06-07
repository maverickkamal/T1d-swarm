import json

from google.adk.agents import LlmAgent
from dotenv import load_dotenv

from .prompts import RISK_FORECASTER_PROMPT, RiskForecastOutput

load_dotenv()



MODEL_NAME = "gemini-2.5-pro-preview-05-06"

# --- Configure Llm Agent --- 

SCHEMA_JSON_STRING = json.dumps(RiskForecastOutput.model_json_schema(), indent=2)

instruction_for_agent = RISK_FORECASTER_PROMPT.format(
schema_string=SCHEMA_JSON_STRING
)

GlycemicRiskForecasterAgent = LlmAgent(
    model=MODEL_NAME,
    name="GlycemicRiskForecasterAgent",
    description="Generates glycemic risk forecasts based on CGM and context data.",
    instruction=instruction_for_agent,
    output_schema=RiskForecastOutput,
    output_key="risk_forecast",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)
