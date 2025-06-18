import os
from typing import Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from google.adk.cli.fast_api import get_fast_api_app
from pydantic import BaseModel

# Import the global scenario management functions
from .agent import set_global_scenario, get_global_scenario

# Pydantic model for the scenario data
class ScenarioData(BaseModel):
    scenario_id: str  # e.g., "high_carb_hyper", "random", "custom"
    custom_text: Optional[str] = None

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Example session DB URL (e.g., SQLite)
SESSION_DB_URL = "sqlite:///./sessions.db"
# Example allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = True

# Call the function to get the FastAPI app instance
# Note: Using 'agent_dir' not 'agents_dir' based on the Google ADK documentation
app: FastAPI = get_fast_api_app(
    agent_dir=AGENT_DIR,
    session_db_url=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

@app.post("/set-scenario/")
async def set_scenario_from_frontend(scenario_data: ScenarioData):
    """
    Receives a scenario selection from frontend and stores it globally.
    Example payload: {"scenario_id": "high_carb_hyper", "custom_text": null}
    """
    try:
        # Store the scenario data globally using the agent's global function
        set_global_scenario({
            "scenario_id": scenario_data.scenario_id,
            "custom_text": scenario_data.custom_text
        })
        
        return {
            "message": "Scenario stored successfully",
            "scenario_id": scenario_data.scenario_id,
            "custom_text": scenario_data.custom_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set scenario: {str(e)}")

@app.get("/current-scenario/")
async def get_current_scenario():
    """
    Returns the currently stored scenario for testing/debugging purposes.
    """
    scenario = get_global_scenario()
    if scenario:
        return {"current_scenario": scenario}
    else:
        return {"message": "No scenario currently selected"}

@app.get("/available-scenarios/")
async def get_available_scenarios():
    """
    Returns the list of available scenario options for the frontend dropdown.
    """
    from .tools import SCENARIO_DETAILS_DB
    
    scenarios = []
    for scenario_id, details in SCENARIO_DETAILS_DB.items():
        scenarios.append({
            "id": scenario_id,
            "display_name": details["display_name"],
            "description": details["scenario_description"]
        })
    
    # Add special options
    scenarios.extend([
        {
            "id": "random",
            "display_name": "Random Scenario",
            "description": "Randomly select one of the predefined scenarios"
        },
        {
            "id": "custom",
            "display_name": "Custom Scenario",
            "description": "Provide your own custom scenario text"
        }
    ])
    
    return {"scenarios": scenarios}

# You can add more FastAPI routes or configurations below if needed.

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080))) 