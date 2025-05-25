import json
import asyncio
import uuid

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

from prompts import RISK_FORECASTER_PROMPT, RiskForecastOutput
from test_scenarios import *

load_dotenv()


# --- Define Constants & YOUR Schema ---
APP_NAME = "glycemic_forecast_agent"
USER_ID = "test_physician_789" # Or a relevant user identifier
MODEL_NAME = "gemini-2.5-pro-preview-05-06"

# --- Configure Llm Agent --- 

SCHEMA_JSON_STRING = json.dumps(RiskForecastOutput.model_json_schema(), indent=2)

instruction_for_agent = RISK_FORECASTER_PROMPT.format(
schema_string=SCHEMA_JSON_STRING
)

glycemic_forecaster_agent = LlmAgent(
    model=MODEL_NAME,
    name="GlycemicRiskForecasterAgent",
    description="Generates glycemic risk forecasts based on CGM and context data.",
    instruction=instruction_for_agent,
    output_schema=RiskForecastOutput,
    output_key="risk_forecast",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)

# --- Set up Session Management and Runner ---
print("--- Setting up Session Service and Runner ---")
session_service = InMemorySessionService()

# We will create/update the session state for each test case within the interaction logic.
# So, we don't need to create multiple session IDs as constants beforehand.
runner = Runner(
    agent=glycemic_forecaster_agent,
    app_name=APP_NAME,
    session_service=session_service
)
print(f"Runner configured for agent: {glycemic_forecaster_agent.name}")

# --- Define Agent Interaction Logic (for testing) ---
async def test_glycemic_agent_with_mock_state(
    session_id_for_test: str, # A unique session ID for each test run
    mock_cgm_data: dict,      # mock CGM data
    mock_context_event: dict  # mock context event data
):
    """
    Sets up session state with mock data, runs the glycemic forecaster,
    and prints the resulting forecast from the state.
    """
    print(f"\n>>> Testing Agent with Session ID: '{session_id_for_test}' <<<")

    # 1. Create or get session and set its state with mock data
    
    # We can pass initial_state directly to create_session.
    initial_state_for_run = {
        "cgm_data": mock_cgm_data,
        "context_event": mock_context_event,
        # Add any other state your agent might expect initially
    }
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id_for_test,
        state=initial_state_for_run # Initialize session with mock data
    )
    print(f" Initial state for this run: {json.dumps(session.state, indent=2)}")
    # print(f"  Session ID: {session.session_id}")


    # 2. Define a generic trigger message (since data comes from state)
    trigger_message_text = "Generate glycemic forecast based on current state."
    user_content = types.Content(role='user', parts=[types.Part(text=trigger_message_text)])
    print(f"  Sending trigger message: '{trigger_message_text}'")

    # 3. Run the agent
    final_forecast_json_str = "No forecast generated."
    async for event in runner.run_async(user_id=USER_ID, session_id=session_id_for_test, new_message=user_content):
        if event.is_final_response() and event.content and event.content.parts:
            final_forecast_json_str = event.content.parts[0].text # This will be the JSON string

    # 4. Retrieve and print the result from session state
    updated_session = await session_service.get_session(app_name=APP_NAME,
                                                  user_id=USER_ID,
                                                  session_id=session_id_for_test)

    print(f"\n  <<< Agent's Direct Text Output (should be JSON string):")
    print(final_forecast_json_str) # The raw JSON string from the agent

    stored_forecast_objec = updated_session.state.get(glycemic_forecaster_agent.output_key)

    print(f"\n  --- Content of session.state['{glycemic_forecaster_agent.output_key}']: ---")
    if  stored_forecast_objec:
        try:
            # parsed_forecast = json.loads( stored_forecast_objec)
            print(json.dumps(stored_forecast_objec, indent=2)) # Pretty print
            # Here you can add assertions to validate the parsed_forecast
            # e.g., assert parsed_forecast['short_term_outlook']['overall_risk_level'] == "expected_value"
        except (json.JSONDecodeError, TypeError) as e:
            print(f"    Error parsing stored forecast as JSON: {e}")
            print(f"    Raw  stored_forecast_objec: { stored_forecast_objec}")
    else:
        print("    No forecast found in session state.")
    print("-" * 40)

# --- Run Interactions with Mock Data ---
async def main_test_runner():
    print("--- Starting Glycemic Forecaster Agent Test Scenarios ---")

    # # Test Case 1: Mock data for a stable scenario
    # print("Test Case 1: Stable Scenario")
    # mock_cgm_stable = mock_cgm_data_stable
    # mock_context_stable = mock_context_event_stable
    # session_id_stable = f"test_session_stable_{uuid.uuid4()}" # Unique ID
    # await test_glycemic_agent_with_mock_state(session_id_stable, mock_cgm_stable, mock_context_stable)

    # # Test Case 2: Mock data for a potential hyperglycemia scenario
    # print("Test Case 2: Potential Hyperglycemia")
    # mock_cgm_hyper = mock_cgm_data_hyper
    # mock_context_hyper = mock_context_event_hyper
    # session_id_hyper = f"test_session_hyper_{uuid.uuid4()}" # Unique ID
    # await test_glycemic_agent_with_mock_state(session_id_hyper, mock_cgm_hyper, mock_context_hyper)

    # # Test Case 3: Mock data for a potential hypoglycemia scenario
    # print("Test Case 3: Potential Hypoglycemia")
    # mock_cgm_hypo = mock_cgm_data_hypo
    # mock_context_hypo = mock_context_event_hypo
    # session_id_hypo = f"test_session_hypo_{uuid.uuid4()}" # Unique ID
    # await test_glycemic_agent_with_mock_state(session_id_hypo, mock_cgm_hypo, mock_context_hypo)

    # # Test Case 4: Mock data with data quality issues - Erractic readings
    # print("Test Case 4: Data Quality Issues - Erractic Readings")
    # mock_cgm_erratic = mock_cgm_data_erratic
    # mock_context_erratic = mock_context_event_erratic
    # session_id_erratic = f"test_session_erratic_{uuid.uuid4()}" # Unique ID
    # await test_glycemic_agent_with_mock_state(session_id_erratic, mock_cgm_erratic, mock_context_erratic)

    # # Test Case 5: Mock data with data quality issues - Missing data
    # print("Test Case 5: Data Quality Issues - Missing Data")
    # mock_cgm_missing = mock_cgm_data_missing
    # mock_context_missing = mock_context_event_missing
    # session_id_missing = f"test_session_missing_{uuid.uuid4()}" # Unique ID
    # await test_glycemic_agent_with_mock_state(session_id_missing, mock_cgm_missing, mock_context_missing)

    # # Test Case 6: Mock data with stress event impacting Glucose
    # print("Test Case 6: Stress Event Impacting Glucose")
    # mock_cgm_stress = mock_cgm_data_stress
    # mock_context_stress = mock_context_event_stress
    # session_id_stress = f"test_session_stress_{uuid.uuid4()}" # Unique ID
    # await test_glycemic_agent_with_mock_state(session_id_stress, mock_cgm_stress, mock_context_stress)

    # # Test Case 7: Mock data with illness event impacting Glucose
    # print("Test Case 7: Illness Impacting Glucose")
    # mock_cgm_illness = mock_cgm_data_illness
    # mock_context_illness = mock_context_event_illness
    # session_id_illness = f"test_session_illness_{uuid.uuid4()}" # Unique ID
    # await test_glycemic_agent_with_mock_state(session_id_illness, mock_cgm_illness, mock_context_illness)

    # # Test Case 8: Mock data with complex meal - High Fat, High Carb (potential delayed spike)
    # print("Test Case 8: Complex Meal - High Fat, High Carb (potential delayed spike)")
    # mock_cgm_complex_meal = mock_cgm_data_complex_meal_initial
    # mock_context_complex_meal = mock_context_event_complex_meal
    # session_id_complex_meal = f"test_session_complex_meal_{uuid.uuid4()}" # Unique ID
    # await test_glycemic_agent_with_mock_state(session_id_complex_meal, mock_cgm_complex_meal, mock_context_complex_meal)

    # Test Case 9: Conflicting Information
    print("Test Case 9: Conflicting Information - User feels hypo, CGM high")
    session_id_conflicting = f"test_session_conflicting_{uuid.uuid4()}"
    await test_glycemic_agent_with_mock_state(session_id_conflicting, mock_cgm_data_conflicting_high, mock_context_event_conflicting_high)

    # Test Case 10: Old Contextual Data
    print("Test Case 10: Old Contextual Data - Meal 4 hours ago")
    session_id_old_context = f"test_session_old_context_{uuid.uuid4()}"
    await test_glycemic_agent_with_mock_state(session_id_old_context, mock_cgm_data_old_context, mock_context_event_old_context)

    # Test Case 11: Multiple Recent Context Events (simulated via most recent)
    print("Test Case 11: Recent Exercise After Implied Meal")
    session_id_multi_event = f"test_session_multi_event_{uuid.uuid4()}"
    await test_glycemic_agent_with_mock_state(session_id_multi_event, mock_cgm_data_multi_event, mock_context_event_multi_event_exercise)

    # Test Case 12: No Obvious Context, Unexpected Rise
    print("Test Case 12: No Obvious Context, Unexpected Rise")
    session_id_unexplained_rise = f"test_session_unexplained_rise_{uuid.uuid4()}"
    await test_glycemic_agent_with_mock_state(session_id_unexplained_rise, mock_cgm_data_unexplained_rise, mock_context_event_unexplained_rise)

    # Test Case 13: Very High Glucose
    print("Test Case 13: Very High Glucose, User Unwell")
    session_id_very_high = f"test_session_very_high_{uuid.uuid4()}"
    await test_glycemic_agent_with_mock_state(session_id_very_high, mock_cgm_data_very_high, mock_context_event_very_high)


    # Add more test cases with different mock data to cover various scenarios

if __name__ == "__main__":
    
    try:
        asyncio.run(main_test_runner())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e) :
            print("\nINFO: To run in Jupyter/Colab, execute 'await main_test_runner()' in a new cell.")
        else:
            raise