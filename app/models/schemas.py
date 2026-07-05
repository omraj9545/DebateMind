from pydantic import BaseModel, Field
from typing import Optional, Dict

class DebateRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="The debate motion or question",
        json_schema_extra={"example": "Should AI replace human judges in courts?"}
    )

class AgentScores(BaseModel):
    pro:     int
    against: int

class DebateScores(BaseModel):
    argument_quality:    AgentScores
    evidence_strength:   AgentScores
    logical_consistency: AgentScores
    persuasiveness:      AgentScores

class AgentTiming(BaseModel):
    pro:        float
    against:    float
    fact_check: float
    judge:      float
    total:      float

class DebateResponse(BaseModel):
    debate_id:         str
    topic:             str
    pro_argument:      str
    against_argument:  str
    fact_check:        str
    winner:            str
    verdict:           str
    scores:            DebateScores
    key_turning_point: Optional[str] = None
    timing:            AgentTiming
    models:            Optional[Dict[str, str]] = None
