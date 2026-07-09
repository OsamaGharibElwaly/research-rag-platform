"""Parser service Pydantic schemas."""
from typing import Any

from pydantic import BaseModel, Field


class ParseRequest(BaseModel):
    paper_id: int = Field(..., gt=0)


class ParseResultData(BaseModel):
    paper_id: int
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    pages: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    references: list[str] = Field(default_factory=list)
    text: str = ""
    status: str = "completed"


class ParseResultResponse(BaseModel):
    paper_id: int
    title: str
    authors: list[str]
    abstract: str
    pages: int
    metadata: dict[str, Any]
    references: list[str]
    text: str
