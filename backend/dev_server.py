"""Single-process local dev API — auth + upload on port 8000.

Use this for local development when you don't want to run 3 separate processes.
For full microservices mode, use gateway + auth_service + upload_service instead.
"""
from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.services.auth_service.routers import router as auth_router
from backend.services.parser_service.routers import router as parser_router
from backend.services.upload_service.routers import router as upload_router
from backend.shared.logger import get_logger
from backend.shared.schemas import APIError

logger = get_logger("dev_server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Dev server starting (auth + upload + parser on :8000)...")
    yield
    logger.info("Dev server shutting down...")


app = FastAPI(
    title="AI Research Assistant API (Dev)",
    description="Combined auth + upload + parser server for local development",
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
    return {
        "status": "healthy",
        "service": "dev_server",
        "routes": ["auth", "upload", "parser"],
    }


app.include_router(auth_router, prefix="/api")
app.include_router(upload_router)
app.include_router(parser_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.dev_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
