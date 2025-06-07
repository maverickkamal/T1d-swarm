

CALLBACK_PROMPT = """Generate a single sentence describing a random scenario involving CGM data and user context.
The output MUST be a JSON object in the format: `{'scenarios': 'Your sentence here.'}`
The sentence should hint at the CGM state (e.g., stable, rising, falling, erratic) and a relevant ambient context 
(e.g., after a meal, during exercise, sensor issue, stress) without providing specific data values, trend arrow names, or detailed event structures.

Example: `{'scenarios': 'User experiences rapidly rising glucose after consuming a high-carbohydrate meal.'}`
"""