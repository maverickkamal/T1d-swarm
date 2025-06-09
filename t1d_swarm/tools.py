# import os

from google import genai
from google.genai import types
from google.genai.types import HttpOptions
from dotenv import load_dotenv
from pydantic import BaseModel

from .prompt import *

load_dotenv()


client = genai.Client(http_options=HttpOptions(api_version="v1"))

class ScenarioDict(BaseModel):
    scenarios: str



def generate_scenario():
    """ Generates a random but realistic scenario sentence inspired by the real world."""
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        config=types.GenerateContentConfig(
            system_instruction=CALLBACK_PROMPT,
            temperature=1.2,
            max_output_tokens=500,
            response_mime_type='application/json',
            response_schema=ScenarioDict
        ),
        contents=['Generate a new, random but realistic scenario sentence inspired by the real world.']  
    )

    if ScenarioDict.model_validate_json(response.text):
        return response.text
    else:
        raise ValueError("Scenario validation failed.")
