from typing import TypedDict, Optional

class AgentResult(TypedDict):
    content: str
    latency: float        # seconds

class DebateState(TypedDict):
    topic:             str
    pro:               Optional[AgentResult]
    against:           Optional[AgentResult]
    fact_check:        Optional[AgentResult]
    verdict:           Optional[dict]
    verdict_latency:   Optional[float]
    total_latency:     Optional[float]
    debate_id:         Optional[str]
    error:             Optional[str]
    status:            Optional[str]
