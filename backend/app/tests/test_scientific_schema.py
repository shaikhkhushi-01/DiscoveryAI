from app.schemas.scientific_extraction import ScientificDocument, ScientificEntities

def test_scientific_document_schema():
    doc=ScientificDocument(title="Test",entities=ScientificEntities(topics=["AI"],methods=["BERT"]))
    assert doc.entities.methods == ["BERT"]
    assert doc.year is None

def test_invalid_year_rejected():
    try:
        ScientificDocument(year=1800,entities=ScientificEntities())
        assert False
    except ValueError:
        assert True
