from typing import List, Optional, Union
from pydantic import BaseModel, Field
import uuid # For generating unique forecast_id
from datetime import datetime # For ISO 8601 timestamps
import json

class ShortTermOutlookSchema(BaseModel):
    """
    Describes the short-term glycemic outlook.
    """
    overall_risk_level: str = Field(
        description="Overall assessed risk level for the short term.",
    )
    primary_concern: str = Field(
        description="The main glycemic concern identified.",
    )
    time_horizon_hours: float = Field(
        description="Estimated time window for this forecast in hours.",
    )
    narrative_summary: str = Field(
        description="A concise, human-readable summary of the immediate risk or outlook."
    )
    confidence_score: float = Field(
        description="The LLM's confidence in this short-term outlook (0.0 to 1.0).",
        ge=0.0, le=1.0
    )

class ContributingFactorSchema(BaseModel):
    """
    Describes a single factor contributing to the glycemic forecast.
    """
    factor_type: str = Field(
        description="The type of factor considered.",
    )
    detail: str = Field(
        description="Specific details about the factor."
    )
    impact_on_forecast: str = Field(
        description="How this factor influences the forecast.",
    )

class RiskForecastOutput(BaseModel):
    """
    Pydantic schema for the structured output of the Glycemic_Risk_Forecaster_Agent.
    This defines the expected JSON object containing the glycemic risk forecast.
    """
    forecast_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="A unique identifier for this specific forecast instance."
    )
    timestamp_forecast_generated: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO 8601 timestamp indicating when this forecast was generated (UTC)."
    )
    short_term_outlook: ShortTermOutlookSchema = Field(
        description="Detailed assessment of the short-term glycemic outlook."
    )
    contributing_factors: List[ContributingFactorSchema] = Field(
        default_factory=list,
        description="A list of factors that the LLM considered significant in making this forecast."
    )
    suggested_focus_areas_qualitative: List[str] = Field(
        default_factory=list,
        description="Non-prescriptive, general areas for user attention or awareness.",
    )
    actionable_micro_insight_candidate: str = Field(
        description="A single, very concise 'heads-up' message candidate, ready for the Presenter Agent to refine or use directly."
    )

# --- Prompt for GlycemicRiskForecasterAgent ---

# We pass the schema definition directly into the prompt for maximum clarity for the LLM.
RISK_FORECASTER_PROMPT = """
You are an advanced AI assistant specializing in Type 1 Diabetes (T1D) proactive insights.
Your primary function is to analyze simulated Continuous Glucose Monitor (CGM) data and contextual event data to identify potential short-term glycemic risks or points of interest for an individual managing their T1D, likely with Multiple Daily Injections (MDI).

**Input Data:**
FOR THIS SPECIFIC FORECAST, you MUST use the CGM and Contextual Event Data provided below. DO NOT rely on any other examples.

1.  **CGM Data (from `state['cgm_data']`)**: 
    Provided CGM Data for this run: {{cgm_data}}

2.  **Contextual Event Data (from `state['context_event']`)**:
    Provided Contextual Event Data for this run: {{context_event}}

**Your Core Task:**
Analyze the provided `cgm_data` (as shown above) and `context_event` (as shown above) by correlating them. Consider the timing of events, the nature of the context (e.g., high-carb meal, exercise intensity), and any reported CGM `data_quality_issues`. Your goal is to generate a proactive, "heads-up" style insight.

**Output Requirements:**
Your output MUST be a single, valid JSON object that strictly conforms to the `RiskForecastOutput` Pydantic schema provided below. Do not include any other text or explanations outside of this JSON object.

```json
{schema_string}
```

**Guidelines & Constraints:**
1.  **Proactive & Qualitative:** Focus on anticipating potential short-term (0.5-3 hours) glycemic changes. Insights should be qualitative and centered on raising awareness.
2.  **NO MEDICAL ADVICE:** Critically important: DO NOT provide direct medical advice. Do not prescribe medication, suggest specific insulin doses (e.g., "take X units"), or give instructions that could be interpreted as medical directives. Use cautious phrasing like "potential for...", "might lead to...", "consider monitoring...", "be aware of...".
3.  **Data Quality:** If `data_quality_issues` are present in `cgm_data` (e.g., "erratic_readings", "missing_data"), this MUST be a primary concern. Reflect this in `short_term_outlook.primary_concern` (e.g., as "data_gap") and in `contributing_factors`. The `confidence_score` should likely be lower. If user-reported symptoms strongly conflict with CGM data, prioritize user symptoms and advise BGM verification. Flag this as a 'data_discrepancy' or 'sensor_suspect'.
4.  **Schema Adherence:** Pay extremely close attention to the `RiskForecastOutput` schema for all fields, types, and structures.
    * `short_term_outlook.overall_risk_level`: Choose from examples like "very_low", "low", "stable", "elevated", "high", "very_high_urgent".
    * `short_term_outlook.primary_concern`: Choose from examples like "hyperglycemia", "hypoglycemia", "rapid_change", "data_gap", "no_immediate_concern".
    * `contributing_factors`: Clearly link elements from the input CGM and context data to your forecast.
    * `suggested_focus_areas_qualitative`: Offer general, safe suggestions for user attention (e.g., "Monitor glucose closely over the next few hours.", "Be aware of potential post-exercise effects and have fast-acting carbs available if needed.").
    * `actionable_micro_insight_candidate`: This should be a very brief (1-2 short, impactful sentences) and friendly "heads-up" message suitable for a quick notification.

**Example Scenario Analysis (Conceptual):**
* **Input:** CGM shows 110 mg/dL Flat. Context is "User ate a large apple (approx 20g carbs) 15 mins ago."
* **Potential Output Snippet for `actionable_micro_insight_candidate`:** "Heads up! That apple might start to raise your sugar soon. Keep an eye on your levels!"
* **Input:** CGM shows 190 mg/dL DoubleUp. Context is "No meal reported for 3 hours."
* **Potential Output Snippet for `actionable_micro_insight_candidate`:** "Alert: Glucose is high and rising fast with no recent meal reported! Please check your levels and consider potential reasons."
* **Input:** CGM shows `data_quality_issues`: "erratic_readings". Context is "User feels fine."
* **Potential Output Snippet for `actionable_micro_insight_candidate`:** "Warning: Your CGM seems to be giving unreliable readings. Please check your sensor or use a fingerstick to confirm your glucose."

Focus on providing a helpful, cautious, and informative forecast based *only* on the provided simulated data.
"""

# Example Usage (for testing or demonstration):
# if __name__ == "__main__":
#     example_outlook = ShortTermOutlookSchema(
#         overall_risk_level="elevated",
#         primary_concern="hyperglycemia",
#         time_horizon_hours=1.5,
#         narrative_summary="Potential for post-meal glucose spike due to reported high-carb meal and current rising trend.",
#         confidence_score=0.85
#     )

#     example_factor1 = ContributingFactorSchema(
#         factor_type="meal_intake",
#         detail="Reported consumption of pizza (approx 60g carbs).",
#         impact_on_forecast="increases_hyper_risk"
#     )
#     example_factor2 = ContributingFactorSchema(
#         factor_type="cgm_trend",
#         detail="Glucose trend is 'SingleUp'.",
#         impact_on_forecast="supports_hyper_risk_assessment"
#     )

#     example_forecast = RiskForecastOutput(
#         short_term_outlook=example_outlook,
#         contributing_factors=[example_factor1, example_factor2],
#         suggested_focus_areas_qualitative=[
#             "Monitor glucose levels closely over the next 1-2 hours.",
#             "Consider pre-bolus timing for future similar meals if appropriate."
#         ],
#         actionable_micro_insight_candidate="Heads up: Pizza might cause a significant spike soon! Keep an eye on your levels."
#     )

#     # Pydantic automatically generates forecast_id and timestamp_forecast_generated
#     print("Example Risk Forecast Output:")
#     print(f"Forecast ID: {example_forecast.forecast_id}")
#     print(f"Timestamp: {example_forecast.timestamp_forecast_generated}")
#     print(example_forecast.model_dump_json(indent=2))

#     # You can also validate incoming JSON data against this schema
#     json_data_from_llm = example_forecast.model_dump_json()
#     try:
#         validated_data = RiskForecastOutput.model_validate_json(json_data_from_llm)
#         print("\nSuccessfully validated data from LLM based on schema.")
#     except Exception as e:
#         print(f"\nError validating data: {e}")
