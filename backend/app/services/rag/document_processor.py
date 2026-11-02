import re
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import pymupdf

logger = logging.getLogger("nitisetu.rag.processor")


class ExtractedPage:
    def __init__(
        self,
        page_number: int,
        text: str,
        headings: Optional[List[str]] = None,
        tables: Optional[List[str]] = None,
        is_scanned: bool = False
    ):
        self.page_number = page_number
        self.text = text
        self.headings = headings or []
        self.tables = tables or []
        self.is_scanned = is_scanned


class ProcessedDocument:
    def __init__(
        self,
        doc_id: str,
        title: str,
        scheme_slug: str,
        source_url: str,
        pages: List[ExtractedPage],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.doc_id = doc_id
        self.title = title
        self.scheme_slug = scheme_slug
        self.source_url = source_url
        self.pages = pages
        self.metadata = metadata or {}


class DocumentProcessor:
    """
    Structure-aware document extractor utilizing PyMuPDF.
    Preserves page numbers, headings, tables, and numerical clauses while removing noise.
    """

    @staticmethod
    def _clean_page_text(raw_text: str) -> str:
        """Strip repetitive running headers, page footers, and redundant line noise."""
        lines = raw_text.split("\n")
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # Strip pure running page numbers e.g. "Page 3 of 12" or "- 3 -"
            if re.match(r'^(?:page\s+\d+(?:\s+of\s+\d+)?|-?\s*\d+\s*-?)$', stripped, re.IGNORECASE):
                continue
            # Strip recurring confidentiality / portal watermark footers
            if re.search(r'^\s*(?:confidential|draft notification|for internal use only)\s*$', stripped, re.IGNORECASE):
                continue
            cleaned_lines.append(line)
        cleaned = "\n".join(cleaned_lines)
        # Normalize excessive whitespace but preserve paragraph breaks
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        return cleaned.strip()

    def extract_from_pdf(
        self,
        source: Union[bytes, str, Path],
        title: str,
        scheme_slug: str,
        source_url: str,
        doc_id: Optional[str] = None
    ) -> ProcessedDocument:
        """Extract pages, headings, and tables from a text-based or mixed PDF using PyMuPDF."""
        doc_id = doc_id or str(uuid.uuid4())
        pages: List[ExtractedPage] = []

        try:
            if isinstance(source, (str, Path)):
                doc = pymupdf.open(str(source))
            else:
                doc = pymupdf.open(stream=source, filetype="pdf")

            for page_idx in range(len(doc)):
                page = doc[page_idx]
                page_num = page_idx + 1

                # 1. Extract markdown/text tables if PyMuPDF table finder is supported
                tables_md = []
                try:
                    table_finder = page.find_tables()
                    for t in table_finder:
                        df = t.extract()
                        if df and len(df) > 1:
                            headers = [str(c or '').strip() for c in df[0]]
                            rows = []
                            for row in df[1:]:
                                rows.append("| " + " | ".join(str(c or '').strip() for c in row) + " |")
                            table_md = "| " + " | ".join(headers) + " |\n| " + " | ".join(["---"] * len(headers)) + " |\n" + "\n".join(rows)
                            tables_md.append(table_md)
                except Exception as te:
                    logger.debug(f"Table finder notice on page {page_num}: {te}")

                # 2. Extract text blocks and detect font-size-based headings
                text_page = page.get_text("blocks")
                headings = []
                page_text_blocks = []

                for block in text_page:
                    if len(block) >= 5 and isinstance(block[4], str):
                        b_text = block[4].strip()
                        # Short single-line title block heuristic
                        if len(b_text) < 120 and "\n" not in b_text and not b_text.endswith("."):
                            if any(k in b_text.lower() for k in ["guideline", "eligib", "income", "criteria", "benefit", "document", "step", "rule", "section"]):
                                headings.append(b_text)
                        page_text_blocks.append(b_text)

                raw_text = "\n\n".join(page_text_blocks)
                cleaned_text = self._clean_page_text(raw_text)

                # Append any parsed tables into the page text if not already inline
                if tables_md:
                    cleaned_text += "\n\n### Official Data Tables\n" + "\n\n".join(tables_md)

                is_scanned = len(cleaned_text.strip()) < 30 and len(page.get_images()) > 0

                pages.append(ExtractedPage(
                    page_number=page_num,
                    text=cleaned_text,
                    headings=headings,
                    tables=tables_md,
                    is_scanned=is_scanned
                ))

            doc.close()
        except Exception as e:
            logger.error(f"Error extracting PDF for {title}: {e}")

        return ProcessedDocument(
            doc_id=doc_id,
            title=title,
            scheme_slug=scheme_slug,
            source_url=source_url,
            pages=pages,
            metadata={"source_type": "pdf", "total_pages": len(pages)}
        )

    def extract_from_markdown(
        self,
        content: str,
        title: str,
        scheme_slug: str,
        source_url: str,
        doc_id: Optional[str] = None
    ) -> ProcessedDocument:
        """Process structured markdown guidelines preserving section hierarchies."""
        doc_id = doc_id or str(uuid.uuid4())
        pages: List[ExtractedPage] = []

        # Split markdown by explicit page break comments if present, otherwise treat as page 1
        page_chunks = re.split(r'<!--\s*pagebreak\s*-->', content, flags=re.IGNORECASE)
        for idx, page_content in enumerate(page_chunks):
            headings = re.findall(r'^#+\s+(.+)$', page_content, flags=re.MULTILINE)
            # Find markdown tables
            tables = re.findall(r'(\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+)', page_content)

            pages.append(ExtractedPage(
                page_number=idx + 1,
                text=page_content.strip(),
                headings=headings,
                tables=tables,
                is_scanned=False
            ))

        return ProcessedDocument(
            doc_id=doc_id,
            title=title,
            scheme_slug=scheme_slug,
            source_url=source_url,
            pages=pages,
            metadata={"source_type": "markdown", "total_pages": len(pages)}
        )


document_processor = DocumentProcessor()
