"""Embedding service main application."""
from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.services.embedding_service.routers import router as embed_router
from backend.shared.logger import get_logger
from backend.shared.schemas import APIError

logger = get_logger("embedding_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Embedding service starting up...")
    yield
    logger.info("Embedding service shutting down...")


app = FastAPI(
    title="Embedding Service",
    description="Semantic embedding microservice for AI Research Paper Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    start_time = time.time()
    request.state.request_id = f"req_{int(start_time * 1000)}"
    response = await call_next(request)
    duration = time.time() - start_time
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Process-Time"] = str(duration)
    logger.info(
        f"[{request.state.request_id}] {request.method} {request.url.path} "
        f"- {response.status_code} - {duration:.3f}s"
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=APIError(
            status="error",
            message="Internal server error",
            error=str(exc),
            request_id=getattr(request.state, "request_id", "unknown"),
        ).model_dump(mode="json"),
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "embedding_service"}


app.include_router(embed_router)


if __name__ == "__main__":
    import uvicorn

    from backend.services.embedding_service.config import SERVICE_PORT

    uvicorn.run(
        "backend.services.embedding_service.main:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True,
    )
