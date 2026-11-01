from unittest.mock import patch


def test_gap_type_values():
    from app.services.gap_detection.types import GapType

    assert GapType.MISSING_DATASET.value == "missing_dataset"
    assert GapType.MISSING_EXPERIMENT.value == "missing_experiment"


@patch("app.services.gap_detection.validator.retrieve_graph_rag")
def test_candidate_validation_is_scope_aware(mock_retrieve):
    mock_retrieve.return_value = {"items": []}
    from app.services.gap_detection.validator import validate_candidate

    result = validate_candidate({"title": "candidate", "gap_type": "underexplored_topic", "evidence_count": 1})
    assert result["status"] == "weak_candidate"
    assert "indexed corpus" in result["validation_note"]


@patch("app.services.gap_detection.candidates.run")
def test_missing_experiment_query_joins_method_and_dataset_through_same_paper(mock_run):
    from app.services.gap_detection.candidates import _missing_experiments

    mock_run.return_value = []
    _missing_experiments()

    query = mock_run.call_args.args[0]
    assert "OPTIONAL MATCH (p:Paper)-[:USES_METHOD]->(m), (p)-[:USES_DATASET]->(d)" in query
    assert "AS evidence_count" in query
