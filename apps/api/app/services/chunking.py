from dataclasses import dataclass
import re


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    content: str
    source_page: int | None


class TextChunker:
    def __init__(self, max_chars: int = 900, overlap_chars: int = 120) -> None:
        if overlap_chars >= max_chars:
            raise ValueError("overlap_chars must be smaller than max_chars")
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars

    def chunk(self, text: str) -> list[TextChunk]:
        normalized = re.sub(r"\n{3,}", "\n\n", text.strip())
        if not normalized:
            return []

        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
        chunks: list[TextChunk] = []
        current = ""

        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
            if len(candidate) <= self.max_chars:
                current = candidate
                continue

            if current:
                chunks.append(TextChunk(len(chunks), current, self._infer_page(current)))
                current = self._tail(current)

            for segment in self._split_long_paragraph(paragraph):
                candidate = f"{current}\n\n{segment}".strip() if current else segment
                if len(candidate) > self.max_chars and current:
                    chunks.append(TextChunk(len(chunks), current, self._infer_page(current)))
                    current = segment
                else:
                    current = candidate

        if current:
            chunks.append(TextChunk(len(chunks), current, self._infer_page(current)))
        return chunks

    def _split_long_paragraph(self, paragraph: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        segments: list[str] = []
        current = ""
        for sentence in sentences:
            candidate = f"{current} {sentence}".strip() if current else sentence
            if len(candidate) <= self.max_chars:
                current = candidate
            else:
                if current:
                    segments.append(current)
                current = sentence
        if current:
            segments.append(current)
        return segments

    def _tail(self, text: str) -> str:
        if self.overlap_chars <= 0:
            return ""
        return text[-self.overlap_chars:].strip()

    def _infer_page(self, text: str) -> int | None:
        match = re.search(r"\bpage\s+(\d+)\b", text, flags=re.IGNORECASE)
        return int(match.group(1)) if match else None
