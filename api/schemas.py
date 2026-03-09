from typing import List
from pydantic import BaseModel, Field


class EmbedRequest(BaseModel):
    inputs: List[str] = Field(..., min_length=1)


class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    model_name: str
    dimensions: int


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str | None = None