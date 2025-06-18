import json
import os

from google.adk.agents import LlmAgent
from dotenv import load_dotenv

from .prompts import AMBIENT_CONTEXT_PROMPT, ContextEventOutput

load_dotenv()


MODEL_NAME = os.getenv("AMBIENT_CONTEXT_MODEL")

# --- Configure Llm Agent --- 

SCHEMA_JSON_STRING = json.dumps(ContextEventOutput.model_json_schema(), indent=2)

instruction_for_agent = AMBIENT_CONTEXT_PROMPT.format(
model_output=SCHEMA_JSON_STRING
)

AmbientContextSimulatorAgent = LlmAgent(
    model=MODEL_NAME,
    name="AmbientContextAgent",
    description="Creates a context to fit with the scenario.",
    instruction=instruction_for_agent,
    output_schema=ContextEventOutput,
    output_key="context_event",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)