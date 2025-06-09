
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

from .prompts import INSIGHT_PRESENTER_PROMPT

load_dotenv()


MODEL_NAME = "gemini-2.5-pro-preview-05-06"

# --- Configure Llm Agent --- 


InsightPresenterAgent = LlmAgent(
    model=MODEL_NAME,
    name="InsightPresenterAgent",
    description="Take the processed insight from our 'Brain' and present it in a user-friendly way",
    instruction=INSIGHT_PRESENTER_PROMPT
)