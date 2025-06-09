from pydantic import BaseModel, Field
from typing import Optional, Dict, Union, List
from datetime import datetime

class EventDetails(BaseModel):
    estimated_carbs_g: Optional[int] = Field(None, description="Estimated carbohydrates consumed in grams.")
    meal_type: Optional[str] = Field(None, description="Type of meal (e.g., 'snack', 'lunch', 'dinner').")
    exercise_type: Optional[str] = Field(None, description="Type of exercise (e.g., 'running', 'walking', 'swimming').")
    exercise_duration_min: Optional[int] = Field(None, description="Duration of exercise in minutes.")
    intensity: Optional[str] = Field(None, description="Intensity of activity (e.g., 'low', 'moderate', 'high').")
    symptoms: Optional[List[str]] = Field(None, description="List of symptoms experienced (e.g., ['shaky', 'sweaty']).")
    notes: Optional[str] = Field(None, description="Any additional relevant notes about the event.")
    # Add any other potential keys from your examples here!
    # For example, if you expect 'stress_level':
    stress_level: Optional[str] = Field(None, description="Level of stress (e.g., 'low', 'medium', 'high').")
    # If 'data_quality_issues' can be a specific type or just True/False
    data_quality_issues: Optional[bool] = Field(None, description="Indicates if there are issues with the CGM data quality.")




class ModelInput(BaseModel):
    glucose_value: int = Field(0, alias='glucose_value', description='The glucose reading of a patient by the CGM')
    trend_arrow: str = Field("...", alias='trend_arrow',
                             description="An arrow showing how quickly the patients glucose is rising,"
                                         "return 'DoubleUp' to indicate patients glucose is rising rapidly,"
                                         "return 'SingleUp' to indicate patients glucose is rising,"
                                         "return 'FortyFiveUp' to indicate patients glucose is rising slowly,"
                                         "return 'Flat' to indicate patients glucose is constant,"
                                         "return 'FortyFiveDown' to indicate patients glucose is falling slowly,"
                                         "return 'SingleDown' to indicate patients glucose is falling,"
                                         "return 'DoubleDown' to indicate patients glucose is falling rapidly,"
                                         "return 'NOT_COMPUTABLE' to indicate the CGM has no reading of patients glucose,"
                                         "return 'Error' to indicate issues with CGM reading")
    unit: str = Field("mg/dL", alias='unit', description='The unit of the glucose reading')
    data_quality_issues: str = Field("None", alias='problems',
                                     description="Indicates whether the cgm is experiencing issues regarding reading data")
    timestamp: str = Field(..., alias='timestamp',
                                description='The date and time the glucose reading was taken')


class ModelOutput(BaseModel):
    event_type : str = Field("...", alias='event_type', description='The event type of what the person might be doing that correlates with the glucose reading')
    description: str = Field("...", alias='description_raw', description='The raw description of the event')
    details: EventDetails = Field(..., alias='parsed_details', description='A JSON object detailing the most important parts of an event, this is used to generate insights as to how to treat the patients glucose levels',)
    timestamp: datetime = Field(datetime.utcnow(), alias='timestamp_event', description='The time the event occurred')

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