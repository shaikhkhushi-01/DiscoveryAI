from app.models import Application, Author, Dataset, Document, Experiment, Hypothesis, Institution, Method, Metric, Paper, Problem, ResearchGap, Topic

def test_scientific_model_tables():
    expected = {
        "papers": Paper, "documents": Document, "authors": Author, "institutions": Institution,
        "datasets": Dataset, "methods": Method, "topics": Topic, "problems": Problem,
        "applications": Application, "research_gaps": ResearchGap, "hypotheses": Hypothesis,
        "experiments": Experiment, "metrics": Metric,
    }
    for table, model in expected.items():
        assert model.__tablename__ == table

def test_scientific_models_have_primary_keys():
    for model in (Paper, Document, Author, Institution, Dataset, Method, Topic, Problem, Application, ResearchGap, Hypothesis, Experiment, Metric):
        assert model.__table__.primary_key.columns
