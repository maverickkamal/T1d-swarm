# In your agent.py file

import asyncio
import uuid
import json
from typing import AsyncGenerator
import re
from dotenv import load_dotenv
from google.adk.agents import (
    BaseAgent, LlmAgent, LoopAgent
)
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.types import Part

load_dotenv()

# --- The Custom Agent Definition (from above) ---

class ConfidenceCheckAgent(BaseAgent):
    """
    A custom agent that checks a confidence score in the session state
    and escalates to exit a LoopAgent if the score meets a threshold.
    """
    threshold: float
    
    def __init__(self, name: str, threshold: float = 0.8):
        super().__init__(name=name, sub_agents=[], threshold=threshold)
        # self.threshold = threshold

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        print(f"--- Running {self.name} ---")
        verification_output = ctx.session.state.get("verification_output", {})
        print(f"  - Verification output: {verification_output}")
        # Ensure verification_output is a dictionary by extracting from markdown if needed
        if isinstance(verification_output, str):
            # Use regex to extract JSON from markdown code block
            match = re.search(r"json\n(.*?)\n", verification_output, re.DOTALL)
            if match:
                json_string = match.group(1)
                try:
                    verification_output = json.loads(json_string)
                except json.JSONDecodeError:
                    print("Warning: Could not decode extracted JSON string.")
                    verification_output = {} # Set to empty dict if decoding fails
            else:
                print("Warning: Could not find JSON in markdown code block.")
                verification_output = {} # Set to empty dict if JSON not found
        
        print(verification_output)
        print(type(verification_output))
        confidence = verification_output.get("verification_confidence", 0.0)
        print(f"  - Checking confidence: {confidence} >= {self.threshold}?")

        if confidence >= self.threshold:
            print(f"  - Confidence threshold met. Escalating to exit loop.")
            actions = EventActions(escalate=True)
            event_content = [Part(text="Confidence threshold met. Verification successful.")]
        else:
            print(f"  - Confidence below threshold. Continuing loop.")
            actions = EventActions()
            event_content = [Part(text="Confidence too low. Continuing refinement.")] # Create content as list of Parts

        yield Event(
            author=self.name,
            content={"parts": event_content},
            actions=actions,
            invocation_id=ctx.invocation_id
        )

# --- A Mock Agent to Simulate Verification Output ---

# This agent simulates another step in your loop that *produces*
# the confidence score and saves it to the session state.
verification_simulator_agent = LlmAgent(
    name="VerificationSimulator",
    model="gemini-2.0-flash",
    instruction="""Based on the user's prompt, generate a JSON object with a
    'verification_confidence' score. If the user says 'high confidence',
    set the score to 0.9. Otherwise, set it to 0.6.
    Output ONLY the JSON object.
    Example for 'high confidence': {"verification_confidence": 0.9}
    Example for anything else: {"verification_confidence": 0.6}
    """,
    # This key saves the agent's JSON output directly into session.state
    output_key="verification_output"
)

# --- Instantiate Your Custom Agent ---
confidence_checker = ConfidenceCheckAgent(
    name="ConfidenceChecker",
    threshold=0.8
)

# --- Define the LoopAgent ---
# The LoopAgent orchestrates the sub-agents.
# The order is important: first simulate, then check.
root_agent = LoopAgent(
    name="VerificationLoop",
    sub_agents=[
        verification_simulator_agent,
        confidence_checker  # Your custom agent is here
    ],
    max_iterations=5 # A safety limit to prevent infinite loops
)

# --- Code to Run the Example ---
async def main():
    session_service = InMemorySessionService()
    # Setup runner and session service
    runner = Runner(
        agent=root_agent,
        app_name="loop_test_app",
        session_service=session_service
    )

    async def run_and_print(query: str, session_id: str):
        print(f"\n{'='*20} RUNNING WITH QUERY: '{query}' {'='*20}")
        user_message = types.Content(role='user', parts=[types.Part(text=query)])
        # Create a new session if it doesn't exist
        # if not runner.session_service.exists_session(session_id):
        #     await runner.session_service.create_session(session_id, user_id="test_user")
        session = await session_service.create_session(
            app_name="loop_test_app",
            user_id="test_user",
            session_id=session_id,
        )
        async for event in runner.run_async(
            user_id="test_user", session_id=session_id, new_message=user_message
        ):
            print(f"Event from [{event.author}]: {event.content}")
            if event.actions.escalate:
                print(">> Escalation signal received by runner! Loop will terminate.")

    # Scenario 1: Confidence is low, loop continues (until max_iterations)
    
    await run_and_print("This is a low confidence scenario", "session_1")
    print("we are here")
    # Scenario 2: Confidence is high, custom agent escalates and exits the loop
    await run_and_print("This is a high confidence scenario", "session_2")


if __name__ == "__main__":
    # Ensure GOOGLE_API_KEY is set as an environment variable
    asyncio.run(main())