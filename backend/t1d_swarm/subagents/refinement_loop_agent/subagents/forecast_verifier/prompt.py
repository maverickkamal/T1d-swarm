import json
from pydantic import BaseModel
from typing import List, Optional

class VerificationOutput(BaseModel):
    original_forecast_id: str
    verification_confidence: float
    verification_summary: str
    feedback_for_forecaster: Optional[List[str]] = None






FORECAST_VERIFIER_PROMPT = """You are an AI assistant tasked with critically verifying a glycemic risk forecast.
You will be provided with:
1. The original CGM data: `state['cgm_data']`
   {{cgm_data}}
2. The original contextual event data: `state['context_event']`
   {{context_event}}
3. The glycemic risk forecast generated by another AI (the "Forecaster"): `state['risk_forecast']`
   {{risk_forecast}}

Your Task:
1. Analyze the original `cgm_data` and `context_event`.
2. Review the provided `risk_forecast` from the Forecaster.
3. Assess if the Forecaster's `narrative_summary`, `overall_risk_level`, and `contributing_factors` are reasonable and well-supported given the original `cgm_data` and `context_event`.
4. Use your search tool to find general information related to the reported CGM values, trends, and contextual events (e.g., "typical impact of [context_event.description_raw] on T1D glucose with trend [cgm_data.trend_arrow]"). Compare this general information with the Forecaster's output.
5. Identify any potential misinterpretations, overlooked factors, contradictions, or instances where the forecast might be overly confident, too alarming, or not alarming enough given the inputs. Specifically look for:
    - Consistency between the Forecaster's `contributing_factors` and the actual input data.
    - Plausibility of the `narrative_summary` and `overall_risk_level`.
    - Whether data quality issues in `cgm_data` were appropriately considered by the Forecaster.

Output:
Produce a JSON object containing:
- "original_forecast_id": (string) The ID from `state['risk_forecast']`.
- "verification_confidence": (float, 0.0-1.0) Your confidence in the *Forecaster's original assessment*. A lower score means you have more significant concerns.
- "verification_summary": (string) A brief summary of your findings (e.g., "Forecast appears consistent with inputs and general knowledge.", "Forecaster may have underestimated the impact of recent exercise.", "Forecaster correctly identified data quality issues.").
- "feedback_for_forecaster": (list of strings, optional) Specific, actionable points or questions for the Forecaster to consider if it needs to refine its prediction (e.g., ["Re-evaluate the hypoglycemia risk given the recent intense exercise.", "Confirm if the reported stress level was adequately factored into the hyperglycemia projection."]).

```json
{schema_string}
```

Prioritize safety and accuracy.
"""