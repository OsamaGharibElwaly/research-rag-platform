"""Heuristic metadata extraction from raw PDF text."""
import re


def extract_title(text: str, metadata_title: str | None = None) -> str:
    if metadata_title and metadata_title.strip():
        return metadata_title.strip()

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:8]:
        if 8 <= len(line) <= 200 and not line.lower().startswith("abstract"):
            return line
    return ""


def extract_authors(text: str, metadata_author: str | None = None) -> list[str]:
    if metadata_author and metadata_author.strip():
        return [part.strip() for part in re.split(r"[,;]", metadata_author) if part.strip()]

    match = re.search(r"(?im)^authors?\s*[:\-]\s*(.+)$", text)
    if match:
        return [part.strip() for part in re.split(r"[,;]", match.group(1)) if part.strip()]

    return []


def extract_abstract(text: str) -> str:
    match = re.search(
        r"(?is)\babstract\b\s*[:\-]?\s*(.+?)(?:\n\s*(?:keywords|introduction|1\.?\s+introduction)\b)",
        text,
    )
    if match:
        return re.sub(r"\s+", " ", match.group(1)).strip()
    return ""


def extract_references(text: str) -> list[str]:
    match = re.search(r"(?is)\breferences\b\s*(.+)$", text)
    if not match:
        return []

    block = match.group(1).strip()
    refs = []
    for line in block.split("\n"):
        cleaned = line.strip()
        if len(cleaned) > 20:
            refs.append(cleaned)
    return refs[:200]
