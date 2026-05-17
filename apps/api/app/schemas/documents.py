from pydantic import BaseModel, Field


class DocumentRead(BaseModel):
    id: str
    title: str
    document_type: str
    plant_id: str


class RagAskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    plant_id: str | None = None
    top_k: int = Field(default=4, ge=1, le=10)


class RetrievedChunk(BaseModel):
    chunk_id: str
    title: str
    content: str
    source_uri: str
    source_page: int | None = None


class RagAskResponse(BaseModel):
    answer: str
    citations: list[RetrievedChunk]
    retrieved_chunks: list[RetrievedChunk]
    model_used: str
    fallback_used: bool
    confidence_notes: str
