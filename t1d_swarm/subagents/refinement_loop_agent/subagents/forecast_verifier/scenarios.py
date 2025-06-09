import uuid
from datetime import datetime, timedelta

# Helper to generate ISO 8601 timestamps for consistency
def get_iso_timestamp(minutes_ago=0):
    return (datetime.utcnow() - timedelta(minutes=minutes_ago)).isoformat() + "Z"

# Test Case 9: Conflicting Information - User feels hypo, CGM shows high (potential compression low or sensor issue)
mock_cgm_data_conflicting_high = {
    "glucose_value": 190,
    "trend_arrow": "Flat", # Or even "SingleUp" to make it more conflicting
    "unit": "mg/dL",
    "data_quality_issues": None, # No obvious issue reported by CGM itself
    "timestamp_simulated": get_iso_timestamp(minutes_ago=2)
}
mock_context_event_conflicting_high = {
    "event_type": "symptoms_user_reported",
    "description_raw": "User reports feeling shaky, sweaty, and very hungry - classic hypo symptoms.",
    "parsed_details": {"symptoms": ["shaky", "sweaty", "very_hungry"]},
    "timestamp_event": get_iso_timestamp(minutes_ago=5)
}

# Test Case 10: Old Contextual Data - Meal was many hours ago
mock_cgm_data_old_context = {
    "glucose_value": 105,
    "trend_arrow": "Flat",
    "unit": "mg/dL",
    "data_quality_issues": None,
    "timestamp_simulated": get_iso_timestamp(minutes_ago=1)
}
mock_context_event_old_context = {
    "event_type": "meal",
    "description_raw": "Ate a balanced lunch (chicken salad sandwich).",
    "parsed_details": {"estimated_carbs_g": 40, "meal_type": "lunch"},
    "timestamp_event": get_iso_timestamp(minutes_ago=240) # 4 hours ago
}

# Test Case 11: Multiple Recent Context Events - Meal followed by light exercise
mock_cgm_data_multi_event = {
    "glucose_value": 145,
    "trend_arrow": "FortyFiveDown", # Starting to come down
    "unit": "mg/dL",
    "data_quality_issues": None,
    "timestamp_simulated": get_iso_timestamp(minutes_ago=5)
}
# This would ideally be a list of events, but our current agent takes one.
# For this test, we'll make the context event a bit more complex in description_raw
# or assume the *most recent relevant* event is passed.
# Let's simulate the most recent being exercise after a meal.
mock_context_event_multi_event_exercise = {
    "event_type": "exercise",
    "description_raw": "Went for a 20-minute gentle walk after lunch.",
    "parsed_details": {"exercise_type": "walking", "exercise_duration_min": 20, "intensity": "light"},
    "timestamp_event": get_iso_timestamp(minutes_ago=30) # Exercise was 30 mins ago
    # Implicitly, a meal happened before this, say ~90 mins ago, which might be in a prior event not given to this agent turn.
    # The agent should primarily focus on the given context_event.
}
# To truly test multiple events, the agent/system would need to handle a list of recent context events.
# For now, we test how it handles the exercise with a slightly higher starting glucose.

# Test Case 12: No Obvious Context, Unexpected Rise
mock_cgm_data_unexplained_rise = {
    "glucose_value": 160,
    "trend_arrow": "SingleUp",
    "unit": "mg/dL",
    "data_quality_issues": None,
    "timestamp_simulated": get_iso_timestamp(minutes_ago=3)
}
mock_context_event_unexplained_rise = {
    "event_type": "no_recent_significant_event", # Or "other_notes"
    "description_raw": "No meal, exercise, or unusual stress reported in the last 3 hours.",
    "parsed_details": {},
    "timestamp_event": get_iso_timestamp(minutes_ago=10) # Just a timestamp for a "check-in"
}

# Test Case 13: Very High Glucose with Ketones Mentioned (if your system could capture this)
# For now, we'll just signal very high glucose. The LLM might infer ketone risk.
mock_cgm_data_very_high = {
    "glucose_value": 350,
    "trend_arrow": "DoubleUp",
    "unit": "mg/dL",
    "data_quality_issues": None,
    "timestamp_simulated": get_iso_timestamp(minutes_ago=5)
}
mock_context_event_very_high = {
    "event_type": "cgm_alert_review", # Simulating this is a review of an alert
    "description_raw": "CGM showing persistent very high glucose. User reports feeling unwell.",
    # "parsed_details": {"ketones_trace": True}, # Future capability
    "timestamp_event": get_iso_timestamp(minutes_ago=15)
}


mock_forecast_conflict = {
  "forecast_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "timestamp_forecast_generated": "2025-05-25T17:05:51.128707Z",
  "short_term_outlook": {
    "overall_risk_level": "very_high_urgent",
    "primary_concern": "hypoglycemia",
    "time_horizon_hours": 0.5,
    "narrative_summary": "Critical Alert: User reports classic hypoglycemia symptoms (shaky, sweaty, very hungry) which strongly conflict with the current CGM reading of 190 mg/dL (Flat). This discrepancy requires immediate blood glucose verification via fingerstick to determine the true glucose level and take appropriate action. Prioritize symptom report; CGM sensor may be inaccurate or significantly lagging.",
    "confidence_score": 0.9
  },
  "contributing_factors": [
    {
      "factor_type": "user_reported_symptoms",
      "detail": "User reported symptoms: shaky, sweaty, very hungry, approximately 3 minutes before the CGM reading. These are classic signs of hypoglycemia.",
      "impact_on_forecast": "Strongly suggests potential current or recent hypoglycemia, creating a critical conflict with the current CGM data. User symptoms are prioritized for safety."
    },
    {
      "factor_type": "cgm_reading",
      "detail": "CGM indicates 190 mg/dL with a Flat trend.",
      "impact_on_forecast": "Suggests hyperglycemia if accurate. However, this directly contradicts the user's reported symptoms, raising significant concerns about sensor accuracy, lag, or a very recent rapid rise from a low."
    },
    {
      "factor_type": "data_discrepancy",
      "detail": "Significant and acute conflict between subjective user-reported symptoms of hypoglycemia and objective CGM data indicating hyperglycemia.",
      "impact_on_forecast": "Elevates risk to 'very_high_urgent' due to the need for immediate clarification. Incorrect action or inaction based on faulty data could be harmful. Mandates BGM verification."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Verify current blood glucose level immediately using a fingerstick blood glucose meter.",
    "If fingerstick confirms low blood glucose, treat hypoglycemia according to your personal management plan.",
    "If fingerstick confirms high blood glucose (matching CGM), consider potential reasons for the reported symptoms (e.g., rapid blood glucose changes, other health conditions) and consult healthcare provider if symptoms persist or are unexplained.",
    "Evaluate CGM sensor performance and consider replacement if it's confirmed to be inaccurate."
  ],
  "actionable_micro_insight_candidate": "URGENT: You're reporting hypo symptoms, but your CGM shows 190 (Flat). Please check your blood sugar with a fingerstick NOW to confirm and act accordingly!"
}

mock_forecast_old = {
  "forecast_id": "f7b3c1e0-a2d8-4f9e-8b1a-0c9d8e7f6a5b",
  "timestamp_forecast_generated": "2025-05-25T17:07:51.128722Z",
  "short_term_outlook": {
    "overall_risk_level": "stable",
    "primary_concern": "no_immediate_concern",
    "time_horizon_hours": 2.0,
    "narrative_summary": "Glucose is currently stable at 105 mg/dL with a flat trend. The lunch consumed approximately 4 hours ago (40g carbs) appears to be well-managed, with no immediate indications of significant glycemic change.",
    "confidence_score": 0.9
  },
  "contributing_factors": [
    {
      "factor_type": "cgm_reading",
      "detail": "Current glucose 105 mg/dL, trend 'Flat'.",
      "impact_on_forecast": "Indicates current glycemic stability, suggesting that recent carbohydrate intake and insulin are balanced."
    },
    {
      "factor_type": "meal_event_timing",
      "detail": "A meal with an estimated 40g of carbohydrates was consumed approximately 4 hours prior to the current CGM reading.",
      "impact_on_forecast": "The majority of the glycemic impact from this meal is likely to have already occurred. The current stable glucose suggests effective management of this past meal."
    },
    {
      "factor_type": "cgm_data_quality",
      "detail": "No data quality issues reported with the current CGM reading.",
      "impact_on_forecast": "Increases confidence in the reliability of the current glucose value and trend for forecasting."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Continue with your routine glucose monitoring.",
    "Be aware of any planned activities or additional food intake in the next few hours, as these could influence your glucose levels."
  ],
  "actionable_micro_insight_candidate": "Your glucose is 105 mg/dL and stable. It looks like your lunch from about 4 hours ago was well-handled!"
}

mock_forecast_exercise = {
  "forecast_id": "fct-20250525-170251-cgm145fd-exer",
  "timestamp_forecast_generated": "2025-05-25T17:02:51.128734Z",
  "short_term_outlook": {
    "overall_risk_level": "elevated",
    "primary_concern": "hypoglycemia",
    "time_horizon_hours": 1.5,
    "narrative_summary": "Current glucose is 145 mg/dL and trending downwards ('FortyFiveDown'). Recent light exercise (a 20-minute walk that ended approximately 5 minutes ago) may cause a further drop in glucose over the next 1-2 hours, increasing the potential for hypoglycemia.",
    "confidence_score": 0.75
  },
  "contributing_factors": [
    {
      "factor_type": "cgm_trend",
      "detail": "Current glucose is 145 mg/dL with a 'FortyFiveDown' trend arrow.",
      "impact_on_forecast": "Indicates that glucose levels are actively decreasing, suggesting a potential for further reduction."
    },
    {
      "factor_type": "recent_exercise",
      "detail": "A 20-minute light intensity walk was completed approximately 5 minutes prior to the current CGM reading.",
      "impact_on_forecast": "Exercise, even light, typically lowers blood glucose. This effect can continue post-exercise and is likely contributing to the observed downward trend and may lead to further decreases."
    },
    {
      "factor_type": "post_prandial_exercise",
      "detail": "The exercise was described as 'after lunch', implying there may be active insulin (IOB) from a recent meal.",
      "impact_on_forecast": "If IOB is present, it can work synergistically with exercise-induced insulin sensitivity to lower glucose more significantly, increasing the risk of hypoglycemia."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Monitor glucose levels closely, especially over the next 1-2 hours.",
    "Be aware of the potential for a further drop in glucose due to the recent exercise.",
    "Consider having fast-acting carbohydrates readily available in case glucose levels fall too low."
  ],
  "actionable_micro_insight_candidate": "Heads up! Your glucose is 145 mg/dL and dropping after your recent walk. Keep an eye on it, as it might continue to decrease over the next hour or two."
}

mock_forecast_no_context = {
  "forecast_id": "f4e8b9c0-a1b2-4c3d-8e7f-6a5b4c3d2e1f",
  "timestamp_forecast_generated": "2025-05-25T17:05:00.000000Z",
  "short_term_outlook": {
    "overall_risk_level": "elevated",
    "primary_concern": "hyperglycemia",
    "time_horizon_hours": 1.5,
    "narrative_summary": "Glucose is at 160 mg/dL and rising ('SingleUp') with no recent significant events like meals or exercise reported in the last 3 hours. This unexplained rise warrants attention as it may lead to further hyperglycemia.",
    "confidence_score": 0.8
  },
  "contributing_factors": [
    {
      "factor_type": "cgm_level",
      "detail": "Current glucose 160 mg/dL.",
      "impact_on_forecast": "Indicates current elevated glucose, above target range for many individuals."
    },
    {
      "factor_type": "cgm_trend",
      "detail": "Trend arrow 'SingleUp'.",
      "impact_on_forecast": "Suggests glucose is actively increasing, potentially leading to higher levels."
    },
    {
      "factor_type": "contextual_event",
      "detail": "No meal, exercise, or unusual stress reported in the last 3 hours.",
      "impact_on_forecast": "The rise is unexplained by recent common events, increasing concern for other underlying factors (e.g., insufficient basal insulin, delayed meal effect, illness onset)."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Monitor glucose readings frequently over the next 1-2 hours to observe the trend.",
    "Consider potential unlogged factors (e.g., delayed meal absorption from a previous meal, mild stress, start of illness) that might be influencing glucose levels.",
    "Be mindful of symptoms of hyperglycemia."
  ],
  "actionable_micro_insight_candidate": "Heads up: Glucose is 160 mg/dL and rising. With no recent meal or activity noted, it's a good idea to keep an eye on your levels."
}

mock_forecast_unwell = {
  "forecast_id": "c2b8e1a0-5d9f-4e8a-b7c1-9f0d2e3a1b4f",
  "timestamp_forecast_generated": "2025-05-25T17:03:00.000000Z",
  "short_term_outlook": {
    "overall_risk_level": "very_high_urgent",
    "primary_concern": "severe_hyperglycemia",
    "time_horizon_hours": 1.0,
    "narrative_summary": "Glucose is critically high (350 mg/dL) and rising very rapidly (DoubleUp). User reports feeling unwell. This combination indicates a serious hyperglycemic event requiring immediate attention according to your personal diabetes management plan. Consider checking for ketones.",
    "confidence_score": 0.95
  },
  "contributing_factors": [
    {
      "factor_type": "cgm_reading",
      "detail": "Current glucose 350 mg/dL with DoubleUp trend.",
      "impact_on_forecast": "Indicates severe and rapidly worsening hyperglycemia."
    },
    {
      "factor_type": "user_report",
      "detail": "User reports feeling unwell.",
      "impact_on_forecast": "Corroborates the severity indicated by CGM and suggests significant physiological impact."
    },
    {
      "factor_type": "recent_cgm_alert_review",
      "detail": "Contextual event from 10 minutes prior ('2025-05-25T16:51:51Z') indicated 'CGM showing persistent very high glucose. User reports feeling unwell.'",
      "impact_on_forecast": "Reinforces the ongoing nature and user awareness of the severe hyperglycemia."
    },
    {
      "factor_type": "cgm_data_quality",
      "detail": "No data quality issues reported by CGM system for the current reading.",
      "impact_on_forecast": "Increases confidence in the current CGM reading's accuracy."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Urgently follow your personalized management plan for severe hyperglycemia.",
    "Consider checking for ketones due to the very high glucose level and feeling unwell.",
    "Closely monitor glucose levels to assess the effectiveness of any actions taken.",
    "Be prepared to follow your established sick day protocols, which may include guidance on when to seek further medical attention if glucose levels do not improve or ketones are significant."
  ],
  "actionable_micro_insight_candidate": "URGENT: Glucose 350 mg/dL & rising very fast (DoubleUp)! You also reported feeling unwell. This is serious. Act now on severe high glucose per your plan & consider checking ketones."
}
