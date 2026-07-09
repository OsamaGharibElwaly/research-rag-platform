"""PyMuPDF-based PDF parser implementation."""
import fitz

from backend.services.parser_service.utils.base_parser import BasePDFParser, ParsedDocument
from backend.services.parser_service.utils.metadata_extractor import (
    extract_abstract,
    extract_authors,
    extract_references,
    extract_title,
)
from backend.services.parser_service.utils.text_cleaner import clean_text


class PyMuPDFParser(BasePDFParser):
    def parse(self, file_path: str) -> ParsedDocument:
        doc = fitz.open(file_path)
        try:
            if doc.page_count == 0:
                raise ValueError("PDF has no pages")

            page_texts: list[str] = []
            for page in doc:
                page_texts.append(page.get_text("text"))

            raw_text = "\n".join(page_texts)
            cleaned = clean_text(raw_text)
            meta = doc.metadata or {}

            title = extract_title(cleaned, meta.get("title"))
            authors = extract_authors(cleaned, meta.get("author"))
            abstract = extract_abstract(cleaned)
            references = extract_references(cleaned)

            metadata = {
                "producer": meta.get("producer") or "",
                "creator": meta.get("creator") or "",
                "format": meta.get("format") or "",
                "encryption": meta.get("encryption") or "",
            }

            return ParsedDocument(
                title=title,
                authors=authors,
                abstract=abstract,
                pages=doc.page_count,
                metadata=metadata,
                references=references,
                text=cleaned,
            )
        finally:
            doc.close()
