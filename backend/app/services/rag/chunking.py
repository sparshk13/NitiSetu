import re
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.services.rag.document_processor import ProcessedDocument

logger = logging.getLogger("nitisetu.rag.chunking")


class ChunkMetadata:
    def __init__(
        self,
        chunk_id: str,
        scheme_id: str,
        scheme_name: str,
        document_id: str,
        document_title: str,
        source_url: str,
        page_number: int,
        section_heading: str,
        category: str = "general",
        key_numbers: Optional[List[str]] = None,
        publication_date: Optional[str] = None,
        last_verified_at: Optional[str] = None,
        parent_chunk_id: Optional[str] = None,
        is_parent: bool = False
    ):
        self.chunk_id = chunk_id
        self.scheme_id = scheme_id
        self.scheme_name = scheme_name
        self.document_id = document_id
        self.document_title = document_title
        self.source_url = source_url
        self.page_number = page_number
        self.section_heading = section_heading
        self.category = category
        self.key_numbers = key_numbers or []
        self.publication_date = publication_date or "2024-01-01"
        self.last_verified_at = last_verified_at or datetime.now(timezone.utc).isoformat()
        self.parent_chunk_id = parent_chunk_id
        self.is_parent = is_parent


class UnifiedChunk:
    def __init__(
        self,
        content: str,
        metadata: ChunkMetadata
    ):
        self.content = content
        self.metadata = metadata
        # Normalized lexical tokens for BM25 / FTS
        self.words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]{3,}\b', content)]
        self.word_count = len(self.words)
        self.title_words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]{3,}\b', f"{metadata.document_title} {metadata.section_heading}")]

    @property
    def token_count(self) -> int:
        """Approximation of tokens based on whitespace and punctuation tokens."""
        return int(len(self.content.split()) * 1.3)


class StructureAwareChunker:
    """
    Structure-aware chunker supporting section boundary preservation,
    table integrity, and parent-child hierarchy.
    """

    def __init__(
        self,
        target_tokens: int = 650,
        overlap_tokens: int = 100,
        child_target_tokens: int = 180
    ):
        self.target_tokens = target_tokens
        self.overlap_tokens = overlap_tokens
        self.child_target_tokens = child_target_tokens

    @staticmethod
    def _categorize_section(title: str, text: str) -> str:
        title_l = title.lower()
        text_l = text.lower()

        # 1. Title-first categorization
        if any(k in title_l for k in ["exclusion", "ineligib", "disqualif", "bar", "prohibit"]):
            return "exclusions"
        if any(k in title_l for k in ["document", "checklist", "certificate", "paper", "proof"]):
            return "documents"
        if any(k in title_l for k in ["step", "procedure", "how to apply", "process", "portal"]):
            return "steps"
        if any(k in title_l for k in ["deadline", "timeline", "schedule", "last date"]):
            return "deadline"
        if any(k in title_l for k in ["income", "ceiling", "salary", "means", "creamy layer"]):
            return "income"
        if any(k in title_l for k in ["threshold", "limit"]) and any(k in text_l for k in ["income", "ceiling", "₹", "lakh"]):
            return "income"
        if any(k in title_l for k in ["benefit", "subsidy", "financial assistance", "allowance", "stipend", "cashless"]):
            return "benefits"
        if any(k in title_l for k in ["eligib", "criteria", "who can apply"]):
            if "income ceiling" in text_l or "family income" in text_l:
                return "income"
            return "eligibility"

        # 2. Body-text fallback
        combined = f"{title_l} {text_l}"
        if any(k in combined for k in ["tax payer", "institutional landholder", "exclusion", "excluded", "cannot apply", "disqualified", "not eligible", "dual scholarship"]):
            return "exclusions"
        if any(k in combined for k in ["income ceiling", "family income", "annual income", "annual limit"]):
            return "income"
        if any(k in combined for k in ["eligib", "criteria", "age limit", "cutoff", "qualify", "who can apply"]):
            return "eligibility"
        if any(k in combined for k in ["document", "certificate", "aadhaar", "marksheet", "bonafide"]):
            return "documents"
        if any(k in combined for k in ["benefit", "subsidy", "financial assistance", "allowance", "stipend"]):
            return "benefits"
        if any(k in combined for k in ["step", "procedure", "how to apply", "registration", "otr"]):
            return "steps"
        if any(k in combined for k in ["deadline", "last date", "due date", "closing date"]):
            return "deadline"

        return "general"

    def chunk_document(
        self,
        doc: ProcessedDocument
    ) -> Dict[str, List[UnifiedChunk]]:
        """
        Creates parent and child chunks preserving section and table boundaries.
        Returns a dict: {'parents': [...], 'children': [...]}
        """
        parent_chunks: List[UnifiedChunk] = []
        child_chunks: List[UnifiedChunk] = []

        for page in doc.pages:
            text = page.text.strip()
            if not text:
                continue

            # Split text by markdown headings (##, ###) while keeping tables and sections intact
            raw_sections = re.split(r'\n(?=##+\s+)', text)

            for sec_idx, sec in enumerate(raw_sections):
                sec_clean = sec.strip()
                if not sec_clean:
                    continue

                # Determine section heading
                lines = sec_clean.split("\n")
                first_line = lines[0].replace("#", "").strip()
                section_heading = first_line if first_line else f"Section {sec_idx + 1}"

                # Extract numerical figures
                key_numbers = list(dict.fromkeys(re.findall(r'₹\s*[\d,]+(?:\s*Lakh)?|\b\d+%\b|\b\d+\s*years?\b', sec_clean)))

                category = self._categorize_section(section_heading, sec_clean)
                parent_id = f"parent_{doc.doc_id}_{page.page_number}_{sec_idx}"

                parent_meta = ChunkMetadata(
                    chunk_id=parent_id,
                    scheme_id=doc.scheme_slug,
                    scheme_name=doc.title,
                    document_id=doc.doc_id,
                    document_title=doc.title,
                    source_url=doc.source_url,
                    page_number=page.page_number,
                    section_heading=section_heading,
                    category=category,
                    key_numbers=key_numbers,
                    is_parent=True
                )
                parent_chunk = UnifiedChunk(content=sec_clean, metadata=parent_meta)
                parent_chunks.append(parent_chunk)

                # Generate atomic child chunks (for fine-grained vector and keyword matching)
                # Split paragraphs or bullet points within section
                atomic_units = re.split(r'\n+[-*•]\s+|\n\d+\.\s+|\n\n+', sec_clean)
                child_buffer = []
                current_tokens = 0

                for unit in atomic_units:
                    unit_clean = unit.strip()
                    if len(unit_clean) < 15:
                        continue

                    unit_tokens = len(unit_clean.split())
                    if current_tokens + unit_tokens > self.child_target_tokens and child_buffer:
                        child_text = "\n".join(child_buffer)
                        child_id = f"child_{doc.doc_id}_{page.page_number}_{len(child_chunks)}"
                        child_meta = ChunkMetadata(
                            chunk_id=child_id,
                            scheme_id=doc.scheme_slug,
                            scheme_name=doc.title,
                            document_id=doc.doc_id,
                            document_title=doc.title,
                            source_url=doc.source_url,
                            page_number=page.page_number,
                            section_heading=section_heading,
                            category=category,
                            key_numbers=list(dict.fromkeys(re.findall(r'₹\s*[\d,]+(?:\s*Lakh)?|\b\d+%\b', child_text))),
                            parent_chunk_id=parent_id,
                            is_parent=False
                        )
                        child_chunks.append(UnifiedChunk(content=child_text, metadata=child_meta))
                        child_buffer = [unit_clean]
                        current_tokens = unit_tokens
                    else:
                        child_buffer.append(unit_clean)
                        current_tokens += unit_tokens

                # Flush trailing child buffer
                if child_buffer:
                    child_text = "\n".join(child_buffer)
                    child_id = f"child_{doc.doc_id}_{page.page_number}_{len(child_chunks)}"
                    child_meta = ChunkMetadata(
                        chunk_id=child_id,
                        scheme_id=doc.scheme_slug,
                        scheme_name=doc.title,
                        document_id=doc.doc_id,
                        document_title=doc.title,
                        source_url=doc.source_url,
                        page_number=page.page_number,
                        section_heading=section_heading,
                        category=category,
                        key_numbers=list(dict.fromkeys(re.findall(r'₹\s*[\d,]+(?:\s*Lakh)?|\b\d+%\b', child_text))),
                        parent_chunk_id=parent_id,
                        is_parent=False
                    )
                    child_chunks.append(UnifiedChunk(content=child_text, metadata=child_meta))

        return {
            "parents": parent_chunks,
            "children": child_chunks
        }


structure_aware_chunker = StructureAwareChunker()
