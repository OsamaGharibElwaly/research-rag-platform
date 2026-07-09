"""Embedding service tests."""
from backend.services.embedding_service.services.embedding_service import EmbeddingService
from backend.services.embedding_service.utils.base_provider import BaseEmbeddingProvider


class StubEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = "test/stub-model", dimension: int = 8):
        self._model_name = model_name
        self._dimension = dimension
        self.embed_calls: list[list[str]] = []

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.embed_calls.append(list(texts))
        vectors = []
        for text in texts:
            seed = sum(ord(char) for char in text) % 1000
            base = (seed % self._dimension) / 100.0
            vectors.append([base + index * 0.01 for index in range(self._dimension)])
        return vectors


class TestEmbeddingHealth:
    def test_health_check(self, embedding_client):
        response = embedding_client.get("/health")
        assert response.status_code == 200
        assert response.json()["service"] == "embedding_service"


class TestSuccessfulEmbedding:
    def test_successful_embedding_generation(
        self, embedding_client, auth_headers, chunked_paper, get_stored_embeddings
    ):
        response = embedding_client.post(
            "/embed",
            headers=auth_headers,
            json={"paper_id": chunked_paper["id"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Embeddings generated successfully"
        assert data["data"]["paper_id"] == chunked_paper["id"]
        assert data["data"]["chunks_embedded"] >= 1
        assert data["data"]["embedding_dimension"] == 8
        assert data["data"]["model"] == "test/stub-model"
        assert data["data"]["processing_time_ms"] >= 0

        stored = get_stored_embeddings(chunked_paper["id"])
        assert len(stored) == data["data"]["chunks_embedded"]


class TestAuthorization:
    def test_unauthorized_access(self, embedding_client, chunked_paper):
        response = embedding_client.post(
            "/embed",
            json={"paper_id": chunked_paper["id"]},
        )
        assert response.status_code in (401, 403)

    def test_ownership_validation(self, embedding_client, other_user_headers, chunked_paper):
        response = embedding_client.post(
            "/embed",
            headers=other_user_headers,
            json={"paper_id": chunked_paper["id"]},
        )
        assert response.status_code == 403


class TestInvalidPaper:
    def test_invalid_paper(self, embedding_client, auth_headers):
        response = embedding_client.post(
            "/embed",
            headers=auth_headers,
            json={"paper_id": 99999},
        )
        assert response.status_code == 404


class TestMissingChunks:
    def test_missing_chunks(self, embedding_client, auth_headers, parsed_paper):
        response = embedding_client.post(
            "/embed",
            headers=auth_headers,
            json={"paper_id": parsed_paper["id"]},
        )
        assert response.status_code == 404


class TestDuplicateEmbeddingPrevention:
    def test_duplicate_embedding_prevention(
        self, embedding_client, auth_headers, chunked_paper, get_stored_embeddings
    ):
        first = embedding_client.post(
            "/embed",
            headers=auth_headers,
            json={"paper_id": chunked_paper["id"]},
        )
        second = embedding_client.post(
            "/embed",
            headers=auth_headers,
            json={"paper_id": chunked_paper["id"]},
        )
        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json()["data"]["chunks_embedded"] >= 1
        assert second.json()["data"]["chunks_embedded"] == 0

        stored = get_stored_embeddings(chunked_paper["id"])
        assert len(stored) == first.json()["data"]["chunks_embedded"]


class TestBatchProcessing:
    def test_batch_processing(
        self, embedding_client, auth_headers, chunked_paper, stub_embedding_provider
    ):
        embedding_client.post(
            "/embed",
            headers=auth_headers,
            json={"paper_id": chunked_paper["id"]},
        )
        assert stub_embedding_provider.embed_calls
        total_texts = sum(len(batch) for batch in stub_embedding_provider.embed_calls)
        assert total_texts >= 1


class TestStoredDimensions:
    def test_stored_dimensions(self, embedding_client, auth_headers, chunked_paper, get_stored_embeddings):
        embedding_client.post(
            "/embed",
            headers=auth_headers,
            json={"paper_id": chunked_paper["id"]},
        )
        stored = get_stored_embeddings(chunked_paper["id"])
        assert stored
        for record in stored:
            assert record.embedding_dimension == 8
            assert len(record.get_vector()) == 8


class TestStoredModel:
    def test_stored_model(self, embedding_client, auth_headers, chunked_paper, get_stored_embeddings):
        embedding_client.post(
            "/embed",
            headers=auth_headers,
            json={"paper_id": chunked_paper["id"]},
        )
        stored = get_stored_embeddings(chunked_paper["id"], model_name="test/stub-model")
        assert stored
        assert all(record.embedding_model == "test/stub-model" for record in stored)


class TestAPIResponseSchema:
    def test_api_response_schema(self, embedding_client, auth_headers, chunked_paper):
        response = embedding_client.post(
            "/embed",
            headers=auth_headers,
            json={"paper_id": chunked_paper["id"]},
        )
        body = response.json()
        assert body["status"] == "success"
        data = body["data"]
        for field in (
            "paper_id",
            "chunks_embedded",
            "embedding_dimension",
            "model",
            "processing_time_ms",
        ):
            assert field in data


class TestErrorHandling:
    def test_invalid_request_body(self, embedding_client, auth_headers):
        response = embedding_client.post(
            "/embed",
            headers=auth_headers,
            json={"paper_id": 0},
        )
        assert response.status_code == 422


class TestProviderAbstraction:
    def test_provider_is_swappable(self):
        provider = StubEmbeddingProvider(dimension=4)
        service = EmbeddingService(provider)
        vectors = service.embed_texts(["alpha", "beta"], batch_size=1)
        assert len(vectors) == 2
        assert len(vectors[0]) == 4

    def test_embedding_service_batch_size(self):
        provider = StubEmbeddingProvider(dimension=3)
        service = EmbeddingService(provider)
        texts = [f"text-{index}" for index in range(5)]
        service.embed_texts(texts, batch_size=2)
        assert len(provider.embed_calls) == 3
        assert len(provider.embed_calls[0]) == 2
        assert len(provider.embed_calls[1]) == 2
        assert len(provider.embed_calls[2]) == 1
