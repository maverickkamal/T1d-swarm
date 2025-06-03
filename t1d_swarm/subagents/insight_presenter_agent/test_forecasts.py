# File: test_forecasts.py

from datetime import datetime, timedelta

def get_iso_timestamp(minutes_ago: int = 0) -> str:
    return (datetime.utcnow() - timedelta(minutes=minutes_ago)).isoformat() + "Z"


# ---------------------------
# 1) Stable Scenario
# ---------------------------
mock_forecast_stable = {
    "timestamp": get_iso_timestamp(5),    # e.g. “2025-06-02T10:55:00Z”
    "predicted_glucose": 110,
    "hypo_risk": 0.05,
    "hyper_risk": 0.10,
    "short_term_outlook": {
        "trend": "flat",
        "next_hour_risk": "low"
    }
}

# ---------------------------
# 2) Potential Hyperglycemia
# ---------------------------
mock_forecast_hyper = {
    "timestamp": get_iso_timestamp(2),
    "predicted_glucose": 185,
    "hypo_risk": 0.02,
    "hyper_risk": 0.30,
    "short_term_outlook": {
        "trend": "rising",
        "next_hour_risk": "high"
    }
}

# ---------------------------
# 3) Potential Hypoglycemia
# ---------------------------
mock_forecast_hypo = {
    "timestamp": get_iso_timestamp(3),
    "predicted_glucose": 80,
    "hypo_risk": 0.40,
    "hyper_risk": 0.05,
    "short_term_outlook": {
        "trend": "falling",
        "next_hour_risk": "high"
    }
}

# ---------------------------
# 4) Erratic Readings / Data Quality Issue
# ---------------------------
mock_forecast_erratic = {
    "timestamp": get_iso_timestamp(1),
    "predicted_glucose": 150,
    "hypo_risk": 0.10,
    "hyper_risk": 0.15,
    "short_term_outlook": {
        "trend": "uncertain",
        "next_hour_risk": "unknown"
    },
    "data_quality_issues": "Erratic CGM readings flagged"
}

# ---------------------------
# 5) Missing Data
# ---------------------------
mock_forecast_missing = {
    "timestamp": get_iso_timestamp(1),
    "predicted_glucose": None,
    "hypo_risk": None,
    "hyper_risk": None,
    "short_term_outlook": {
        "trend": "not_computable",
        "next_hour_risk": "unknown"
    },
    "data_quality_issues": "Sensor signal lost"
}

# You can continue adding as many mock forecasts as you need…
# e.g. mock_forecast_stress, mock_forecast_illness, mock_forecast_complex, etc.
