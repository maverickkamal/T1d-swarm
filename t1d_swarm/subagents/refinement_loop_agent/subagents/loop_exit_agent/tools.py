import re
import json
from typing import Dict, Any, Optional

def extract_json_from_llm_output(raw_output: str) -> Optional[Dict[str, Any]]:
    """
    Robustly extracts a JSON object from a string that may contain surrounding text.

    This function is designed to handle typical LLM outputs where a JSON object
    is embedded within narrative text, often enclosed in markdown-style code blocks
    (e.g., ```json ... ```).

    Args:
        raw_output: The raw string output from the LLM agent.

    Returns:
        A dictionary if a valid JSON object is found and parsed successfully.
        None if no JSON block is found or if parsing fails.
    """
    if not isinstance(raw_output, str):
        # Handle cases where the input might not be a string
        return None

    # Regex to find a JSON block enclosed in ```json ... ``` or just ``` ... ```
    # It's non-greedy (.*?) to handle cases with multiple code blocks.
    match = re.search(r'```(?:json)?\s*({.*?})\s*```', raw_output, re.DOTALL)

    json_string = None
    if match:
        json_string = match.group(1)
    else:
        # Fallback for cases where the JSON is not in a code block but is the
        # only curly-brace delimited object in the string. This is less reliable.
        # For your current output, the regex above is the primary method.
        if '{' in raw_output and '}' in raw_output:
             # Find the first '{' and the last '}'
            start = raw_output.find('{')
            end = raw_output.rfind('}') + 1
            if start != -1 and end != -1:
                json_string = raw_output[start:end]

    if not json_string:
        print("Warning: No JSON block found in the output.")
        return None

    try:
        # Parse the extracted string into a Python dictionary
        parsed_json = json.loads(json_string)
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"Warning: Could not decode extracted JSON string. Error: {e}")
        print(f"--- Faulty JSON String ---")
        print(json_string)
        print("--------------------------")
        return None
