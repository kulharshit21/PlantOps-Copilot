from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    api_root = Path(__file__).resolve().parents[2] / "apps" / "api"
    sys.path.insert(0, str(api_root))

    from app.core.security import DEMO_USER
    from app.schemas.documents import RagAskRequest
    from app.services.rag import RagService

    response = RagService().ask(
        RagAskRequest(question="What should next shift do for spindle vibration?", top_k=3),
        DEMO_USER,
    )
    if not response.citations:
        print("FAIL: RAG response did not include citations")
        return 1
    print(f"PASS: RAG returned {len(response.citations)} citation(s), model={response.model_used}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
