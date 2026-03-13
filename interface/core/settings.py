from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"

DEBUG = True  ## Avoid executing unnecessary and repetetive tasks while development 


############ Static files and directories ############
EMAILS_CSV_PATH = STATIC_DIR / "emails.csv"  
EMBEDDINGS_DIR = STATIC_DIR / "dense_embeddings.npy" 


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



############## Search Settings ############
EMAIL_ID = "email_id"
CHUNK_INDEX = "chunk_index"
CHUNK_TEXT_SPARSE = "chunk_text_sparse"
RETURN_PROPERTIES = [
    # "chunk_id",
    EMAIL_ID,
    CHUNK_INDEX,
    # "chunk_base",
    CHUNK_TEXT_SPARSE,
    # "chunk_text_dense",
    # "subject",
    # "from",
    # "to",
    # "date",
]
PER_QUERY_TOP_K = 10

BM25_fields = ["chunk_text_sparse"]
BM25_SCORE = "score"

DENSE_DISTANCE = "distance"
DENSE_SCORE = BM25_SCORE




############# Generation Settings ############
BASE = "http://141.55.226.254:11434"
BASE_URL = f"{BASE}/api/generate"

## Fetch available models at startup
ALL_MODELS = []
TAG_URL = f"{BASE}/api/tags"

## Hypothesis Expansion (HE) Settings
HE_MODEL = "mixtral:8x22b"
HE_QUERIES = 10
HE_MAX_LENGTH = 5
HE_PROMPT_TEMPLATE = STATIC_DIR / "prompts" / "hypothesis_expansion.txt"

## Chunk Generation (CG) Settings
CG_MODEL = "llama3:latest"
CG_PROMPT_TEMPLATE = STATIC_DIR / "prompts" / "chunk_analysis.txt"
