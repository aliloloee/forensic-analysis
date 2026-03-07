from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


############ Static files and directories ############
EMAILS_CSV_PATH = BASE_DIR / "emails.csv"  
EMBEDDINGS_DIR = BASE_DIR / "dense_embeddings.npy" 


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
RETURN_PROPERTIES = [
    # "chunk_id",
    # "email_id",
    # "chunk_index",
    # "chunk_base",
    "chunk_text_sparse",
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
