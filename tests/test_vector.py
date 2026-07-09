"""Vector service tests."""
from backend.services.vector_service.services.embedding_access import EmbeddingRecord
from backend.services.vector_service.services.vector_service import VectorIndexService
from backend.services.vector_service.utils.base_index import BaseVectorIndex, SearchResult


class _InlineStubIndex(BaseVectorIndex):
    def __init__(self, dimension: int, bit_width: int = 4):
        self._dimension = dimension
        self._bit_width = bit_width
        self._vectors: dict[int, list[float]] = {}

    @property
    def engine_name(self) -> str:
        return "stub"

    @property
    def dimension(self) -> int | None:
        return self._dimension

    @property
    def vector_count(self) -> int:
        return len(self._vectors)

    def add_with_ids(self, vectors: list[list[float]], ids: list[int]) -> None:
        for vector, vector_id in zip(vectors, ids, strict=True):
            self._vectors[int(vector_id)] = list(vector)

    def search(self, query: list[float], top_k: int, allowlist: list[int] | None = None) -> SearchResult:
        candidates = self._vectors.items()
        if allowlist is not None:
            allowed = set(allowlist)
            candidates = ((vid, vec) for vid, vec in candidates if vid in allowed)

        def dot(a: list[float], b: list[float]) -> float:
            return sum(x * y for x, y in zip(a, b, strict=True))

        ranked = sorted(
            ((vid, dot(query, vec)) for vid, vec in candidates),
            key=lambda item: item[1],
            reverse=True,
        )[:top_k]
        return SearchResult(ids=[item[0] for item in ranked], scores=[item[1] for item in ranked])

    def contains(self, vector_id: int) -> bool:
        return int(vector_id) in self._vectors

    def remove(self, vector_id: int) -> bool:
        return self._vectors.pop(int(vector_id), None) is not None

    def prepare(self) -> None:
        return None

    def save(self, path: str) -> None:
        return None

    @classmethod
    def load(cls, path: str, bit_width: int) -> "_InlineStubIndex":
        return cls(8, bit_width)

    @classmethod
    def create(cls, dimension: int, bit_width: int) -> "_InlineStubIndex":
        return cls(dimension, bit_width)


class TestVectorHealth:
    def test_health_check(self, vector_client):
        response = vector_client.get("/health")
        assert response.status_code == 200
        assert response.json()["service"] == "vector_service"


class TestIndexCreation:
    def test_index_creation(self, vector_client, auth_headers, embedded_paper):
        response = vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": embedded_paper["id"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["paper_id"] == embedded_paper["id"]
        assert data["data"]["vector_count"] >= 1
        assert data["data"]["vectors_indexed"] >= 1
        assert data["data"]["engine"] == "stub"
        assert data["data"]["index_size_bytes"] > 0


class TestDuplicatePrevention:
    def test_duplicate_prevention(self, vector_client, auth_headers, embedded_paper):
        first = vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": embedded_paper["id"]},
        )
        second = vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": embedded_paper["id"]},
        )
        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json()["data"]["vectors_indexed"] >= 1
        assert second.json()["data"]["vectors_indexed"] == 0
        assert second.json()["data"]["status"] == "unchanged"
        assert first.json()["data"]["vector_count"] == second.json()["data"]["vector_count"]


class TestPersistence:
    def test_persistence(self, vector_client, auth_headers, embedded_paper):
        response = vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": embedded_paper["id"]},
        )
        assert response.status_code == 200
        assert response.json()["data"]["index_size_bytes"] > 0


class TestLoading:
    def test_loading(self, vector_client, auth_headers, embedded_paper, get_stored_embeddings):
        vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": embedded_paper["id"]},
        )
        stored = get_stored_embeddings(embedded_paper["id"])
        query = stored[0].get_vector()
        search = vector_client.post(
            "/search",
            headers=auth_headers,
            json={
                "paper_id": embedded_paper["id"],
                "query_embedding": query,
                "top_k": 3,
            },
        )
        assert search.status_code == 200
        assert search.json()["data"]["results"]


class TestSearching:
    def test_searching(self, vector_client, auth_headers, embedded_paper, get_stored_embeddings):
        vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": embedded_paper["id"]},
        )
        stored = get_stored_embeddings(embedded_paper["id"])
        query = stored[0].get_vector()
        response = vector_client.post(
            "/search",
            headers=auth_headers,
            json={
                "paper_id": embedded_paper["id"],
                "query_embedding": query,
                "top_k": 5,
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["search_latency_ms"] >= 0
        assert len(body["data"]["results"]) >= 1


class TestTopKCorrectness:
    def test_top_k_correctness(self, vector_client, auth_headers, embedded_paper, get_stored_embeddings):
        vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": embedded_paper["id"]},
        )
        stored = get_stored_embeddings(embedded_paper["id"])
        query = stored[0].get_vector()
        response = vector_client.post(
            "/search",
            headers=auth_headers,
            json={
                "paper_id": embedded_paper["id"],
                "query_embedding": query,
                "top_k": 2,
            },
        )
        results = response.json()["data"]["results"]
        assert len(results) <= 2
        assert results[0]["chunk_id"] == stored[0].chunk_id
        assert results[0]["score"] >= results[-1]["score"]


class TestAuthorization:
    def test_unauthorized_user(self, vector_client, embedded_paper):
        response = vector_client.post(
            "/index",
            json={"paper_id": embedded_paper["id"]},
        )
        assert response.status_code in (401, 403)

    def test_ownership_validation(self, vector_client, other_user_headers, embedded_paper):
        response = vector_client.post(
            "/index",
            headers=other_user_headers,
            json={"paper_id": embedded_paper["id"]},
        )
        assert response.status_code == 403


class TestMissingEmbeddings:
    def test_missing_embeddings(self, vector_client, auth_headers, chunked_paper):
        response = vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": chunked_paper["id"]},
        )
        assert response.status_code == 404


class TestInvalidPaper:
    def test_invalid_paper(self, vector_client, auth_headers):
        response = vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": 99999},
        )
        assert response.status_code == 404


class TestAPIResponseSchema:
    def test_api_response_schema(self, vector_client, auth_headers, embedded_paper):
        response = vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": embedded_paper["id"]},
        )
        body = response.json()
        assert body["status"] == "success"
        for field in (
            "paper_id",
            "engine",
            "vector_count",
            "dimension",
            "vectors_indexed",
            "index_path",
            "index_size_bytes",
            "bit_width",
            "status",
            "processing_time_ms",
        ):
            assert field in body["data"]


class TestErrorHandling:
    def test_invalid_request_body(self, vector_client, auth_headers):
        response = vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": 0},
        )
        assert response.status_code == 422


class TestProviderAbstraction:
    def test_provider_is_swappable(self):
        index = _InlineStubIndex.create(8, 4)
        service = VectorIndexService(index)
        records = [
            EmbeddingRecord(chunk_id=1, paper_id=1, vector=[1.0] + [0.0] * 7, dimension=8, model="stub"),
            EmbeddingRecord(chunk_id=2, paper_id=1, vector=[0.0, 1.0] + [0.0] * 6, dimension=8, model="stub"),
        ]
        added = service.add_embeddings(records)
        assert added == 2
        result = index.search([1.0] + [0.0] * 7, top_k=1)
        assert result.ids[0] == 1


class TestIncrementalIndexing:
    def test_incremental_indexing(self, vector_client, auth_headers, embedded_paper):
        first = vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": embedded_paper["id"]},
        )
        second = vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": embedded_paper["id"], "rebuild": False},
        )
        assert first.json()["data"]["vectors_indexed"] >= 1
        assert second.json()["data"]["vectors_indexed"] == 0
        assert second.json()["data"]["vector_count"] == first.json()["data"]["vector_count"]


class TestIndexDeletion:
    def test_index_deletion(self, vector_client, auth_headers, embedded_paper, get_stored_embeddings):
        vector_client.post(
            "/index",
            headers=auth_headers,
            json={"paper_id": embedded_paper["id"]},
        )
        delete = vector_client.delete(
            f"/index/{embedded_paper['id']}",
            headers=auth_headers,
        )
        assert delete.status_code == 200
        stored = get_stored_embeddings(embedded_paper["id"])
        search = vector_client.post(
            "/search",
            headers=auth_headers,
            json={
                "paper_id": embedded_paper["id"],
                "query_embedding": stored[0].get_vector(),
                "top_k": 3,
            },
        )
        assert search.status_code == 404
