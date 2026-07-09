"""Abstract PDF parser interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParsedDocument:
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    pages: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    references: list[str] = field(default_factory=list)
    text: str = ""


class BasePDFParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> ParsedDocument:
        """Parse a PDF file and return structured content."""
