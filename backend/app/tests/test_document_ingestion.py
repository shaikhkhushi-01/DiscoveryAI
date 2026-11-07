from app.services.document_ingestion import checksum, clean_text, detect_sections, validate_pdf, DocumentIngestionError

def test_pdf_validation():
    validate_pdf(b"%PDF-1.7 fake", "paper.pdf", "application/pdf")
    try:
        validate_pdf(b"not-pdf", "paper.pdf", "application/pdf")
        assert False
    except DocumentIngestionError:
        assert True

def test_checksum_is_stable():
    assert checksum(b"abc") == checksum(b"abc")
    assert checksum(b"abc") != checksum(b"abd")

def test_text_cleaning_and_sections():
    text = "Abstract\nA  test\n\n\n1 Introduction\nBody"
    cleaned = clean_text(text)
    sections = detect_sections(cleaned)
    assert "A test" in cleaned
    assert any(s["type"] == "abstract" for s in sections)
    assert any(s["type"] == "introduction" for s in sections)

def test_text_cleaning_removes_nul_and_control_characters():
    cleaned = clean_text("Title" + chr(0) + chr(1) + chr(10) + "Body" + chr(0))
    assert cleaned == "Title" + chr(10) + "Body"
    assert chr(0) not in cleaned
