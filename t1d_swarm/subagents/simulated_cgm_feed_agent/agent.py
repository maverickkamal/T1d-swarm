import json
import os

from google.adk.agents import LlmAgent
from dotenv import load_dotenv

from .prompts import SIMULATED_CGM_FEED_PROMPT, CGMDataOutput

load_dotenv()


MODEL_NAME = os.getenv("SIMULATED_CGM_MODEL")

# --- Configure Llm Agent --- 

SCHEMA_JSON_STRING = json.dumps(CGMDataOutput.model_json_schema(), indent=2)

instruction_for_agent = SIMULATED_CGM_FEED_PROMPT.format(
model_output=SCHEMA_JSON_STRING
)

SimulatedCGMFeedAgent = LlmAgent(
    model=MODEL_NAME,
    name="SimulatedCGMFeedAgent",
    description="Provides mock continuous glucose readings imitating that of a type 1 diabetes patient.",
    instruction=instruction_for_agent,
    output_schema=CGMDataOutput,
    output_key="cgm_data",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)
