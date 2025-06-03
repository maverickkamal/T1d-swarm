
import json
import asyncio
import uuid
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from prompts import INSIGHT_PRESENTER_PROMPT

load_dotenv()  

# load environment variables
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
USER_ID    = os.getenv("USER_ID", "test_physician_789")

# constants
APP_NAME           = "insight_presenter_agent"
INPUT_KEY_FORECAST = "risk_forecast"
OUTPUT_KEY_INSIGHT = "insight_presentation"

# defining the agent
INSIGHT_PRESENTER_AGENT = LlmAgent(
    model=MODEL_NAME,
    name="InsightPresenterAgent",
    description="Takes a glycemic risk_forecast JSON and produces a plain-English summary.",
    instruction="",                  # we’ll fill this in right before each run
    output_key=OUTPUT_KEY_INSIGHT,     # store LLM text under session.state["insight_presentation"]
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True
)

# in-memory session and runner
session_service = InMemorySessionService()
presenter_runner = Runner(
    agent=INSIGHT_PRESENTER_AGENT,
    app_name=APP_NAME,
    session_service=session_service
)


#  SINGLE-SCENARIO RUNNER: Given one mock_forecast, run the agent

async def run_presenter_with_single_forecast(mock_forecast: dict):
    """
    1) Create a session where session.state["risk_forecast"] = mock_forecast
    2) Format the prompt by injecting mock_forecast as JSON
    3) Send a dummy trigger so ADK knows to call the LLM
    4) Capture & print the LLM’s plain-text output
    5) Show session.state["insight_presentation"] (should match LLM text)
    """

    # 1) Create a brand-new session_id each time
    session_id = f"session_{uuid.uuid4()}"
    print(f">>> Starting Insight Presenter for session_id = {session_id}\n")

    # Put mock_forecast into session.state
    initial_state = {INPUT_KEY_FORECAST: mock_forecast}
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
        state=initial_state
    )
    print("Initial session.state:")
    print(json.dumps(session.state, indent=2), "\n")

    # 2) Inject the JSON into the prompt
    forecast_json_str = json.dumps(mock_forecast, indent=2)
    INSIGHT_PRESENTER_AGENT.instruction = INSIGHT_PRESENTER_PROMPT.format(
        risk_forecast_json=forecast_json_str
    )

    # 3) Create a dummy “trigger” message so the LLM runs
    trigger = "Generate plain-English insight now."
    user_content = types.Content(role="user", parts=[types.Part(text=trigger)])
    print(f"Trigger message: “{trigger}”\n")

    # 4) Run the agent, capture final plain-text
    final_insight = None
    async for event in presenter_runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_insight = event.content.parts[0].text

    print("<<< LLM’s Plain-Text Output >>>")
    if final_insight:
        print(final_insight)
    else:
        print("[No response from LLM]")
    print("")

    # 5) Fetch updated session, show what’s stored under OUTPUT_KEY_INSIGHT
    updated = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )
    stored = updated.state.get(OUTPUT_KEY_INSIGHT)
    print(f"--- session.state['{OUTPUT_KEY_INSIGHT}'] ---")
    if stored:
        print(stored)
    else:
        print("[Nothing stored]")

    print("\n" + "=" * 60 + "\n")


# -------------------------------------------------------------------
# 6) If someone runs this file directly, do nothing.
#    (We’ll call this module from a separate “test runner.”)
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("This file defines the InsightPresenterAgent. To run tests, execute run_insight_tests.py.")
