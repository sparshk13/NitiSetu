import time
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from backend.app.config import settings
from backend.app.api.v1.router import api_router
from backend.app.services.scheme_service import scheme_service
from backend.app.services.rag.retriever import retriever

logger = logging.getLogger("nitisetu.api")

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Authentic AI-Powered Government Scheme Discovery & Application Assistant API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. Production Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# 2. Production Request Timing & Diagnostic Middleware
class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Process-Time"] = f"{process_time_ms}ms"
        if request.url.path not in ("/health", "/"):
            logger.info(f"{request.method} {request.url.path} responded {response.status_code} in {process_time_ms}ms")
        return response

app.add_middleware(RequestTimingMiddleware)

# 3. CORS setup: support local development, configured frontend domain, and wildcard in development/staging
origins = [
    settings.frontend_origin,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.frontend_origin == "*" else origins,
    allow_origin_regex=r"https://.*" if settings.frontend_origin != "*" else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Please correct the highlighted fields.",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error at {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again shortly."
            }
        }
    )


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint with subsystem readiness diagnostics."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.app_env,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "diagnostics": {
            "catalog_schemes_loaded": len(scheme_service._schemes),
            "rag_chunks_indexed": len(retriever._chunks),
            "generation_model": getattr(settings, "gemini_generation_model", "gemini-flash-lite-latest")
        }
    }


# Root informational endpoint
@app.get("/", tags=["System"])
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "disclaimer": "NitiSetu is an independent public welfare assistant and not an official government agency."
    }
