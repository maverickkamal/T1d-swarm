import uuid
from datetime import datetime, timedelta

# Helper to generate ISO 8601 timestamps for consistency
def get_iso_timestamp(minutes_ago=0):
    return (datetime.utcnow() - timedelta(minutes=minutes_ago)).isoformat() + "Z"

# --- Robust Mock Data Test Cases ---

# Test Case 1: Stable Scenario - Recent light meal, stable glucose
mock_cgm_data_stable = {
    "glucose_value": 110,
    "trend_arrow": "Flat",
    "unit": "mg/dL",
    "data_quality_issues": None,
    "timestamp_simulated": get_iso_timestamp(minutes_ago=5)
}
mock_context_event_stable = {
    "event_type": "meal",
    "description_raw": "Ate a small apple and a handful of almonds.",
    "parsed_details": {"estimated_carbs_g": 20, "meal_type": "snack"},
    "timestamp_event": get_iso_timestamp(minutes_ago=30)
}
# session_id_stable = f"test_session_stable_{uuid.uuid4()}"
# await test_glycemic_agent_with_mock_state(session_id_stable, mock_cgm_data_stable, mock_context_event_stable)

# Test Case 2: Potential Hyperglycemia - Recent high-carb meal, rising glucose
mock_cgm_data_hyper = {
    "glucose_value": 185,
    "trend_arrow": "SingleUp",
    "unit": "mg/dL",
    "data_quality_issues": None,
    "timestamp_simulated": get_iso_timestamp(minutes_ago=2)
}
mock_context_event_hyper = {
    "event_type": "meal",
    "description_raw": "Had a large bowl of pasta with garlic bread for lunch.",
    "parsed_details": {"estimated_carbs_g": 85, "meal_type": "lunch"},
    "timestamp_event": get_iso_timestamp(minutes_ago=45)
}
# session_id_hyper = f"test_session_hyper_{uuid.uuid4()}"
# await test_glycemic_agent_with_mock_state(session_id_hyper, mock_cgm_data_hyper, mock_context_event_hyper)

# Test Case 3: Potential Hypoglycemia - Post-exercise, falling glucose
mock_cgm_data_hypo = {
    "glucose_value": 80,
    "trend_arrow": "SingleDown",
    "unit": "mg/dL",
    "data_quality_issues": None,
    "timestamp_simulated": get_iso_timestamp(minutes_ago=3)
}
mock_context_event_hypo = {
    "event_type": "exercise",
    "description_raw": "Completed a 45-minute moderate intensity run.",
    "parsed_details": {"exercise_type": "running", "exercise_duration_min": 45, "intensity": "moderate"},
    "timestamp_event": get_iso_timestamp(minutes_ago=15)
}
# session_id_hypo = f"test_session_hypo_{uuid.uuid4()}"
# await test_glycemic_agent_with_mock_state(session_id_hypo, mock_cgm_data_hypo, mock_context_event_hypo)

# Test Case 4: CGM Data Quality Issue - Erratic readings
mock_cgm_data_erratic = {
    "glucose_value": 150, # Value might be present but flagged as unreliable
    "trend_arrow": "RATE_OUT_OF_RANGE", # Or some other error indicator
    "unit": "mg/dL",
    "data_quality_issues": "Erratic readings, sensor may need calibration or replacement.",
    "timestamp_simulated": get_iso_timestamp(minutes_ago=1)
}
mock_context_event_erratic = {
    "event_type": "other_notes",
    "description_raw": "User reports feeling fine, but CGM readings have been jumpy.",
    "parsed_details": {},
    "timestamp_event": get_iso_timestamp(minutes_ago=10)
}
# session_id_erratic = f"test_session_erratic_{uuid.uuid4()}"
# await test_glycemic_agent_with_mock_state(session_id_erratic, mock_cgm_data_erratic, mock_context_event_erratic)

# Test Case 5: CGM Data Quality Issue - Missing data
mock_cgm_data_missing = {
    "glucose_value": None, # Glucose value is null
    "trend_arrow": "NOT_COMPUTABLE",
    "unit": "mg/dL",
    "data_quality_issues": "Sensor signal lost. No glucose data available for the last 15 minutes.",
    "timestamp_simulated": get_iso_timestamp(minutes_ago=1) # Timestamp of when the missing data was noted
}
mock_context_event_missing = {
    "event_type": "other_notes",
    "description_raw": "CGM app shows data gap.",
    "parsed_details": {},
    "timestamp_event": get_iso_timestamp(minutes_ago=5)
}
# session_id_missing = f"test_session_missing_{uuid.uuid4()}"
# await test_glycemic_agent_with_mock_state(session_id_missing, mock_cgm_data_missing, mock_context_event_missing)


# Test Case 6: Stress Event Impacting Glucose
mock_cgm_data_stress = {
    "glucose_value": 160,
    "trend_arrow": "FortyFiveUp",
    "unit": "mg/dL",
    "data_quality_issues": None,
    "timestamp_simulated": get_iso_timestamp(minutes_ago=5)
}
mock_context_event_stress = {
    "event_type": "stress",
    "description_raw": "Feeling very stressed due to an important work deadline.",
    "parsed_details": {"intensity": "high"},
    "timestamp_event": get_iso_timestamp(minutes_ago=60)
}
# session_id_stress = f"test_session_stress_{uuid.uuid4()}"
# await test_glycemic_agent_with_mock_state(session_id_stress, mock_cgm_data_stress, mock_context_event_stress)

# Test Case 7: Illness Impacting Glucose
mock_cgm_data_illness = {
    "glucose_value": 175,
    "trend_arrow": "SingleUp",
    "unit": "mg/dL",
    "data_quality_issues": None,
    "timestamp_simulated": get_iso_timestamp(minutes_ago=10)
}
mock_context_event_illness = {
    "event_type": "illness",
    "description_raw": "Woke up with a slight fever and body aches. Took paracetamol.",
    "parsed_details": {"symptoms": ["fever", "body_aches"]},
    "timestamp_event": get_iso_timestamp(minutes_ago=120)
}
# session_id_illness = f"test_session_illness_{uuid.uuid4()}"
# await test_glycemic_agent_with_mock_state(session_id_illness, mock_cgm_data_illness, mock_context_event_illness)

# Test Case 8: Complex Meal - High Fat, High Carb (potential delayed spike)
mock_cgm_data_complex_meal_initial = { # Initial reading post-meal
    "glucose_value": 130,
    "trend_arrow": "Flat",
    "unit": "mg/dL",
    "data_quality_issues": None,
    "timestamp_simulated": get_iso_timestamp(minutes_ago=60) # 1 hour after meal
}
mock_context_event_complex_meal = {
    "event_type": "meal",
    "description_raw": "Ate a large cheeseburger with fries and a milkshake.",
    "parsed_details": {"estimated_carbs_g": 90, "meal_type": "dinner", "notes": "High fat content"},
    "timestamp_event": get_iso_timestamp(minutes_ago=60) # Meal was 1 hour ago
}

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