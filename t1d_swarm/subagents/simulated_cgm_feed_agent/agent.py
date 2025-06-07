import json

from google.adk.agents import LlmAgent
# from google.genai import types
from dotenv import load_dotenv

from .prompts import SIMULATED_CGM_FEED_PROMPT, CGMDataOutput

load_dotenv()


MODEL_NAME = "gemini-2.0-flash"

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


# import datetime
# from zoneinfo import ZoneInfo
# from google.adk.agents import LlmAgent
# from .prompts import ModelOutput


# root_agent = LlmAgent(
#     name="weather_agent_v1",
#     model="gemini-2.0-flash", # Can be a string for Gemini or a LiteLlm object
#     description="Provides mock continuous glucose readings imitating that of a type 1 diabetes patient.",
#     instruction="You are a continuous glucose monitoring system. "
#                 "When the user asks for a glucose reading, "
#                 "generate a random glucose reading of a patient with type 1 diabetes,"
#                 "Keep track of all the glucose readings you've produced and generate a trend supporting those readings,"
#                 "Here are the trend values that you should use and when to use them,"
#                 "return 'DoubleUp' to indicate patients glucose is rising rapidly, use this when the current reading is higher than the previous reading by 50,"
#                 "return 'SingleUp' to indicate patients glucose is rising, use this when the current reading is higher than the previous reading by 20,"
#                 "return 'FortyFiveUp' to indicate patients glucose is rising slowly, use this when the current reading is slightly higher than the previous reading,"
#                 "return 'Flat' to indicate patients glucose is constant,"
#                 "return 'FortyFiveDown' to indicate patients glucose is falling slowly,"
#                 "return 'SingleDown' to indicate patients glucose is falling,"
#                 "return 'DoubleDown' to indicate patients glucose is falling rapidly,"
#                 "return 'NOT_COMPUTABLE' to indicate the CGM has no reading of patients glucose,"
#                 "return 'Error' to indicate issues with CGM reading"
#                 "Also randomly simulate the cgm monitor having issues reading patients data accurately",
#     output_schema = ModelOutput,
# )