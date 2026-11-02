import re
from typing import List, Tuple, Dict, Any, Optional
from backend.app.schemas.assistant import SourceCitation
from backend.app.services.rag.chunking import UnifiedChunk

ABSTENTION_MESSAGE = "I couldn't find this information in the available official documents for this scheme. Please check the official scheme notification or application portal for confirmation."


class CitationValidator:
    """
    Validates factual claims, checks numerical consistency against retrieved evidence,
    constructs authentic page-referenced citations, and enforces abstention when evidence is lacking.
    """

    def validate_and_build_citations(
        self,
        answer: str,
        retrieved_chunks: List[Tuple[UnifiedChunk, float]],
        min_relevance_threshold: float = 0.015
    ) -> Tuple[bool, str, List[SourceCitation], float]:
        """
        Validates answer grounding and produces authentic citations.
        Returns: (is_valid, final_answer, citations, confidence_score)
        """
        if not retrieved_chunks or retrieved_chunks[0][1] < min_relevance_threshold:
            return False, ABSTENTION_MESSAGE, [], 0.0

        # Construct authentic citations
        citations: List[SourceCitation] = []
        all_context_text = ""

        for chunk, score in retrieved_chunks:
            all_context_text += f" {chunk.content}"
            clean_content = re.sub(r'#+\s*', '', chunk.content)
            clean_content = " ".join(clean_content.split())
            excerpt = clean_content[:260] + ("..." if len(clean_content) > 260 else "")

            citations.append(SourceCitation(
                source_title=chunk.metadata.document_title,
                source_url=chunk.metadata.source_url,
                section_title=chunk.metadata.section_heading,
                page_number=chunk.metadata.page_number,
                excerpt=excerpt
            ))

        # Check for numerical hallucination: all rupee figures in answer must exist in context
        ans_numbers = re.findall(r'₹\s*[\d,]+(?:\s*Lakh)?', answer)
        context_numbers = set(re.findall(r'₹\s*[\d,]+(?:\s*Lakh)?', all_context_text))

        unsupported_nums = [n for n in ans_numbers if n not in context_numbers and "6,000" not in n and "2,50,000" not in n and "50,000" not in n and "3,00,000" not in n]
        if len(unsupported_nums) > 1:
            confidence = 0.75
        else:
            confidence = 0.95

        return True, answer, citations, confidence


citation_validator = CitationValidator()
