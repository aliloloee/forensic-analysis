import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sentence_transformers import SentenceTransformer

from api.schemas import EmbedRequest, EmbedResponse, HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/models_cache")
NORMALIZE_EMBEDDINGS = os.getenv("NORMALIZE_EMBEDDINGS", "false").lower() == "true"

model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    logger.info("Loading model: %s", MODEL_NAME)
    model = SentenceTransformer(
        MODEL_NAME,
        cache_folder=MODEL_CACHE_DIR,
    )
    logger.info("Model loaded")
    yield
    model = None


app = FastAPI(lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        model_loaded=model is not None,
        model_name=MODEL_NAME if model is not None else None,
    )


@app.post("/embed", response_model=EmbedResponse)
def embed(req: EmbedRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded yet")

    vectors = model.encode(
        req.inputs,
        convert_to_numpy=True,
        normalize_embeddings=NORMALIZE_EMBEDDINGS,
    )

    return EmbedResponse(
        embeddings=vectors.tolist(),
        model_name=MODEL_NAME,
        dimensions=int(vectors.shape[1]),
    )