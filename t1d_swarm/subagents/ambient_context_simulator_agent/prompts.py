from pydantic import BaseModel, Field
from typing import Optional, Dict, Union, List
from datetime import datetime


class ContextEventOutput(BaseModel):
    """
    Pydantic schema for the structured output of the Ambient_Context_Simulator_Agent.
    """
    event_type: str = Field(
        description="The primary type of contextual event (e.g., 'meal', 'exercise', 'stress', 'illness', 'symptoms_user_reported', 'no_recent_significant_event', 'cgm_alert_review', 'other_notes')."
    )
    description_raw: str = Field(
        description="A natural language description of the event, often derived directly from the input scenario."
    )
    parsed_details: Optional[Dict[str, Union[str, int, float, List[str]]]] = Field(
        default_factory=dict, # Ensure it's an empty dict if no details, not None
        description="Optional structured details extracted or inferred from the event description (e.g., {'estimated_carbs_g': 60, 'meal_type': 'lunch'}, {'exercise_type': 'running', 'intensity': 'moderate'}, {'symptoms': ['nausea', 'headache']})."
    )
    timestamp_event: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO 8601 timestamp for when the event occurred or was logged (UTC)."
    )


AMBIENT_CONTEXT_PROMPT = """
You are an AI assistant simulating contextual events for a Type 1 Diabetes management system.
Your input is a scenario description provided in `state['current_context_scenario']`.

Current Scenario: `{{scenario}}`

Based on this scenario, generate a contextual event.
The `event_type` should categorize the scenario (e.g., "meal", "exercise", "stress", "illness", "symptoms_user_reported", "no_recent_significant_event").
The `description_raw` should closely reflect or be the provided scenario.
If the scenario implies specific details (like carb amounts, exercise duration/intensity, specific symptoms), attempt to populate `parsed_details`. If not, `parsed_details` can be an empty dictionary.
The `timestamp_event` should be a current ISO 8601 UTC timestamp.

Your output MUST be a single, valid JSON object conforming to the `ContextEventOutput` Pydantic schema below.
Do not include any other text or explanations outside this JSON object.

```json
{model_output}
```

Example Scenario: "User reports: 'Just ate a large bowl of pasta and a slice of cake.'"
Expected `event_type` for example: "meal"

Avoid giving potential consequences or effect.
"""