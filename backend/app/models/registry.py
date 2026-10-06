"""Import all SQLAlchemy models so their mappers share one registry."""

from app.models.application import Application
from app.models.author import Author
from app.models.dataset import Dataset
from app.models.document import Document
from app.models.experiment import Experiment
from app.models.hypothesis import Hypothesis
from app.models.institution import Institution
from app.models.metric import Metric
from app.models.method import Method
from app.models.paper import Paper
from app.models.problem import Problem
from app.models.research_gap import ResearchGap
from app.models.topic import Topic

__all__ = [
    "Application",
    "Author",
    "Dataset",
    "Document",
    "Experiment",
    "Hypothesis",
    "Institution",
    "Metric",
    "Method",
    "Paper",
    "Problem",
    "ResearchGap",
    "Topic",
]
