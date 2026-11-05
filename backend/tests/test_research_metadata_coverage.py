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
        "Attention Is All You Need\n\nAshish Vaswani, Noam Shazeer\n\nAbstract\nWe propose...",
        "real scientific research PDF",
        "5692a5514787a8c6727b4ff3b726a3385798bc68e12138d1d4af83947e2acf6e.pdf",
    ) == "Attention Is All You Need"


def test_publisher_permission_notice_is_skipped_when_inferring_title():
    extracted_text = (
        "Provided proper attribution is provided, Google hereby grants permission "
        "to reproduce the tables and figures in this paper solely for use in "
        "journalistic or scholarly works.\n"
        "Attention Is All You Need\n"
        "Ashish Vaswani, Noam Shazeer, Niki Parmar\n"
        "Abstract\nWe propose a new simple network architecture..."
    )
    assert infer_paper_title(extracted_text) == "Attention Is All You Need"


def test_publisher_permission_notice_is_not_a_usable_title():
    assert not is_usable_paper_title(
        "Provided proper attribution is provided, Google hereby grants permission "
        "to reproduce the tables and figures in this paper solely for use in "
        "journalistic or scholarly works."
    )


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


def test_existing_placeholder_paper_title_can_be_recovered_from_document_text():
    from app.services.gap_detection.research_critic import _canonical_paper_titles
    from app.models.paper import Paper
    from app.models.document import Document
    from app.db.session import SessionLocal
    from unittest.mock import patch

    class FakeQuery:
        def join(self, *args, **kwargs):
            return self
        def filter(self, *args, **kwargs):
            return self
        def all(self):
            return [(
                42,
                "real scientific research PDF",
                "Provided proper attribution is provided, Google hereby grants permission "
                "to reproduce the tables and figures in this paper solely for use in "
                "journalistic or scholarly works.\\nAttention Is All You Need\\n"
                "Ashish Vaswani, Noam Shazeer\\nAbstract\\nWe propose...",
                '{"metadata":{"title":"real scientific research PDF"}}',
                "/papers/5692a5514787a8c6727b4ff3b726a3385798bc68e12138d1d4af83947e2acf6e.pdf",
            )]
    class FakeSession:
        def query(self, *args):
            return FakeQuery()
        def close(self):
            pass

    with patch("app.services.gap_detection.research_critic.SessionLocal", return_value=FakeSession()):
        assert _canonical_paper_titles({42})[42] == "Attention Is All You Need"
