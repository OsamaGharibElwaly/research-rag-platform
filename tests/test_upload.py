"""Upload service tests."""
from backend.shared.auth import decode_token


class TestUploadHealth:
    def test_health_check(self, upload_client):
        response = upload_client.get("/health")
        assert response.status_code == 200
        assert response.json()["service"] == "upload_service"


class TestUpload:
    def test_successful_upload(self, upload_client, auth_headers, sample_pdf):
        response = upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("paper.pdf", sample_pdf, "application/pdf")},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["paper"]["original_filename"] == "paper.pdf"

    def test_invalid_file_type(self, upload_client, auth_headers):
        response = upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("notes.txt", b"hello", "text/plain")},
        )
        assert response.status_code == 400

    def test_file_too_large(self, upload_client, auth_headers, monkeypatch):
        monkeypatch.setattr(
            "backend.services.upload_service.services.MAX_FILE_SIZE_BYTES",
            10,
        )
        content = b"%PDF-1.4\n" + b"x" * 100
        response = upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("big.pdf", content, "application/pdf")},
        )
        assert response.status_code == 413

    def test_empty_upload(self, upload_client, auth_headers):
        response = upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert response.status_code == 400

    def test_missing_authentication(self, upload_client, sample_pdf):
        response = upload_client.post(
            "/upload",
            files={"file": ("paper.pdf", sample_pdf, "application/pdf")},
        )
        assert response.status_code in (401, 403)

    def test_metadata_saved_correctly(self, upload_client, auth_headers, sample_pdf):
        response = upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("research.pdf", sample_pdf, "application/pdf")},
        )
        paper = response.json()["data"]["paper"]
        token = auth_headers["Authorization"].split(" ", 1)[1]
        payload = decode_token(token)
        assert paper["content_type"] == "application/pdf"
        assert paper["file_size"] == len(sample_pdf)
        assert paper["user_id"] == int(payload["sub"])


class TestListPapers:
    def test_list_uploaded_papers(self, upload_client, auth_headers, sample_pdf):
        upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("one.pdf", sample_pdf, "application/pdf")},
        )
        response = upload_client.get("/papers", headers=auth_headers)
        assert response.status_code == 200
        papers = response.json()["data"]["papers"]
        assert len(papers) >= 1
        assert papers[0]["original_filename"] == "one.pdf"

    def test_list_requires_auth(self, upload_client):
        response = upload_client.get("/papers")
        assert response.status_code in (401, 403)


class TestDeletePaper:
    def test_delete_uploaded_paper(self, upload_client, auth_headers, sample_pdf):
        upload_response = upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("delete-me.pdf", sample_pdf, "application/pdf")},
        )
        paper_id = upload_response.json()["data"]["paper"]["id"]

        response = upload_client.delete(f"/paper/{paper_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["paper_id"] == paper_id

        list_response = upload_client.get("/papers", headers=auth_headers)
        ids = [paper["id"] for paper in list_response.json()["data"]["papers"]]
        assert paper_id not in ids

    def test_delete_non_existing_paper(self, upload_client, auth_headers):
        response = upload_client.delete("/paper/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_unauthorized_delete(self, upload_client, auth_headers, other_user_headers, sample_pdf):
        upload_response = upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("protected.pdf", sample_pdf, "application/pdf")},
        )
        paper_id = upload_response.json()["data"]["paper"]["id"]

        response = upload_client.delete(
            f"/paper/{paper_id}",
            headers=other_user_headers,
        )
        assert response.status_code == 403


class TestAPIResponseFormat:
    def test_validation_error_format(self, upload_client, auth_headers):
        response = upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("bad.exe", b"not-a-pdf", "application/octet-stream")},
        )
        assert response.status_code == 400
        body = response.json()
        assert "detail" in body

    def test_success_response_format(self, upload_client, auth_headers, sample_pdf):
        response = upload_client.post(
            "/upload",
            headers=auth_headers,
            files={"file": ("format.pdf", sample_pdf, "application/pdf")},
        )
        body = response.json()
        assert body["status"] == "success"
        assert "message" in body
        assert "data" in body
