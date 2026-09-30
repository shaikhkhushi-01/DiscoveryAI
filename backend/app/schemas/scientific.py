from pydantic import BaseModel, ConfigDict, Field

class ScientificBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class PaperResponse(ScientificBase):
    id: int
    title: str
    doi: str | None = None
    abstract: str | None = None
    venue: str | None = None

class ResearchGapResponse(ScientificBase):
    id: int
    title: str
    description: str
    gap_type: str
    confidence: float | None = Field(default=None, ge=0, le=1)

class HypothesisResponse(ScientificBase):
    id: int
    statement: str
    rationale: str | None = None
    status: str

class ExperimentResponse(ScientificBase):
    id: int
    name: str
    methodology: str | None = None
    status: str
