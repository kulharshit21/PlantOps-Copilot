from dataclasses import dataclass
from uuid import uuid5, NAMESPACE_URL

from app.core.security import CurrentUser
from app.schemas.documents import DocumentIngestRequest, DocumentIngestResponse, DocumentRead, RetrievedChunk
from app.services.chunking import TextChunker
from app.services.embeddings import EmbeddingProvider, MockEmbeddingProvider, cosine_similarity


@dataclass(frozen=True)
class StoredChunk:
    chunk: RetrievedChunk
    organization_id: str
    plant_id: str
    embedding: list[float]


class InMemoryDocumentStore:
    def __init__(
        self,
        *,
        chunker: TextChunker | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.chunker = chunker or TextChunker()
        self.embedding_provider = embedding_provider or MockEmbeddingProvider()
        self.documents: dict[str, DocumentRead] = {}
        self.chunks: list[StoredChunk] = []

    def ingest(self, request: DocumentIngestRequest, user: CurrentUser) -> DocumentIngestResponse:
        plant_id = request.plant_id or user.plant_id
        document_id = str(uuid5(NAMESPACE_URL, f"{user.organization_id}:{plant_id}:{request.title}"))
        source_uri = request.source_uri or f"seed://{document_id}"
        document = DocumentRead(
            id=document_id,
            title=request.title,
            document_type=request.document_type,
            plant_id=plant_id,
            source_uri=source_uri,
        )
        self.documents[document_id] = document

        created_chunks: list[RetrievedChunk] = []
        for text_chunk in self.chunker.chunk(request.content):
            chunk_id = str(uuid5(NAMESPACE_URL, f"{document_id}:{text_chunk.chunk_index}:{text_chunk.content[:80]}"))
            retrieved = RetrievedChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                title=request.title,
                content=text_chunk.content,
                source_uri=source_uri,
                source_page=text_chunk.source_page,
                score=None,
            )
            self.chunks.append(
                StoredChunk(
                    chunk=retrieved,
                    organization_id=user.organization_id,
                    plant_id=plant_id,
                    embedding=self.embedding_provider.embed(text_chunk.content),
                )
            )
            created_chunks.append(retrieved)

        return DocumentIngestResponse(
            document=document,
            chunk_count=len(created_chunks),
            chunks=created_chunks,
        )

    def list_documents(self, user: CurrentUser) -> list[DocumentRead]:
        return [
            document
            for document in self.documents.values()
            if document.plant_id == user.plant_id
        ]

    def search(self, *, query: str, user: CurrentUser, plant_id: str | None, top_k: int) -> list[RetrievedChunk]:
        scoped_plant_id = plant_id or user.plant_id
        query_embedding = self.embedding_provider.embed(query)
        scored: list[RetrievedChunk] = []
        for stored in self.chunks:
            if stored.organization_id != user.organization_id or stored.plant_id != scoped_plant_id:
                continue
            score = cosine_similarity(query_embedding, stored.embedding)
            scored.append(stored.chunk.model_copy(update={"score": round(score, 4)}))
        scored.sort(key=lambda chunk: chunk.score or 0, reverse=True)
        return scored[:top_k]


DOCUMENT_STORE = InMemoryDocumentStore()
