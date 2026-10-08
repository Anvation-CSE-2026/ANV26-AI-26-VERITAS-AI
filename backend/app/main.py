from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.routes.auth import router as auth_router
from app.routes.billing import router as billing_router
from app.routes.contracts import router as contracts_router
from app.routes.embeddings import router as embeddings_router
from app.routes.webhooks import router as webhooks_router

app = FastAPI(title=settings.app_name, version="0.1.0")

# Register routes
app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(webhooks_router)
app.include_router(contracts_router)
app.include_router(embeddings_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health() -> HealthResponse:
    """Process health only; does not check AI-service readiness."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=app.version,
        environment=settings.environment,
    )
