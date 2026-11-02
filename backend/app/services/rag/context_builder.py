from typing import List, Tuple
from backend.app.services.rag.chunking import UnifiedChunk


class ContextBuilder:
    """Formats and bounds retrieved chunks into clean, cited LLM context."""

    def build_context(
        self,
        ranked_chunks: List[Tuple[UnifiedChunk, float]],
        max_words: int = 1500
    ) -> str:
        if not ranked_chunks:
            return ""

        context_parts = []
        total_words = 0
        seen_contents = set()

        for chunk, score in ranked_chunks:
            # Dedup exact chunks
            content_norm = " ".join(chunk.content.split())
            if content_norm in seen_contents:
                continue
            seen_contents.add(content_norm)

            chunk_words = len(content_norm.split())
            if total_words + chunk_words > max_words and context_parts:
                break

            header = f"[{chunk.metadata.document_title} | Page {chunk.metadata.page_number} | Section: {chunk.metadata.section_heading}]"
            context_parts.append(f"{header}\n{chunk.content}")
            total_words += chunk_words

        return "\n\n---\n\n".join(context_parts)


context_builder = ContextBuilder()
