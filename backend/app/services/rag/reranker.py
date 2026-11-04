import re
from typing import List, Tuple
from backend.app.services.rag.chunking import UnifiedChunk


class Reranker:
    """
    Evaluates and reranks candidate chunks using cross-intent scoring,
    key numerical alignment, and statutory exclusion priorities.
    """

    def rerank(
        self,
        query: str,
        candidates: List[Tuple[UnifiedChunk, float]],
        intent: str,
        top_k: int = 4
    ) -> List[Tuple[UnifiedChunk, float]]:
        if not candidates:
            return []

        q_lower = query.lower()
        reranked = []

        for chunk, base_score in candidates:
            score = base_score
            c_text_lower = chunk.content.lower()

            # 1. Exact phrase match bonus
            if len(query) > 10 and query.lower() in c_text_lower:
                score += 0.05

            # 2. Key numerical alignment bonus
            # If user asks about an amount (e.g. "3.5 lakh" or "6000"), prioritize chunks with figures
            has_num_query = bool(re.search(r'₹|\d+\s*(?:lakh|lac|k|thousand|\d{3})', q_lower))
            if has_num_query and chunk.metadata.key_numbers:
                score += 0.03

            # 3. Category-Intent exact alignment
            if intent == chunk.metadata.category:
                score += 0.03
            elif intent == "income" and any(k in c_text_lower for k in ["income ceiling", "annual family income", "income limit", "₹2,50,000", "₹4,50,000"]):
                score += 0.04

            # 4. Exclusions priority
            if intent == "exclusions" and any(k in c_text_lower for k in ["exclusion", "ineligible", "prohibited", "tax", "dual"]):
                score += 0.04

            reranked.append((chunk, score))

        reranked.sort(key=lambda x: x[1], reverse=True)

        # Deduplicate sections
        seen = set()
        deduped = []
        for c, s in reranked:
            key = (c.metadata.scheme_id, c.metadata.section_heading.strip().lower())
            if key not in seen:
                seen.add(key)
                deduped.append((c, s))

        return (deduped if deduped else reranked)[:top_k]


reranker = Reranker()
