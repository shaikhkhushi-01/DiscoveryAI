"""Import and finalize all SQLAlchemy models before the application starts."""

from sqlalchemy.orm import configure_mappers

from app.models.application import Application
from app.models.author import Author
from app.models.dataset import Dataset
from app.models.document import Document
from app.models.experiment import Experiment
from app.models.hypothesis import Hypothesis
from app.models.indexing_job import IndexingJob
from app.models.institution import Institution
from app.models.metric import Metric
from app.models.method import Method
from app.models.paper import Paper
from app.models.problem import Problem
from app.models.research_gap import ResearchGap
from app.models.topic import Topic

configure_mappers()

__all__ = [
    "Application", "Author", "Dataset", "Document", "Experiment",
    "Hypothesis", "IndexingJob", "Institution", "Metric", "Method", "Paper",
    "Problem", "ResearchGap", "Topic",
]
