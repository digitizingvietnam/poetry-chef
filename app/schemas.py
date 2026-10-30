"""
schemas.py

Request and response models for the `/ask` endpoint.

Field names are kept stable for the frontend; see GLOSSARY.md for what they
mean in domain terms (`question` is the Emotion, `additional_context` the Weight).
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Body of `POST /ask`."""

    question: str = Field(..., min_length=1, description="The user's Emotion.")
    additional_context: Optional[str] = Field(
        None, description="The Weight of the Emotion, e.g. '5 kg'."
    )
    temperature: Optional[float] = Field(
        None, ge=0.0, le=2.0, description="Overrides the LLM temperature."
    )


class SourceChunk(BaseModel):
    """The Original Recipe a Re-cooked Recipe was based on."""

    label: str
    chapter: Optional[str] = None
    book_title: Optional[str] = None
    file_name: Optional[str] = None
    source_path: Optional[str] = None
    text: str


class AskResponse(BaseModel):
    """Body returned by `POST /ask`."""

    answer: str
    citations: List[str]
    sources: List[SourceChunk]
