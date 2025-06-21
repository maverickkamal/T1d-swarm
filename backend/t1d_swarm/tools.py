import random
import os
from typing import Dict, Optional
from fastapi import HTTPException
from pydantic import BaseModel

from google import genai
from google.genai import types
from google.genai.types import HttpOptions
from dotenv import load_dotenv

from .prompt import *

load_dotenv()

MODEL = os.getenv("GENERATE_SCENARIO_MODEL")

client = genai.Client(http_options=HttpOptions(api_version="v1"))

class ScenarioDict(BaseModel):
    scenarios: str


def generate_scenario():
    """
    Generates a random but realistic scenario sentence inspired by the real world.
    
    Uses Google's Gemini API to create contextually appropriate T1D scenarios.
    
    Returns:
        str: JSON string containing the generated scenario
        
    Raises:
        ValueError: If scenario validation fails
        
    Time Complexity: O(1) - Single API call with fixed parameters
    """
    response = client.models.generate_content(
        model=MODEL,
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

def rephrase_custom_scenario(custom_text: str):
    """
    Rephrase the custom text into a properly formatted scenario sentence.
    
    Takes user input and transforms it into a medically appropriate T1D scenario
    using Google's Gemini API.
    
    Args:
        custom_text (str): Raw user input describing their scenario
        
    Returns:
        str: JSON string containing the rephrased scenario
        
    Raises:
        ValueError: If scenario validation fails
        
    Time Complexity: O(1) - Single API call with fixed parameters
    """
    response = client.models.generate_content(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=REPHRASE_PROMPT,
            temperature=0.5,
            max_output_tokens=500,
            response_mime_type='application/json',
            response_schema=ScenarioDict
        ),
        contents=[custom_text]  
    )

    if ScenarioDict.model_validate_json(response.text):
        return response.text
    else:
        raise ValueError("Scenario validation failed.")


# --- Robust Scenario Definitions ---
# This dictionary holds the detailed scenario descriptions that will be fed
# into your simulator agents. The keys are simple identifiers.
# 
# Design note: Using a dictionary for O(1) lookup time instead of iterating through lists

SCENARIO_DETAILS_DB: Dict[str, Dict[str, str]] = {
    "stable_day": {
        "display_name": "1. Stable Day",
        "scenario_description": "A normal day where a user's glucose is relatively stable within the target range. The user reports eating a small, balanced snack like an apple with peanut butter about an hour ago."
    },
    "high_carb_hyper": {
        "display_name": "2. High-Carb Meal (Hyperglycemia)",
        "scenario_description": "A user has consumed a large, high-carbohydrate meal and is now experiencing a significant and rapid rise in glucose. They report having just eaten a large bowl of pasta, garlic bread, and a sugary soda for lunch."
    },
    "post_exercise_hypo": {
        "display_name": "3. Post-Exercise (Hypoglycemia)",
        "scenario_description": "A user has just completed a moderate-intensity workout, and their glucose is now trending steadily downwards, posing a risk of post-exercise hypoglycemia. They report just finishing a 45-minute run on the treadmill."
    },
    "complex_meal_delayed_spike": {
        "display_name": "4. Complex Meal (Delayed Spike)",
        "scenario_description": "A user ate a meal high in both fat and carbs (like pizza) an hour ago. Their glucose is currently stable but a delayed and prolonged rise is expected due to the fat content slowing carb absorption."
    },
    "edge_case_sensor_failure": {
        "display_name": "5. Edge Case: Sensor Failure",
        "scenario_description": "A user's CGM sensor is malfunctioning, providing erratic, jumpy readings and data gaps. The user notes that the CGM readings have been unreliable and don't match how they feel."
    },
    "edge_case_illness": {
        "display_name": "6. Edge Case: Illness",
        "scenario_description": "A user is sick with a mild fever, causing increased insulin resistance and leading to a stubborn, slowly rising high glucose level. They report feeling unwell with a slight fever and body aches since this morning."
    },
    "contradictory_stress_hypo": {
        "display_name": "7. Contradictory: Stress-Induced Hypo",
        "scenario_description": "Despite being in a high-stakes, stressful situation (like giving a presentation), a user's glucose is trending downwards, which is contrary to the typical hyperglycemic stress response."
    },
    "contradictory_symptoms": {
        "display_name": "8. Contradictory: Conflicting Symptoms",
        "scenario_description": "A user's CGM is reading high and stable (e.g., 190 mg/dL), but the user is reporting classic symptoms of hypoglycemia like feeling shaky and sweaty."
    }
}

# Performance optimization: Pre-compute scenario keys list to avoid O(n) conversion on each random call
# Time Complexity: O(1) for random selection vs O(n) for list(dict.keys()) every time
_SCENARIO_KEYS = list(SCENARIO_DETAILS_DB.keys())



# --- Models for API ---
class ScenarioOption(BaseModel):
    id: str
    display_name: str

class ScenarioRequest(BaseModel):
    scenario_id: str  # e.g., "high_carb_hyper", "random", "custom"
    session_id: str
    custom_text: Optional[str] = None




# --- Main Logic Function ---

def get_scenario_details(scenario_id: str, custom_text: Optional[str] = None) -> Dict[str, str]:
    """
    Retrieves the detailed scenario descriptions based on the selected ID.
    
    This function handles three types of scenario requests:
    1. Specific scenario IDs from the predefined database
    2. 'random' - randomly selects from available scenarios  
    3. 'custom' - uses AI to rephrase user input into a medical scenario
    
    Args:
        scenario_id (str): The scenario identifier ('random', 'custom', or predefined ID)
        custom_text (Optional[str]): User text for custom scenarios
        
    Returns:
        Dict[str, str]: Dictionary containing the scenario description
        
    Raises:
        HTTPException: For invalid scenario IDs or missing custom text
        
    Time Complexity: 
        - O(1) for predefined and random scenarios (dictionary lookup)
        - O(1) for custom scenarios (single API call)
    """
    if scenario_id == "random":
        # O(1) random selection using pre-computed keys list
        random_id = random.choice(_SCENARIO_KEYS)
        details = SCENARIO_DETAILS_DB[random_id]
        return {
            "scenarios": details["scenario_description"]
        }

    elif scenario_id == "custom":
        if not custom_text or not custom_text.strip():
            raise HTTPException(status_code=400, detail="Custom text must be provided for 'custom' scenario.")
        # Call AI rephrasing function - O(1) time complexity
        details = rephrase_custom_scenario(custom_text)
        return details

    elif scenario_id in SCENARIO_DETAILS_DB:
        # O(1) dictionary lookup
        details = SCENARIO_DETAILS_DB[scenario_id]
        return {
            "scenarios": details["scenario_description"]
        }
    else:
        raise HTTPException(status_code=404, detail="Scenario ID not found.")
