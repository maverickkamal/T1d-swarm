# import datetime
# from zoneinfo import ZoneInfo
# from google.adk.agents import LlmAgent
# from .prompts import ModelOutput, ModelInput


# root_agent = LlmAgent(
#     name="Ambient_Context_Simulator_Agent",
#     model="gemini-2.0-flash",
#     description="Reads glucose readings from CGM and creates a context to fit with the readings.",
#     instruction="You are a Ambient Context Simulator agent."
#                 "You will receive various glucose readings one-by-one from the CGM,"
#                 "By keeping track of the the glucose readings, create a situation which a person suffering from type 1 diabetes might be performing that correlates with the received glucose reading,"
#                 "generate a random glucose reading of a patient with type 1 diabetes,",
#     input_schema = ModelInput,
#     output_schema = ModelOutput,
# )

import json

from google.adk.agents import LlmAgent
from dotenv import load_dotenv

from .prompts import AMBIENT_CONTEXT_PROMPT, ContextEventOutput

load_dotenv()


MODEL_NAME = "gemini-2.0-flash"

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