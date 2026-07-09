"""Core PDF parsing service."""
from backend.services.parser_service.utils.base_parser import BasePDFParser, ParsedDocument
from backend.services.parser_service.utils.pymupdf_parser import PyMuPDFParser
from backend.shared.logger import get_logger

logger = get_logger("parser_service")


class ParserService:
    def __init__(self, parser: BasePDFParser | None = None):
        self._parser = parser or PyMuPDFParser()

    def parse_pdf(self, file_path: str) -> ParsedDocument:
        logger.info(f"Parsing PDF: {file_path}")
        try:
            return self._parser.parse(file_path)
        except Exception as exc:
            logger.error(f"Failed to parse PDF {file_path}: {exc}")
            raise ValueError(f"Failed to parse PDF: {exc}") from exc
