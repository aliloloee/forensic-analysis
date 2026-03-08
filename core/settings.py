from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"


############ Static files and directories ############
EMAILS_CSV_PATH = STATIC_DIR / "emails.csv"  
EMBEDDINGS_DIR = STATIC_DIR / "dense_embeddings.npy" 


############ Embedding Model Settings ############
EMBEDDING_MODEL = "BAAI/bge-small-en" ## "BAAI/bge-large-en"
EMBEDDING_NORMALIZED = True
BATCH_SIZE = 64


############# Weaviate Settings ############
WEAVIATE_HTTP_HOST = "localhost"
WEAVIATE_HTTP_PORT = 8080
WEAVIATE_GRPC_PORT = 50051

COLLECTION_VECTOR_NAME = "dense_vector"

PIPELINE_VERSION = "v1"
SAFE_MODEL = EMBEDDING_MODEL.replace("/", "_").replace("-", "_")
CHUNK_COLLECTION = f"EmailChunk_{SAFE_MODEL}_{PIPELINE_VERSION}"



############## Search Settings ############
EMAIL_ID = "email_id"
CHUNK_TEXT_SPARSE = "chunk_text_sparse"
RETURN_PROPERTIES = [
    # "chunk_id",
    EMAIL_ID,
    # "chunk_index",
    # "chunk_base",
    CHUNK_TEXT_SPARSE,
    # "chunk_text_dense",
    # "subject",
    # "from",
    # "to",
    # "date",
]

BM25_fields = ["chunk_text_sparse"]
BM25_SCORE = "score"

DENSE_DISTANCE = "distance"
DENSE_SCORE = BM25_SCORE




############# Generation Settings ############
BASE = "http://141.55.226.254:11434"
BASE_URL = f"{BASE}/api/generate"

## Hypothesis Expansion (HE) Settings
HE_MODEL = "mixtral:8x22b"
HE_QUERIES = 10
HE_MAX_LENGTH = 5
HE_PROMPT_TEMPLATE = STATIC_DIR / "prompts" / "hypothesis_expansion.txt"

## Chunk Generation (CG) Settings
CG_MODEL = "llama3:latest"
CG_PROMPT_TEMPLATE = STATIC_DIR / "prompts" / "chunk_analysis.txt"
