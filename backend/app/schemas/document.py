from pydantic import BaseModel, ConfigDict

class DocumentUploadResponse(BaseModel):
    id: int
    paper_id: int
    filename: str
    checksum: str
    status: str
    page_count: int | None

class ParsedDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    document_id: int
    page_count: int
    metadata: dict
    sections: list[dict]
    references: list[dict]
    tables: list[dict]
    figures: list[dict]
    chunks: list[dict]
