from pydantic import BaseModel, Field


class DocumentRead(BaseModel):
    id: str
    title: str
    document_type: str
    plant_id: str
    source_uri: str | None = None


class DocumentIngestRequest(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    document_type: str = Field(pattern="^(sop|manual|work_order|safety|other)$")
    content: str = Field(min_length=20, max_length=100_000)
    plant_id: str | None = None
    source_uri: str | None = Field(default=None, max_length=500)


class DocumentIngestResponse(BaseModel):
    document: DocumentRead
    chunk_count: int
    chunks: list["RetrievedChunk"]


class RagAskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    plant_id: str | None = None
    top_k: int = Field(default=4, ge=1, le=10)


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str | None = None
    title: str
    content: str
    source_uri: str
    source_page: int | None = None
    score: float | None = None


class RagAskResponse(BaseModel):
    answer: str
    recommendation: str
    urgency: str
    next_steps: list[str]
    citations: list[RetrievedChunk]
    retrieved_chunks: list[RetrievedChunk]
    model_used: str
    fallback_used: bool
    confidence_notes: str
