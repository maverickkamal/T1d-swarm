from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai.types import Part

from .tools import extract_json_from_llm_output


class ConfidenceCheckAgent(BaseAgent):
    """
    A custom agent that evaluates confidence scores in agent verification outputs
    and determines whether to exit the refinement loop.
    
    This agent implements a threshold-based decision system for loop termination,
    helping to prevent infinite refinement cycles while ensuring quality outputs.
    
    Design Pattern: Circuit Breaker for iterative agent workflows
    Time Complexity: O(1) - Simple threshold comparison and JSON extraction
    """
    threshold: float
    
    def __init__(self, name: str, threshold: float = 0.8):
        """
        Initialize the confidence check agent.
        
        Args:
            name (str): Agent identifier
            threshold (float): Confidence threshold for loop exit (0.0-1.0)
                              Default 0.8 provides good balance between quality and efficiency
        """
        super().__init__(name=name, sub_agents=[], threshold=threshold)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Core logic for confidence-based loop exit evaluation.
        
        Extracts verification confidence from session state and compares against
        threshold to determine whether refinement loop should continue or exit.
        
        Args:
            ctx: Invocation context containing session state and metadata
            
        Yields:
            Event: Agent execution event with escalation action if threshold met
            
        Time Complexity: O(1) - Fixed operations regardless of input size
        Error Handling: Graceful degradation with default values for missing data
        """
        print(f"--- Running {self.name} ---")
        
        # Extract verification output from session state
        # Default to empty dict if missing to prevent KeyError
        verification_output = ctx.session.state.get("verification_output", {})
        print(f"  - Raw verification output: {verification_output}")
        
        # Handle case where verification_output might be a string with embedded JSON
        # This covers scenarios where LLM output hasn't been parsed yet
        if isinstance(verification_output, str):
            verification_output = extract_json_from_llm_output(verification_output)
        
        # Validate extraction was successful
        if verification_output and isinstance(verification_output, dict):
            print(f"  - Parsed verification output: {verification_output}")
            print(f"  - Output type: {type(verification_output)}")
        else:
            print("  - Warning: Could not extract valid verification data")
            verification_output = {}
        
        # Extract confidence score with safe fallback
        # Using .get() with default 0.0 prevents KeyError and ensures numeric type
        confidence = verification_output.get("verification_confidence", 0.0)
        
        # Type safety: ensure confidence is numeric
        try:
            confidence = float(confidence)
        except (ValueError, TypeError):
            print(f"  - Warning: Invalid confidence value '{confidence}', defaulting to 0.0")
            confidence = 0.0
        
        print(f"  - Checking confidence: {confidence} >= {self.threshold}?")

        # Core decision logic: threshold comparison determines loop continuation
        if confidence >= self.threshold:
            print(f"  - ✅ Confidence threshold met ({confidence:.2f} >= {self.threshold}). Escalating to exit loop.")
            actions = EventActions(escalate=True)  # Signal loop termination
            event_content = [Part(text=f"Confidence threshold met ({confidence:.2f}). Verification successful.")]
        else:
            print(f"  - 🔄 Confidence below threshold ({confidence:.2f} < {self.threshold}). Continuing loop.")
            actions = EventActions()  # Continue loop iteration
            event_content = [Part(text=f"Confidence too low ({confidence:.2f}). Continuing refinement.")]

        # Yield execution event with appropriate action
        yield Event(
            author=self.name,
            content={"parts": event_content},
            actions=actions,
            invocation_id=ctx.invocation_id
        )