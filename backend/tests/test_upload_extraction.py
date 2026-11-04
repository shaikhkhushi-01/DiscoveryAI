from app.api.documents import build_scientific_extraction


def test_build_scientific_extraction_creates_indexer_contract():
    result = build_scientific_extraction(
        "Paper text includes DOI 10.1234/example. The model uses masked language modeling.",
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "author": "Jacob Devlin; Ming-Wei Chang",
            "creationDate": "D:20181011",
        },
        {"topics": ["language representation"], "methods": ["masked language modeling"]},
        "bert.pdf",
        [{"type": "abstract", "text": "We introduce BERT."}],
    )

    assert result["title"].startswith("BERT")
    assert result["authors"] == ["Jacob Devlin", "Ming-Wei Chang"]
    assert result["year"] == 2018
    assert result["doi"] == "10.1234/example"
    assert result["abstract"] == "We introduce BERT."
    assert result["topics"] == ["language representation"]
    assert result["methods"] == ["masked language modeling"]


def test_build_scientific_extraction_uses_filename_without_pdf_title():
    result = build_scientific_extraction(
        "No DOI in this paper.",
        {},
        {},
        "research-paper.pdf",
    )

    assert result["title"] == "research-paper"
    assert result["doi"] is None
    assert result["year"] is None
    assert result["abstract"] is None
    assert result["topics"] == []
