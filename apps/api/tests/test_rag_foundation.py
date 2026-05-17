from app.core.security import CurrentUser, UserRole
from app.schemas.documents import DocumentIngestRequest
from app.services.chunking import TextChunker
from app.services.document_store import InMemoryDocumentStore
from app.services.embeddings import MockEmbeddingProvider


def test_chunker_preserves_citation_friendly_pages() -> None:
    text = (
        "Page 3\n"
        "Inspect spindle vibration before the next shift.\n\n"
        "Page 4\n"
        "Apply lockout tagout before opening guards."
    )

    chunks = TextChunker(max_chars=80, overlap_chars=10).chunk(text)

    assert len(chunks) >= 2
    assert chunks[0].source_page == 3
    assert "spindle vibration" in chunks[0].content


def test_document_ingest_creates_cited_chunks() -> None:
    user = CurrentUser(
        user_id="u1",
        email="u1@example.com",
        role=UserRole.supervisor,
        organization_id="org-a",
        plant_id="plant-a",
    )
    store = InMemoryDocumentStore(embedding_provider=MockEmbeddingProvider())

    response = store.ingest(
        DocumentIngestRequest(
            title="Spindle test SOP",
            document_type="sop",
            content="Page 1\nSpindle vibration and torque require bearing inspection.\n\nPage 2\nUse lockout tagout before inspection.",
            source_uri="seed://test/spindle",
        ),
        user,
    )

    assert response.chunk_count >= 1
    assert response.chunks[0].source_uri == "seed://test/spindle"
    assert response.chunks[0].document_id == response.document.id


def test_vector_search_filters_wrong_plant() -> None:
    user_a = CurrentUser(
        user_id="u1",
        email="u1@example.com",
        role=UserRole.supervisor,
        organization_id="org-a",
        plant_id="plant-a",
    )
    user_b = CurrentUser(
        user_id="u2",
        email="u2@example.com",
        role=UserRole.supervisor,
        organization_id="org-a",
        plant_id="plant-b",
    )
    store = InMemoryDocumentStore(embedding_provider=MockEmbeddingProvider())
    store.ingest(
        DocumentIngestRequest(
            title="Plant A spindle SOP",
            document_type="sop",
            plant_id="plant-a",
            content="Page 1\nSpindle vibration torque bearing inspection for Plant A only.",
        ),
        user_a,
    )

    allowed = store.search(query="spindle vibration", user=user_a, plant_id=None, top_k=3)
    denied = store.search(query="spindle vibration", user=user_b, plant_id=None, top_k=3)

    assert allowed
    assert denied == []
