"""Parser service tests."""
import os
from pathlib import Path

import fitz
import pytest

from backend.services.parser_service.services.parser_service import ParserService
from backend.services.parser_service.utils.base_parser import BasePDFParser, ParsedDocument
from backend.services.upload_service.models import Paper


class TestParserHealth:
    def test_health_check(self, parser_client):
        response = parser_client.get("/health")
        assert response.status_code == 200
        assert response.json()["service"] == "parser_service"


class TestSuccessfulParsing:
    def test_successful_parsing(self, parser_client, auth_headers, uploaded_paper):
        response = parser_client.post(
            "/parse",
            headers=auth_headers,
            json={"paper_id": uploaded_paper["id"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Paper parsed successfully"
        assert data["data"]["paper_id"] == uploaded_paper["id"]
        assert data["data"]["pages"] >= 1
        assert len(data["data"]["text"]) > 0


class TestInvalidPaper:
    def test_invalid_paper_id(self, parser_client, auth_headers):
        response = parser_client.post(
            "/parse",
            headers=auth_headers,
            json={"paper_id": 99999},
        )
        assert response.status_code == 404


class TestAuthorization:
    def test_missing_authentication(self, parser_client, uploaded_paper):
        response = parser_client.post(
            "/parse",
            json={"paper_id": uploaded_paper["id"]},
        )
        assert response.status_code in (401, 403)

    def test_unauthorized_access(self, parser_client, other_user_headers, uploaded_paper):
        response = parser_client.post(
            "/parse",
            headers=other_user_headers,
            json={"paper_id": uploaded_paper["id"]},
        )
        assert response.status_code == 403


class TestMalformedPDFs:
    def test_corrupted_pdf(self, parser_client, auth_headers, tmp_path, current_user_id):
        upload_dir = tmp_path / "uploads" / str(current_user_id)
        upload_dir.mkdir(parents=True)
        bad_path = upload_dir / "bad.pdf"
        bad_path.write_bytes(b"not-a-real-pdf-content")

        db = __import__(
            "backend.services.parser_service.services.paper_access",
            fromlist=["UploadSessionLocal"],
        ).UploadSessionLocal()
        paper = Paper(
            user_id=current_user_id,
            filename="bad.pdf",
            original_filename="bad.pdf",
            file_path=str(bad_path),
            file_size=len(bad_path.read_bytes()),
            content_type="application/pdf",
        )
        db.add(paper)
        db.commit()
        paper_id = paper.id
        db.close()

        response = parser_client.post(
            "/parse",
            headers=auth_headers,
            json={"paper_id": paper_id},
        )
        assert response.status_code == 422

    def test_empty_pdf(self, parser_client, auth_headers, tmp_path, current_user_id):
        upload_dir = tmp_path / "uploads" / str(current_user_id)
        upload_dir.mkdir(parents=True)
        empty_path = upload_dir / "empty.pdf"
        empty_path.write_bytes(b"%PDF-1.4\n%%EOF")

        db = __import__(
            "backend.services.parser_service.services.paper_access",
            fromlist=["UploadSessionLocal"],
        ).UploadSessionLocal()
        paper = Paper(
            user_id=current_user_id,
            filename="empty.pdf",
            original_filename="empty.pdf",
            file_path=str(empty_path),
            file_size=empty_path.stat().st_size,
            content_type="application/pdf",
        )
        db.add(paper)
        db.commit()
        paper_id = paper.id
        db.close()

        response = parser_client.post(
            "/parse",
            headers=auth_headers,
            json={"paper_id": paper_id},
        )
        assert response.status_code == 422


class TestMetadataExtraction:
    def test_metadata_extraction(self, parser_client, auth_headers, uploaded_paper):
        response = parser_client.post(
            "/parse",
            headers=auth_headers,
            json={"paper_id": uploaded_paper["id"]},
        )
        result = response.json()["data"]
        assert "Neural Network Survey" in result["title"]
        assert isinstance(result["authors"], list)
        assert "abstract" in result
        assert isinstance(result["metadata"], dict)


class TestPageCount:
    def test_page_count(self, parser_client, auth_headers, upload_client, make_pdf):
        content, _ = make_pdf("multi.pdf", pages=3, title="Three Page Paper")
        upload_response = upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("multi.pdf", content, "application/pdf")},
        )
        paper_id = upload_response.json()["data"]["paper"]["id"]

        response = parser_client.post(
            "/parse",
            headers=auth_headers,
            json={"paper_id": paper_id},
        )
        assert response.json()["data"]["pages"] == 3


class TestLargePDF:
    def test_large_pdf(self, parser_client, auth_headers, upload_client, make_pdf):
        content, _ = make_pdf("large.pdf", pages=30, title="Large Paper", body="Content block.")
        upload_response = upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("large.pdf", content, "application/pdf")},
        )
        paper_id = upload_response.json()["data"]["paper"]["id"]

        response = parser_client.post(
            "/parse",
            headers=auth_headers,
            json={"paper_id": paper_id},
        )
        assert response.status_code == 200
        assert response.json()["data"]["pages"] == 30
        assert len(response.json()["data"]["text"]) > 0


class TestAPIResponseSchema:
    def test_api_response_schema(self, parser_client, auth_headers, uploaded_paper):
        response = parser_client.post(
            "/parse",
            headers=auth_headers,
            json={"paper_id": uploaded_paper["id"]},
        )
        body = response.json()
        assert body["status"] == "success"
        assert "message" in body
        data = body["data"]
        for field in ("paper_id", "title", "authors", "abstract", "pages", "metadata", "references", "text"):
            assert field in data


class TestErrorHandling:
    def test_invalid_request_body(self, parser_client, auth_headers):
        response = parser_client.post(
            "/parse",
            headers=auth_headers,
            json={"paper_id": 0},
        )
        assert response.status_code == 422

    def test_parser_service_is_swappable(self, tmp_path, make_pdf):
        pdf_bytes, pdf_path = make_pdf("swap.pdf", title="Swappable Parser")

        class StubParser(BasePDFParser):
            def parse(self, file_path: str) -> ParsedDocument:
                return ParsedDocument(
                    title="Stub Title",
                    authors=["Stub Author"],
                    abstract="Stub abstract",
                    pages=1,
                    metadata={"source": "stub"},
                    references=["Ref 1"],
                    text="Stub text",
                )

        service = ParserService(parser=StubParser())
        result = service.parse_pdf(pdf_path)
        assert result.title == "Stub Title"
        assert result.authors == ["Stub Author"]
