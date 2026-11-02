from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.app.config import settings
from backend.app.api.v1.router import api_router

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Authentic AI-Powered Government Scheme Discovery & Application Assistant API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup: support local development, configured frontend domain, and wildcard in development/staging
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


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint required by deployment & operational specs."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.app_env,
        "timestamp": datetime.now(timezone.utc).isoformat()
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
