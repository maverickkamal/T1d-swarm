import json
from typing import AsyncGenerator
import re
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai.types import Part

from .tools import extract_json_from_llm_output



class ConfidenceCheckAgent(BaseAgent):
    """
    A custom agent that checks a confidence score in the session state
    and escalates to exit a LoopAgent if the score meets a threshold.
    """
    threshold: float
    
    def __init__(self, name: str, threshold: float = 0.8):
        super().__init__(name=name, sub_agents=[], threshold=threshold)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        print(f"--- Running {self.name} ---")
        verification_output = ctx.session.state.get("verification_output", {})
        print(f"  - Verification output: {verification_output}")
        # Ensure verification_output is a dictionary by extracting from markdown if needed
        verification_output = extract_json_from_llm_output(verification_output)

        if verification_output:
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