import json
import asyncio
import uuid

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

from prompts import INSIGHT_PRESENTER_PROMPT
from test_forecasts import *

load_dotenv()


# --- Define Constants & YOUR Schema ---
APP_NAME = "glycemic_forecast_agent"
USER_ID = "test_physician_789" # Or a relevant user identifier
MODEL_NAME = "gemini-2.5-pro-preview-05-06"

# --- Configure Llm Agent --- 


insight_presenter_agent = LlmAgent(
    model=MODEL_NAME,
    name="InsightPresenterAgent",
    description="Take the processed insight from our 'Brain' and present it in a user-friendly way",
    instruction=INSIGHT_PRESENTER_PROMPT
)

# --- Set up Session Management and Runner ---
print("--- Setting up Session Service and Runner ---")
session_service = InMemorySessionService()

# We will create/update the session state for each test case within the interaction logic.
# So, we don't need to create multiple session IDs as constants beforehand.
runner = Runner(
    agent=insight_presenter_agent,
    app_name=APP_NAME,
    session_service=session_service
)
print(f"Runner configured for agent: {insight_presenter_agent.name}")

# --- Define Agent Interaction Logic (for testing) ---
async def test_insight_agent_with_mock_state(
    session_id_for_test: str, # A unique session ID for each test run
    risk_forecast: dict,      # risk insight data
):
    """
    Sets up session state with mock data, runs the glycemic forecaster,
    and prints the resulting insight from the state.
    """
    print(f"\n>>> Testing Agent with Session ID: '{session_id_for_test}' <<<")

    # 1. Create or get session and set its state with mock data
    
    # We can pass initial_state directly to create_session.
    initial_state_for_run = {
        "risk_forecast": risk_forecast
    }

  
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id_for_test,
        state=initial_state_for_run # Initialize session with mock insight
    )
    print(f" Initial state for this run: {json.dumps(session.state, indent=2)}")
    # print(f"  Session ID: {session.session_id}")


    # 2. Define a generic trigger message (since data comes from state)
    trigger_message_text = "Generate insight based on current state."
    user_content = types.Content(role='user', parts=[types.Part(text=trigger_message_text)])
    print(f"  Sending trigger message: '{trigger_message_text}'")

    # 3. Run the agent
    final_insight_str = "No insight generated."
    async for event in runner.run_async(user_id=USER_ID, session_id=session_id_for_test, new_message=user_content):
        if event.is_final_response() and event.content and event.content.parts:
            final_insight_str = event.content.parts[0].text 

    # 4. Retrieve and print the result from session state
    updated_session = await session_service.get_session(app_name=APP_NAME,
                                                  user_id=USER_ID,
                                                  session_id=session_id_for_test)

    print(f"\n  <<< Agent's Direct Text Output :")
    print(final_insight_str) # The raw JSON string from the agent

    # stored_forecast_objec = updated_session.state.get(insight_presenter_agent.output_key)

    # print(f"\n  --- Content of session.state['{insight_presenter_agent.output_key}']: ---")
    # if  stored_forecast_objec:
    #     try:
    #         # parsed_forecast = json.loads( stored_forecast_objec)
    #         print(json.dumps(stored_forecast_objec, indent=2)) # Pretty print
    #         # Here you can add assertions to validate the parsed_forecast
    #         # e.g., assert parsed_forecast['short_term_outlook']['overall_risk_level'] == "expected_value"
    #     except (json.JSONDecodeError, TypeError) as e:
    #         print(f"    Error parsing stored insight as JSON: {e}")
    #         print(f"    Raw  stored_forecast_objec: { stored_forecast_objec}")
    # else:
    #     print("    No insight found in session state.")
    print("-" * 40)

# --- Run Interactions with Mock Data ---
async def main_test_runner():
    print("--- Starting Glycemic Forecaster Agent Test Scenarios ---")

    # Test Case 1: Mock data for a stable scenario
    print("Test Case 1: Stable Scenario")
    # mock_forecast_stable = mock_forecast_stable
    session_id_stable = f"test_session_stable_{uuid.uuid4()}" # Unique ID
    await test_insight_agent_with_mock_state(session_id_stable, mock_forecast_stable)

    # Test Case 2: Mock data for a potential hyperglycemia scenario
    print("Test Case 2: Potential Hyperglycemia")
    mock_cgm_hyper = mock_forecast_hyper
    session_id_hyper = f"test_session_hyper_{uuid.uuid4()}" # Unique ID
    await test_insight_agent_with_mock_state(session_id_hyper, mock_cgm_hyper)

    # Test Case 3: Mock data for a potential hypoglycemia scenario
    print("Test Case 3: Potential Hypoglycemia")
    mock_cgm_hypo = mock_forecast_hypo
    session_id_hypo = f"test_session_hypo_{uuid.uuid4()}" # Unique ID
    await test_insight_agent_with_mock_state(session_id_hypo, mock_cgm_hypo)

    # Test Case 4: Mock data with data quality issues - Erractic readings
    print("Test Case 4: Data Quality Issues - Erractic Readings")
    mock_cgm_erratic = mock_forecast_erractic
    session_id_erratic = f"test_session_erratic_{uuid.uuid4()}" # Unique ID
    await test_insight_agent_with_mock_state(session_id_erratic, mock_cgm_erratic)

    # Test Case 5: Mock data with data quality issues - Missing data
    print("Test Case 5: Data Quality Issues - Missing Data")
    mock_cgm_missing = mock_forecast_missing
    session_id_missing = f"test_session_missing_{uuid.uuid4()}" # Unique ID
    await test_insight_agent_with_mock_state(session_id_missing, mock_cgm_missing)

    # Test Case 6: Mock data with stress event impacting Glucose
    print("Test Case 6: Stress Event Impacting Glucose")
    mock_cgm_stress = mock_forecast_stress
    session_id_stress = f"test_session_stress_{uuid.uuid4()}" # Unique ID
    await test_insight_agent_with_mock_state(session_id_stress, mock_cgm_stress)

    # Test Case 7: Mock data with illness event impacting Glucose
    print("Test Case 7: Illness Impacting Glucose")
    mock_cgm_illness = mock_forecast_illness
    session_id_illness = f"test_session_illness_{uuid.uuid4()}" # Unique ID
    await test_insight_agent_with_mock_state(session_id_illness, mock_cgm_illness)

    # Test Case 8: Mock data with complex meal - High Fat, High Carb (potential delayed spike)
    print("Test Case 8: Complex Meal - High Fat, High Carb (potential delayed spike)")
    mock_cgm_complex_meal = mock_forecast_complex
    session_id_complex_meal = f"test_session_complex_meal_{uuid.uuid4()}" # Unique ID
    await test_insight_agent_with_mock_state(session_id_complex_meal, mock_cgm_complex_meal)

    # Test Case 9: Conflicting Information
    print("Test Case 9: Conflicting Information - User feels hypo, CGM high")
    session_id_conflicting = f"test_session_conflicting_{uuid.uuid4()}"
    await test_insight_agent_with_mock_state(session_id_conflicting, mock_forecast_conflict)

    # Test Case 10: Old Contextual Data
    print("Test Case 10: Old Contextual Data - Meal 4 hours ago")
    session_id_old_context = f"test_session_old_context_{uuid.uuid4()}"
    await test_insight_agent_with_mock_state(session_id_old_context, mock_forecast_old)

    # Test Case 11: Multiple Recent Context Events (simulated via most recent)
    print("Test Case 11: Recent Exercise After Implied Meal")
    session_id_multi_event = f"test_session_multi_event_{uuid.uuid4()}"
    await test_insight_agent_with_mock_state(session_id_multi_event, mock_forecast_exercise)

    # Test Case 12: No Obvious Context, Unexpected Rise
    print("Test Case 12: No Obvious Context, Unexpected Rise")
    session_id_unexplained_rise = f"test_session_unexplained_rise_{uuid.uuid4()}"
    await test_insight_agent_with_mock_state(session_id_unexplained_rise, mock_forecast_no_context)

    # Test Case 13: Very High Glucose
    print("Test Case 13: Very High Glucose, User Unwell")
    session_id_very_high = f"test_session_very_high_{uuid.uuid4()}"
    await test_insight_agent_with_mock_state(session_id_very_high, mock_forecast_unwell)


    # Add more test cases with different mock data to cover various scenarios

if __name__ == "__main__":
    
    try:
        asyncio.run(main_test_runner())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e) :
            print("\nINFO: To run in Jupyter/Colab, execute 'await main_test_runner()' in a new cell.")
        else:
            raise