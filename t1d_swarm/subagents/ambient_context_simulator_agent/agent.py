import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import LlmAgent
from .prompts import ModelOutput, ModelInput


root_agent = LlmAgent(
    name="Ambient_Context_Simulator_Agent",
    model="gemini-2.0-flash",
    description="Reads glucose readings from CGM and creates a context to fit with the readings.",
    instruction="You are a Ambient Context Simulator agent."
                "You will receive various glucose readings one-by-one from the CGM,"
                "By keeping track of the the glucose readings, create a situation which a person suffering from type 1 diabetes might be performing that correlates with the received glucose reading,"
                "generate a random glucose reading of a patient with type 1 diabetes,",
    input_schema = ModelInput,
    output_schema = ModelOutput,
)