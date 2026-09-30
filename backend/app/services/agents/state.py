from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class DiscoveryState:
    question: str
    retrieval: dict[str, Any] = field(default_factory=dict)
    gaps: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    trends: dict[str, Any] = field(default_factory=dict)
    critique: dict[str, Any] = field(default_factory=dict)
    report: dict[str, Any] = field(default_factory=dict)
    trace: list[dict[str, Any]] = field(default_factory=list)
