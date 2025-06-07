import json

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from dotenv import load_dotenv

from .prompt import FORECAST_VERIFIER_PROMPT, VerificationOutput

load_dotenv()


MODEL_NAME = "gemini-2.5-flash-preview-05-20"

# --- Configure Llm Agent --- 

SCHEMA_JSON_STRING = json.dumps(VerificationOutput.model_json_schema(), indent=2)

instruction_for_agent = FORECAST_VERIFIER_PROMPT.format(
schema_string=SCHEMA_JSON_STRING
)

ForecastVerifierAgent = LlmAgent(
    model=MODEL_NAME,
    name="ForecastVerifierAgent",
    description="Verifies verification risk forecasts based on grounding data.",
    instruction=instruction_for_agent,
    tools=[google_search],
    output_key="verification_output",
)