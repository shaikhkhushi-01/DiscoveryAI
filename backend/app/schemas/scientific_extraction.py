from pydantic import BaseModel, Field
from typing import Any

class ScientificEntities(BaseModel):
    topics: list[str] = []
    keywords: list[str] = []
    methods: list[str] = []
    algorithms: list[str] = []
    datasets: list[str] = []
    problems: list[str] = []
    applications: list[str] = []
    domains: list[str] = []
    metrics: list[str] = []
    baselines: list[str] = []
    experimental_settings: list[str] = []
    results: list[str] = []
    limitations: list[str] = []
    future_work: list[str] = []
    metadata: dict[str, Any] = {}

class Limitation(BaseModel):
    text: str
    category: str
    evidence: str | None = None

class FutureDirection(BaseModel):
    text: str
    category: str = "unspecified"
    evidence: str | None = None

class ScientificDocument(BaseModel):
    document_id: int | None = None
    title: str | None = None
    authors: list[str] = []
    institutions: list[str] = []
    year: int | None = Field(default=None, ge=1900, le=2100)
    venue: str | None = None
    doi: str | None = None
    entities: ScientificEntities
    limitations: list[Limitation] = []
    future_work: list[FutureDirection] = []
