from app.services.gap_detection.opportunity_report import _measurement_list
from app.services.graph_rag.fusion import fuse
from app.services.extraction import infer_paper_title, is_usable_paper_title


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



def test_placeholder_pdf_metadata_does_not_override_scientific_title():
    assert infer_paper_title(
        "Attention Is All You Need\\n\\nAshish Vaswani, Noam Shazeer\\n\\nAbstract\\nWe propose...",
        "real scientific research PDF",
        "5692a5514787a8c6727b4ff3b726a3385798bc68e12138d1d4af83947e2acf6e.pdf",
    ) == "Attention Is All You Need"


def test_checksum_and_filename_are_not_accepted_as_paper_titles():
    assert not is_usable_paper_title("5692a5514787a8c6727b4ff3b726a3385798bc68e12138d1d4af83947e2acf6e")
    assert not is_usable_paper_title("my-upload.pdf", "my-upload.pdf")


def test_fusion_keeps_multiple_chunks_from_the_same_paper():
    items = fuse(
        [
            {"paper_id": 7, "document_id": 12, "chunk_id": "intro-1", "text": "Introduction evidence", "semantic_score": 0.9, "rerank_score": 0.8},
            {"paper_id": 7, "document_id": 12, "chunk_id": "methods-2", "text": "Methods evidence", "semantic_score": 0.8, "rerank_score": 0.7},
        ],
        [],
    )
    assert len(items) == 2
    assert {item["chunk_id"] for item in items} == {"intro-1", "methods-2"}
