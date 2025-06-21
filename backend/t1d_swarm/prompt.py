

CALLBACK_PROMPT = """Generate a single sentence describing a random scenario involving CGM data and user context.
The output MUST be a JSON object in the format: `{'scenarios': 'Your sentence here.'}`
The sentence should hint at the CGM state (e.g., stable, rising, falling, erratic) and a relevant ambient context 
(e.g., after a meal, during exercise, sensor issue, stress) without providing specific data values, trend arrow names, or detailed event structures.

Example: `{'scenarios': 'User experiences rapidly rising glucose after consuming a high-carbohydrate meal.'}`
"""

REPHRASE_PROMPT = """You are an AI assistant that refines user text into a single, well-formed sentence describing a plausible Type 1 Diabetes scenario for a simulation.

Your task is to take the user's input and rephrase it into a clear sentence hinting at both a glucose state (e.g., rising, falling, erratic) and a relevant context (e.g., meal, exercise, stress). Do not use specific numbers or technical CGM trend names.

Your output **MUST** be only a single, valid JSON object formatted as:
`{"scenario_description": "Your refined sentence here."}`

**Example:**
If the user prompt is: `pizza and coke, bg going up fast`
Your required JSON output is: `{"scenario_description": "After consuming a high-carbohydrate meal of pizza and soda, the user’s glucose is rising rapidly."}`
"""