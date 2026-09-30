from __future__ import annotations
from enum import Enum

class GapType(str, Enum):
    MISSING_DATASET = "missing_dataset"
    MISSING_EXPERIMENT = "missing_experiment"
    MISSING_EVALUATION = "missing_evaluation"
    UNDEREXPLORED_TOPIC = "underexplored_topic"
    MISSING_APPLICATION = "missing_application"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    FUTURE_WORK = "future_work"
