mock_forecast_stable = {
  "forecast_id": "f1a7d3b8-e2c9-4f8a-b7e6-0c9d1f2a3b4c",
  "timestamp_forecast_generated": "2025-05-25T00:02:15.000000Z",
  "short_term_outlook": {
    "overall_risk_level": "elevated",
    "primary_concern": "hyperglycemia",
    "time_horizon_hours": 2.0,
    "narrative_summary": "Current glucose is 110 mg/dL and stable ('Flat' trend). However, due to a recent snack (estimated 20g carbohydrates consumed approximately 25 minutes ago), there is an elevated potential for glucose levels to rise in the next 1-2 hours.",
    "confidence_score": 0.75
  },
  "contributing_factors": [
    {
      "factor_type": "recent_meal_intake",
      "detail": "User consumed a snack (small apple and almonds) with an estimated 20g of carbohydrates approximately 25 minutes prior to the latest CGM reading.",
      "impact_on_forecast": "This carbohydrate intake is expected to cause a gradual increase in blood glucose levels over the next 1-2 hours."
    },
    {
      "factor_type": "current_cgm_state",
      "detail": "Current glucose is 110 mg/dL with a 'Flat' trend. No data quality issues were reported with the CGM reading.",
      "impact_on_forecast": "Indicates a stable baseline at a healthy glucose level prior to the expected impact of the recent meal. The flat trend may change as carbohydrates are absorbed."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Monitor glucose levels over the next 1-2 hours to observe the impact of the recent snack.",
    "Be aware that a rise in glucose is likely due to the recent carbohydrate intake."
  ],
  "actionable_micro_insight_candidate": "Heads up! Your glucose is 110 mg/dL and flat for now. The 20g carb snack from ~25 mins ago will likely cause a rise soon. Keep an eye on your levels!"
}

mock_forecast_hyper = {
  "forecast_id": "fca2d6a8-c5b4-4f3e-9d1a-7b8c0f9e4d52",
  "timestamp_forecast_generated": "2025-05-25T00:01:15.421597Z",
  "short_term_outlook": {
    "overall_risk_level": "high",
    "primary_concern": "hyperglycemia",
    "time_horizon_hours": 2.5,
    "narrative_summary": "Glucose is currently 185 mg/dL and rising, following a large high-carbohydrate meal (85g estimated) consumed approximately 43 minutes ago. A continued significant rise in glucose levels, leading to hyperglycemia, is expected over the next 1-3 hours.",
    "confidence_score": 0.9
  },
  "contributing_factors": [
    {
      "factor_type": "meal_intake",
      "detail": "Consumed a large bowl of pasta with garlic bread (estimated 85g carbohydrates) for lunch approximately 43 minutes prior to the CGM reading.",
      "impact_on_forecast": "This high carbohydrate load is the primary driver for the anticipated rise in blood glucose."
    },
    {
      "factor_type": "current_glucose_level",
      "detail": "Current glucose value is 185 mg/dL.",
      "impact_on_forecast": "Glucose is already elevated, increasing the likelihood and potential severity of hyperglycemia as the meal digests."
    },
    {
      "factor_type": "cgm_trend",
      "detail": "CGM trend arrow is 'SingleUp'.",
      "impact_on_forecast": "Indicates that blood glucose is actively rising and is expected to continue this upward trajectory in the short term."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Monitor glucose levels closely over the next 1-3 hours as the recent meal continues to impact them.",
    "Be aware of the potential for glucose to rise significantly higher.",
    "Ensure access to water, as hyperglycemia can increase thirst."
  ],
  "actionable_micro_insight_candidate": "Heads up! Your glucose is 185 mg/dL and rising after that large pasta meal (85g carbs). Expect it to climb higher in the next couple of hours."
}
mock_forecast_hypo = {
  "forecast_id": "f7b3e1c0-a2d8-4f19-8e7a-6b5c0d1e9f2a",
  "timestamp_forecast_generated": "2025-05-24T23:59:15.421618Z",
  "short_term_outlook": {
    "overall_risk_level": "high",
    "primary_concern": "hypoglycemia",
    "time_horizon_hours": 1.5,
    "narrative_summary": "Glucose is 80 mg/dL and trending downwards ('SingleDown') shortly after a 45-minute moderate intensity run. This combination indicates a high risk of hypoglycemia in the next 1-2 hours.",
    "confidence_score": 0.85
  },
  "contributing_factors": [
    {
      "factor_type": "cgm_reading",
      "detail": "Current glucose 80 mg/dL with 'SingleDown' trend.",
      "impact_on_forecast": "Indicates current low-normal glucose with an active decrease, significantly increasing hypoglycemia risk."
    },
    {
      "factor_type": "exercise_event",
      "detail": "Completed a 45-minute moderate intensity run approximately 12 minutes prior to CGM reading.",
      "impact_on_forecast": "Moderate intensity exercise has a known glucose-lowering effect that can persist post-activity, further elevating the risk of hypoglycemia."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Monitor glucose levels closely over the next 1-2 hours.",
    "Be prepared for potential low blood sugar by having fast-acting carbohydrates readily available.",
    "Consider if any adjustments or preventative snacks are needed post-exercise based on your usual response."
  ],
  "actionable_micro_insight_candidate": "Heads up! Your glucose is 80 mg/dL and heading down after your run. Keep an eye out for lows and have quick carbs handy!"
}

mock_forecast_erractic = {
  "forecast_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "timestamp_forecast_generated": "2025-05-25T00:02:00.000000Z",
  "short_term_outlook": {
    "overall_risk_level": "high",
    "primary_concern": "data_gap",
    "time_horizon_hours": 1.0,
    "narrative_summary": "CGM readings (150 mg/dL, Trend: RATE_OUT_OF_RANGE) appear highly unreliable due to reported 'Erratic readings' and potential sensor issues. This aligns with your recent observation of 'jumpy' CGM readings. Trustworthy glucose data is currently unavailable, posing a risk for informed decision-making.",
    "confidence_score": 0.9
  },
  "contributing_factors": [
    {
      "factor_type": "cgm_data_quality",
      "detail": "CGM data indicates 'Erratic readings, sensor may need calibration or replacement.'",
      "impact_on_forecast": "Significantly reduces reliability of current glucose value and trend, making glycemic assessment uncertain."
    },
    {
      "factor_type": "cgm_trend",
      "detail": "CGM trend arrow is 'RATE_OUT_OF_RANGE'.",
      "impact_on_forecast": "Indicates unstable and unpredictable glucose changes, or sensor malfunction, further supporting data unreliability."
    },
    {
      "factor_type": "user_context",
      "detail": "User reported 'CGM readings have been jumpy' approximately 9 minutes before the current CGM reading.",
      "impact_on_forecast": "Corroborates the CGM's reported data quality issues and reinforces the concern about sensor reliability."
    },
    {
      "factor_type": "current_glucose_value",
      "detail": "CGM glucose_value is 150 mg/dL.",
      "impact_on_forecast": "The specific value is less relevant due to overriding data quality concerns, but noted as the last sensor output."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Verify current blood glucose level using a fingerstick meter due to unreliable CGM readings.",
    "Assess the CGM sensor: check for proper adhesion, consider calibration if available, or sensor replacement if issues persist.",
    "Avoid making treatment decisions based on the current CGM data until its reliability is confirmed."
  ],
  "actionable_micro_insight_candidate": "Heads up! Your CGM is showing erratic readings (150 mg/dL, Rate Out Of Range), and you also noted it's been jumpy. Please check your sensor and confirm your glucose with a fingerstick."
}

mock_forecast_missing = {
  "forecast_id": "fdc112a1-78c9-4ba7-9b70-5a193445a2d8",
  "timestamp_forecast_generated": "2025-05-25T00:01:30.123456Z",
  "short_term_outlook": {
    "overall_risk_level": "high",
    "primary_concern": "data_gap",
    "time_horizon_hours": 1.0,
    "narrative_summary": "CGM sensor signal is lost, and no glucose data has been available for the last 15 minutes. Current glucose levels are unknown, which poses an immediate risk.",
    "confidence_score": 0.95
  },
  "contributing_factors": [
    {
      "factor_type": "cgm_data_quality",
      "detail": "Sensor signal lost. No glucose data available for the last 15 minutes.",
      "impact_on_forecast": "Primary driver of the forecast; inability to assess current glycemic state creates high risk due to unknown glucose levels."
    },
    {
      "factor_type": "user_context_event",
      "detail": "User note: 'CGM app shows data gap.' recorded at 2025-05-24T23:57:15.421669Z.",
      "impact_on_forecast": "Corroborates the CGM data issue, reinforcing the data gap as the primary concern and increasing confidence in this assessment."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Urgently check CGM sensor and transmitter to ensure they are properly connected and functioning.",
    "Consider performing a blood glucose meter (BGM) fingerstick test to ascertain current blood glucose level.",
    "While CGM data is unavailable, be mindful of recent insulin doses, carbohydrate intake, and physical activity to anticipate potential glucose fluctuations."
  ],
  "actionable_micro_insight_candidate": "Heads up! Your CGM isn't sending glucose data. Please check your sensor connection and consider a fingerstick to see your current level."
}

mock_forecast_stress = {
  "forecast_id": "forecast-20250524235800123",
  "timestamp_forecast_generated": "2025-05-24T23:58:00.123456Z",
  "short_term_outlook": {
    "overall_risk_level": "high",
    "primary_concern": "hyperglycemia",
    "time_horizon_hours": 2.0,
    "narrative_summary": "Current glucose is 160 mg/dL and trending upwards ('FortyFiveUp'). Recent high stress (reported approx. 55 minutes ago) is likely contributing, suggesting a potential for further glucose elevation in the next 1-3 hours.",
    "confidence_score": 0.85
  },
  "contributing_factors": [
    {
      "factor_type": "cgm_reading",
      "detail": "Current glucose 160 mg/dL with a 'FortyFiveUp' trend.",
      "impact_on_forecast": "Indicates current glucose is elevated and actively rising, increasing the short-term risk of more significant hyperglycemia."
    },
    {
      "factor_type": "contextual_event_stress",
      "detail": "High intensity stress reported approximately 55 minutes ago.",
      "impact_on_forecast": "High stress is known to elevate glucose levels, likely contributing to the current rise and the potential for continued increase."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Monitor glucose levels closely over the next 1-3 hours.",
    "Be aware that the recent high stress may continue to influence your glucose levels.",
    "If this pattern of stress-induced hyperglycemia is common, consider discussing strategies with your healthcare provider."
  ],
  "actionable_micro_insight_candidate": "Heads up! Glucose is 160 mg/dL and rising. The high stress you felt earlier is likely a factor. Keep a close eye on your levels."
}

mock_forecast_illness = {
  "forecast_id": "e8d3c5a2-7b1f-4e9a-8c5d-6f2a1b3e4d7c",
  "timestamp_forecast_generated": "2025-05-24T23:57:15.421699Z",
  "short_term_outlook": {
    "overall_risk_level": "elevated",
    "primary_concern": "hyperglycemia",
    "time_horizon_hours": 2.0,
    "narrative_summary": "Glucose is currently 175 mg/dL and rising ('SingleUp' trend). The reported illness (fever, body aches) from about 1 hour and 50 minutes ago is likely contributing to increased glucose levels. Expect continued upward pressure on glucose.",
    "confidence_score": 0.85
  },
  "contributing_factors": [
    {
      "factor_type": "cgm_reading",
      "detail": "Current glucose 175 mg/dL with 'SingleUp' trend.",
      "impact_on_forecast": "Indicates current hyperglycemia with an ongoing upward trajectory, suggesting a worsening glycemic state."
    },
    {
      "factor_type": "contextual_event_illness",
      "detail": "User reported illness (symptoms: fever, body_aches) that started approximately 1 hour and 50 minutes prior to the latest CGM reading.",
      "impact_on_forecast": "Illness, particularly with fever, often increases insulin resistance and can lead to significantly elevated blood glucose levels. This is a strong driver for the current and anticipated hyperglycemia."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Monitor glucose levels frequently over the next few hours due to the ongoing illness.",
    "Ensure adequate hydration, which is important during illness and can sometimes affect glucose.",
    "Be aware that illness can alter insulin sensitivity; refer to personal sick day management guidelines if available."
  ],
  "actionable_micro_insight_candidate": "Heads up: Your glucose is 175 mg/dL and rising. The illness you reported earlier is likely affecting your sugar levels. Keep a close watch."
}

mock_forecast_complex = {
  "forecast_id": "fcf1c9f8-f9c0-4b0a-8e1b-7a3d6b8e0f9c",
  "timestamp_forecast_generated": "2025-05-24T23:07:15.421750Z",
  "short_term_outlook": {
    "overall_risk_level": "elevated",
    "primary_concern": "hyperglycemia",
    "time_horizon_hours": 4.0,
    "narrative_summary": "Glucose is currently stable at 130 mg/dL (Flat trend). However, a large, high-carbohydrate (90g), high-fat meal (cheeseburger, fries, milkshake) was just consumed. This is expected to cause a significant and potentially prolonged rise in glucose levels over the next 2-4 hours. The high fat content can delay the initial glucose absorption and extend the duration of the post-meal rise.",
    "confidence_score": 0.9
  },
  "contributing_factors": [
    {
      "factor_type": "meal_intake",
      "detail": "Consumed a large meal (dinner: cheeseburger, fries, milkshake) with an estimated 90g of carbohydrates.",
      "impact_on_forecast": "High carbohydrate load is expected to significantly increase blood glucose levels."
    },
    {
      "factor_type": "meal_composition",
      "detail": "Meal was noted to have 'High fat content'.",
      "impact_on_forecast": "High fat content can delay gastric emptying, leading to a slower initial glucose rise but a more prolonged period of hyperglycemia, potentially peaking later than a lower-fat meal."
    },
    {
      "factor_type": "current_glucose_state",
      "detail": "Current glucose is 130 mg/dL with a 'Flat' trend.",
      "impact_on_forecast": "Provides a stable baseline before the meal's impact, but the impending effect of the large, high-fat meal is the primary driver of the forecast."
    },
    {
      "factor_type": "data_quality",
      "detail": "CGM data quality is good with no reported issues.",
      "impact_on_forecast": "Increases confidence in the current glucose value as a reliable starting point for the forecast."
    }
  ],
  "suggested_focus_areas_qualitative": [
    "Monitor glucose levels closely over the next 2-4 hours, paying attention to the rate and duration of any rise.",
    "Be aware that the high fat content of your recent meal may cause a delayed and more prolonged increase in glucose compared to lower-fat meals.",
    "Reflect on whether your insulin management for this meal adequately addressed both the substantial carbohydrate amount and the potential for a delayed glucose peak due to high fat."
  ],
  "actionable_micro_insight_candidate": "Heads up! That large, high-fat meal (90g carbs) is likely to cause a significant glucose rise. Monitor closely, as the rise could be delayed and last longer due to the fat content."
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
