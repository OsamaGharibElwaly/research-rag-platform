"""Vector index provider factory."""
from backend.services.vector_service.config import VECTOR_BIT_WIDTH, VECTOR_ENGINE
from backend.services.vector_service.providers.turbovec_provider import TurboVecIndex
from backend.services.vector_service.utils.base_index import BaseVectorIndex


def get_vector_index_provider(
    engine_name: str | None = None,
    bit_width: int | None = None,
) -> type[BaseVectorIndex]:
    name = (engine_name or VECTOR_ENGINE).lower()
    if name == "turbovec":
        return TurboVecIndex
    raise ValueError(f"Unsupported vector engine: {name}")


def create_index(dimension: int, engine_name: str | None = None, bit_width: int | None = None) -> BaseVectorIndex:
    provider_cls = get_vector_index_provider(engine_name, bit_width)
    effective_bit_width = bit_width or VECTOR_BIT_WIDTH
    return provider_cls.create(dimension, effective_bit_width)


def load_index(path: str, engine_name: str | None = None, bit_width: int | None = None) -> BaseVectorIndex:
    provider_cls = get_vector_index_provider(engine_name, bit_width)
    effective_bit_width = bit_width or VECTOR_BIT_WIDTH
    return provider_cls.load(path, effective_bit_width)
