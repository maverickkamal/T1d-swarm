from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json

# --- Pydantic Schema for CGMDataOutput ---
# This is what the Simulated_CGM_Feed_Agent will output.

class CGMDataOutput(BaseModel):
    """
    Pydantic schema for the structured output of the Simulated_CGM_Feed_Agent.
    """
    glucose_value: Optional[int] = Field(
        default=None,
        description="The blood glucose reading in mg/dL. Can be null if there's a sensor error or missing data."
    )
    trend_arrow: str = Field(
        description="An arrow showing how quickly the patients glucose is rising,"
                    "return 'DoubleUp' to indicate patients glucose is rising rapidly,"
                    "return 'SingleUp' to indicate patients glucose is rising,"
                    "return 'FortyFiveUp' to indicate patients glucose is rising slowly,"
                    "return 'Flat' to indicate patients glucose is constant,"
                    "return 'FortyFiveDown' to indicate patients glucose is falling slowly,"
                    "return 'SingleDown' to indicate patients glucose is falling,"
                    "return 'DoubleDown' to indicate patients glucose is falling rapidly,"
                    "return 'NOT_COMPUTABLE' to indicate the CGM has no reading of patients glucose,"
                    "return 'Error' to indicate issues with CGM reading",)
    unit: str = Field(
        default="mg/dL",
        description="Unit for the glucose value, typically 'mg/dL'."
    )
    data_quality_issues: Optional[str] = Field(
        default=None,
        description="Describes any sensor data quality issues (e.g., 'missing_data', 'erratic_readings', 'sensor_error_X01'). Omit or null if no issues."
    )
    timestamp_simulated: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO 8601 timestamp for when this CGM reading was simulated (UTC)."
    )

# --- Prompt for SimulatedCGMFeedAgent ---
# This prompt will be used by an LlmAgent.
# It expects 'current_cgm_scenario' to be in session.state, populated by a before_agent_callback.

SIMULATED_CGM_FEED_PROMPT = """
You are an AI assistant simulating Continuous Glucose Monitor (CGM) data for a Type 1 Diabetes management system.
Your input is a scenario description provided in `state['current_cgm_scenario']`.

Current Scenario: `{{scenario}}`

Based on this scenario, generate a single, realistic CGM data point.
Consider how the scenario (e.g., post-meal, exercise, sensor issue) would affect glucose value and trend.
If the scenario implies a sensor malfunction or data gap, reflect that in `glucose_value` (e.g., set to null), `trend_arrow` (e.g., "NOT_COMPUTABLE"), and `data_quality_issues`.
The `timestamp_simulated` should be a current ISO 8601 UTC timestamp.

Your output MUST be a single, valid JSON object conforming to the `CGMDataOutput` Pydantic schema below.
Do not include any other text or explanations outside this JSON object.

```json
{model_output}
```

Example Scenario: "User has just eaten a high-carb meal and is experiencing a rapid glucose rise."
Expected `glucose_value` for example: Likely > 150 (will vary)
Expected `trend_arrow` for example: "SingleUp" or "DoubleUp"

Example Scenario: "CGM sensor is failing, producing no readings."
Expected `glucose_value` for example: null
Expected `trend_arrow` for example: "NOT_COMPUTABLE"
Expected `data_quality_issues` for example: "Sensor failure, no readings available."

Generate the JSON output now.
"""
