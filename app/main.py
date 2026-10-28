"""
main.py

FastAPI entry point for the Poetry Chef backend.

Endpoints (documented in API.md):
- GET  /        liveness check
- GET  /health  liveness check
- POST /ask     re-cook an Emotion into a historical Vietnamese recipe

Run locally with `uvicorn app.main:app --reload --port 8000`.
"""

from __future__ import annotations

import logging
from time import perf_counter
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .deps import get_app_settings, get_service
from .schemas import AskRequest, AskResponse
from .service import PoetryChefService

LOGGER = logging.getLogger(__name__)
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False


settings = get_app_settings()

app = FastAPI(
    title="Poetry Chef Assistant",
    docs_url="/swagger",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    """Liveness check at the root path."""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse, tags=["assistant"])
async def ask_endpoint(
    payload: AskRequest,
    service: Annotated[PoetryChefService, Depends(get_service)],
) -> AskResponse:
    """Re-cook the user's Emotion using a random Original Recipe."""
    start_ts = perf_counter()
    result = service.ask(
        question=payload.question,
        additional_context=payload.additional_context,
        temperature=payload.temperature,
    )
    duration = perf_counter() - start_ts

    LOGGER.info(
        "Ask request completed in %.3fs for emotion: %s",
        duration,
        payload.question
    )
    return AskResponse(**result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
