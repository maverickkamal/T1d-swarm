from .logic import ConfidenceCheckAgent



LoopExitAgent = ConfidenceCheckAgent(
    name="ConfidenceChecker",
    threshold=0.8
)