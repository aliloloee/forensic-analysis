from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
DEBUG = False  ## Avoid executing unnecessary and repetetive tasks while development 


############ Static files and directories ############
# INGESTION = False
# EMAILS_CSV_PATH = STATIC_DIR / "emails.csv"  
# EMBEDDINGS_DIR = STATIC_DIR / "dense_embeddings.npy" 


############ Embedding Model Settings ############
# BATCH_SIZE = 64
# EMBEDDING_NORMALIZED = True
EMBEDDING_MODEL = "BAAI/bge-small-en" ## "BAAI/bge-large-en"
EMBEDDING_URL_BASE = "http://localhost:8000".rstrip("/")
EMBEDDING_URL_HEALTH = F"{EMBEDDING_URL_BASE}/health"
EMBEDDING_URL_EMBED = F"{EMBEDDING_URL_BASE}/embed"


############# Weaviate Settings ############
WEAVIATE_HTTP_HOST = "localhost"
WEAVIATE_HTTP_PORT = 8080
WEAVIATE_GRPC_PORT = 50051

COLLECTION_VECTOR_NAME = "dense_vector"

PIPELINE_VERSION = "v1"
SAFE_MODEL = EMBEDDING_MODEL.replace("/", "_").replace("-", "_")
CHUNK_COLLECTION = f"EmailChunk_{SAFE_MODEL}_{PIPELINE_VERSION}"

HYPOTHESIS_COLLECTION = 'Hypothesis'
ALL_HYPOTHESES = {}  # title: uuid

EMAIL_COLLECTION = F"Email_{PIPELINE_VERSION}"



############## Search Settings ############
EMAIL_ID = "email_id"
CHUNK_INDEX = "chunk_id"
CHUNK_TEXT_SPARSE = "chunk_sparse"
CHUNK_TEXT_DENSE = "chunk_dense"
RETURN_PROPERTIES = [
    EMAIL_ID,
    CHUNK_INDEX,
    CHUNK_TEXT_SPARSE,
    CHUNK_TEXT_DENSE
]
TOP_K_CHUNKS = 50

# BM25_fields = ["chunk_sparse"]
BM25_SCORE = "score"

DENSE_DISTANCE = "distance"
DENSE_SCORE = BM25_SCORE


BM25_RETRIEVED_CHUNKS_KEY = "bm25_retrieved_chunks"
DENSE_RETRIEVED_CHUNKS_KEY = "dense_retrieved_chunks"
HYBRID_RETRIEVED_CHUNKS_KEY = "hybrid_retrieved_chunks"

# RRF Constant
RRF_CONSTANT = 60


############# Generation Settings ############
BASE = "http://141.55.226.254:11434"
BASE_URL = f"{BASE}/api/generate"

## Fetch available models at startup
ALL_MODELS = []
TAG_URL = f"{BASE}/api/tags"

## Hypothesis Expansion (HE) Settings
HE_MODEL = "qwen3.5:latest"
HE_QUERIES = 10
# HE_MAX_LENGTH_SPARSE = 5 # Harcoded in the prompts
# HE_MAX_LENGTH_DENSE  = 20 # Harcoded in the prompts
HE_PROMPT_TEMPLATE_SPARSE = STATIC_DIR / "prompts" / "hypothesis_expansion_sparse.txt"
HE_PROMPT_TEMPLATE_DENSE = STATIC_DIR / "prompts" / "hypothesis_expansion_dense.txt"

## Chunk Generation (CG) Settings
CG_MODEL = "llama3:latest"
CG_PROMPT_TEMPLATE = STATIC_DIR / "prompts" / "chunk_analysis_2.txt"

## Inference Timeout
INFERENCE_TIMEOUT = 4*60
