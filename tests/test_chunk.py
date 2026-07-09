"""Chunk service tests."""
from backend.services.chunk_service.services.chunk_service import ChunkService
from backend.services.chunk_service.utils.base_chunker import BaseChunker, ChunkConfig, TextChunk


class TestChunkHealth:
    def test_health_check(self, chunk_client):
        response = chunk_client.get("/health")
        assert response.status_code == 200
        assert response.json()["service"] == "chunk_service"


class TestSuccessfulChunking:
    def test_successful_chunk_generation(self, chunk_client, auth_headers, parsed_paper):
        response = chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={"paper_id": parsed_paper["id"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Chunks generated successfully"
        assert data["data"]["paper_id"] == parsed_paper["id"]
        assert data["data"]["chunks_created"] >= 1
        assert data["data"]["average_chunk_size"] > 0


class TestAuthorization:
    def test_unauthorized_user(self, chunk_client, parsed_paper):
        response = chunk_client.post(
            "/chunk",
            json={"paper_id": parsed_paper["id"]},
        )
        assert response.status_code in (401, 403)

    def test_ownership_validation(self, chunk_client, other_user_headers, parsed_paper):
        response = chunk_client.post(
            "/chunk",
            headers=other_user_headers,
            json={"paper_id": parsed_paper["id"]},
        )
        assert response.status_code == 403


class TestInvalidPaper:
    def test_invalid_paper(self, chunk_client, auth_headers):
        response = chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={"paper_id": 99999},
        )
        assert response.status_code == 404


class TestEmptyParsedText:
    def test_empty_parsed_text(self, chunk_client, auth_headers, uploaded_paper, current_user_id, seed_parse_result):
        seed_parse_result(uploaded_paper["id"], current_user_id, "")

        response = chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={"paper_id": uploaded_paper["id"]},
        )
        assert response.status_code == 422


class TestLargeDocument:
    def test_very_large_document(self, chunk_client, auth_headers, uploaded_paper, current_user_id, seed_parse_result):
        large_text = "Paragraph about machine learning. " * 2000
        seed_parse_result(uploaded_paper["id"], current_user_id, large_text, pages=50)

        response = chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={"paper_id": uploaded_paper["id"]},
        )
        assert response.status_code == 200
        assert response.json()["data"]["chunks_created"] > 10


class TestChunkOverlap:
    def test_chunk_overlap_correctness(self):
        text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
        service = ChunkService()
        config = ChunkConfig(chunk_size=30, chunk_overlap=10, minimum_chunk_length=5)
        chunks = service.generate_chunks(text, config)
        assert len(chunks) >= 2
        assert chunks[1].start_offset < chunks[0].end_offset


class TestChunkOrdering:
    def test_chunk_ordering(self, chunk_client, auth_headers, parsed_paper, get_stored_chunks):
        chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={"paper_id": parsed_paper["id"]},
        )
        stored = get_stored_chunks(parsed_paper["id"])
        indexes = [chunk.chunk_index for chunk in stored]
        assert indexes == list(range(len(stored)))


class TestChunkMetadata:
    def test_chunk_metadata(self, chunk_client, auth_headers, parsed_paper, get_stored_chunks):
        chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={"paper_id": parsed_paper["id"]},
        )
        stored = get_stored_chunks(parsed_paper["id"])
        assert stored
        chunk = stored[0]
        assert chunk.paper_id == parsed_paper["id"]
        assert chunk.chunk_text
        assert chunk.start_offset >= 0
        assert chunk.end_offset > chunk.start_offset
        assert chunk.chunk_length == len(chunk.chunk_text)


class TestAPIResponseSchema:
    def test_api_response_schema(self, chunk_client, auth_headers, parsed_paper):
        response = chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={"paper_id": parsed_paper["id"]},
        )
        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        for field in (
            "paper_id",
            "chunks_created",
            "average_chunk_size",
            "largest_chunk",
            "smallest_chunk",
            "first_chunk",
            "last_chunk",
        ):
            assert field in data


class TestErrorHandling:
    def test_invalid_request_body(self, chunk_client, auth_headers):
        response = chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={"paper_id": 0},
        )
        assert response.status_code == 422

    def test_chunk_service_is_swappable(self):
        class StubChunker(BaseChunker):
            def chunk(self, text: str, config: ChunkConfig) -> list[TextChunk]:
                return [
                    TextChunk(
                        chunk_index=0,
                        chunk_text="stub",
                        start_offset=0,
                        end_offset=4,
                        chunk_length=4,
                    )
                ]

        service = ChunkService(chunker=StubChunker())
        chunks = service.generate_chunks("any text", ChunkConfig())
        assert chunks[0].chunk_text == "stub"


class TestConfigurationOverride:
    def test_configuration_override(self, chunk_client, auth_headers, parsed_paper):
        small = chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={
                "paper_id": parsed_paper["id"],
                "config": {
                    "chunk_size": 80,
                    "chunk_overlap": 10,
                    "separators": ["\n\n", "\n", ". ", " "],
                    "minimum_chunk_length": 5,
                },
            },
        )
        large = chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={
                "paper_id": parsed_paper["id"],
                "config": {
                    "chunk_size": 5000,
                    "chunk_overlap": 0,
                    "separators": ["\n\n", "\n", ". ", " "],
                    "minimum_chunk_length": 5,
                },
            },
        )
        assert small.json()["data"]["chunks_created"] >= large.json()["data"]["chunks_created"]


class TestChunkBoundaries:
    def test_chunk_boundaries(self):
        text = "wordone wordtwo. wordthree wordfour."
        service = ChunkService()
        config = ChunkConfig(chunk_size=25, chunk_overlap=5, minimum_chunk_length=5)
        chunks = service.generate_chunks(text, config)
        for chunk in chunks:
            assert " " in chunk.chunk_text or len(chunk.chunk_text) <= config.chunk_size


class TestDeterministicChunking:
    def test_deterministic_chunking(self, chunk_client, auth_headers, parsed_paper, get_stored_chunks):
        first = chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={"paper_id": parsed_paper["id"]},
        )
        first_chunks = [chunk.chunk_text for chunk in get_stored_chunks(parsed_paper["id"])]

        second = chunk_client.post(
            "/chunk",
            headers=auth_headers,
            json={"paper_id": parsed_paper["id"]},
        )
        second_chunks = [chunk.chunk_text for chunk in get_stored_chunks(parsed_paper["id"])]

        assert first.status_code == 200
        assert second.status_code == 200
        assert first_chunks == second_chunks
