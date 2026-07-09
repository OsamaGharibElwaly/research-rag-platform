"""API Gateway - single entry point for all microservices."""
from contextlib import asynccontextmanager
import os
import time

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.shared.logger import get_logger
from backend.shared.schemas import APIError

logger = get_logger("api_gateway")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
UPLOAD_SERVICE_URL = os.getenv("UPLOAD_SERVICE_URL", "http://localhost:8002")
PARSER_SERVICE_URL = os.getenv("PARSER_SERVICE_URL", "http://localhost:8003")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "8000"))

PROTECTED_PREFIXES = ("/upload", "/papers", "/paper/", "/parse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Gateway starting up...")
    yield
    logger.info("API Gateway shutting down...")


app = FastAPI(
    title="API Gateway",
    description="Gateway for AI Research Paper Assistant microservices",
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


def _resolve_upstream(path: str) -> str | None:
    if path.startswith("/api/auth") or path == "/health":
        return AUTH_SERVICE_URL
    if path.startswith("/upload") or path.startswith("/papers") or path.startswith("/paper/"):
        return UPLOAD_SERVICE_URL
    if path.startswith("/parse"):
        return PARSER_SERVICE_URL
    return None


def _is_protected(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES)


async def _proxy(request: Request, upstream_base: str) -> Response:
    target_url = f"{upstream_base}{request.url.path}"
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length"}
    }

    body = await request.body()

    async with httpx.AsyncClient(timeout=60.0) as client:
        upstream_response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
        )

    response_headers = {
        key: value
        for key, value in upstream_response.headers.items()
        if key.lower() not in {"content-encoding", "transfer-encoding", "content-length"}
    }

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )


@app.get("/gateway/health")
async def gateway_health():
    return {"status": "healthy", "service": "api_gateway"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def gateway_proxy(request: Request, path: str):
    full_path = f"/{path}" if path else "/"

    upstream = _resolve_upstream(full_path)
    if upstream is None:
        return JSONResponse(
            status_code=404,
            content=APIError(
                status="error",
                message="Route not found",
                error=f"No upstream service for {full_path}",
                request_id=getattr(request.state, "request_id", "unknown"),
            ).model_dump(mode="json"),
        )

    if _is_protected(full_path) and "authorization" not in {
        key.lower() for key in request.headers.keys()
    }:
        return JSONResponse(
            status_code=401,
            content=APIError(
                status="error",
                message="Authentication required",
                error="Missing Authorization header",
                request_id=getattr(request.state, "request_id", "unknown"),
            ).model_dump(mode="json"),
        )

    return await _proxy(request, upstream)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.gateway.main:app",
        host="0.0.0.0",
        port=GATEWAY_PORT,
        reload=True,
    )
