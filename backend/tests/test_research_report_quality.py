from app.services.gap_detection.opportunity_report import _measurement_list
from app.services.graph_rag.fusion import fuse


def test_possible_measurements_are_normalized_from_serialized_list():
    assert _measurement_list("['Latency', 'Memory use', 'Latency']") == [
        "Latency", "Memory use"
    ]


def test_possible_measurements_preserve_json_arrays():
    assert _measurement_list(["Latency", "Memory use"]) == [
        "Latency", "Memory use"
    ]


def test_fusion_preserves_source_section_and_chunk_metadata():
    items = fuse(
        [{
            "paper_id": 7,
            "document_id": 12,
            "chunk_id": 3,
            "title": "Temporary PDF title",
            "section": "Experiments",
            "text": "A scientific excerpt.",
            "semantic_score": 0.9,
            "rerank_score": 0.8,
        }],
        [],
    )
    assert items[0]["section"] == "Experiments"
    assert items[0]["chunk_id"] == 3
    assert items[0]["document_id"] == 12
