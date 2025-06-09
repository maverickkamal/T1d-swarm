import json
import asyncio
import uuid

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

from .prompts import SIMULATED_CGM_FEED_PROMPT, CGMDataOutput
from t1d_swarm.tools import generate_scenario

load_dotenv()


# --- Define Constants & YOUR Schema ---
APP_NAME = "cgm_feed_agent"
USER_ID = "test_physician_789" # Or a relevant user identifier
MODEL_NAME = "gemini-2.0-flash"

# --- Configure Llm Agent --- 

SCHEMA_JSON_STRING = json.dumps(CGMDataOutput.model_json_schema(), indent=2)

instruction_for_agent = SIMULATED_CGM_FEED_PROMPT.format(
model_output=SCHEMA_JSON_STRING
)

cgm_feed_agent = LlmAgent(
    model=MODEL_NAME,
    name="SimulatedCGMFeedAgent",
    description="Provides mock continuous glucose readings imitating that of a type 1 diabetes patient.",
    instruction=instruction_for_agent,
    output_schema=CGMDataOutput,
    output_key="cgm_data",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)

# --- Set up Session Management and Runner ---
print("--- Setting up Session Service and Runner ---")
session_service = InMemorySessionService()

# We will create/update the session state for each test case within the interaction logic.
# So, we don't need to create multiple session IDs as constants beforehand.
runner = Runner(
    agent=cgm_feed_agent,
    app_name=APP_NAME,
    session_service=session_service
)
print(f"Runner configured for agent: {cgm_feed_agent.name}")

# --- Define Agent Interaction Logic (for testing) ---
async def test_cgm_agent_with_scenario_state(
    session_id_for_test: str, # A unique session ID for each test run
    mock_scenario: dict,      # mock CGM data
):
    """
    Sets up session state with mock data, runs the glycemic forecaster,
    and prints the resulting forecast from the state.
    """
    print(f"\n>>> Testing Agent with Session ID: '{session_id_for_test}' <<<")

    # 1. Create or get session and set its state with mock data
    
    # We can pass initial_state directly to create_session.
    initial_state_for_run = {
        "scenario": mock_scenario,
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
    trigger_message_text = "Generate ambient context based on current state."
    user_content = types.Content(role='user', parts=[types.Part(text=trigger_message_text)])
    print(f"  Sending trigger message: '{trigger_message_text}'")

    # 3. Run the agent
    final_cgm_json_str = "No forecast generated."
    async for event in runner.run_async(user_id=USER_ID, session_id=session_id_for_test, new_message=user_content):
        if event.is_final_response() and event.content and event.content.parts:
            final_cgm_json_str = event.content.parts[0].text # This will be the JSON string

    # 4. Retrieve and print the result from session state
    updated_session = await session_service.get_session(app_name=APP_NAME,
                                                  user_id=USER_ID,
                                                  session_id=session_id_for_test)

    print(f"\n  <<< Agent's Direct Text Output (should be JSON string):")
    print(final_cgm_json_str) # The raw JSON string from the agent

    stored_forecast_objec = updated_session.state.get(cgm_feed_agent.output_key)

    print(f"\n  --- Content of session.state['{cgm_feed_agent.output_key}']: ---")
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
    print("--- Starting Simulated CGM Agent Test Scenarios ---")

    mock_scenario_random = generate_scenario()
    print(f"Scenario: {mock_scenario_random}")
    # Test Case 13: Very High Glucose
    print("Test Case 13: Very High Glucose, User Unwell")
    session_id_very_high = f"test_session_very_high_{uuid.uuid4()}"
    await test_cgm_agent_with_scenario_state(session_id_very_high, mock_scenario_random)


    # Add more test cases with different mock data to cover various scenarios

if __name__ == "__main__":
    
    try:
        asyncio.run(main_test_runner())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e) :
            print("\nINFO: To run in Jupyter/Colab, execute 'await main_test_runner()' in a new cell.")
        else:
            raise

        