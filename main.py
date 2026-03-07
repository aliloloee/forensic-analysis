from core import settings
from prepration.embedding import read_embeddings
from prepration.preprocessing import apply_chunking_and_normalization
from core.settings import EMBEDDINGS_DIR
from core.weaviate_client import get_client
from chunks.ingest import ingest_chunks
from chunks.collection import create_chunk_collection

# def bulk_ingestion():
#     chunk_df = apply_chunking_and_normalization()

#     #### This part need to be updated to compute embeddings instead of reading from file
#     embeddings = read_embeddings(EMBEDDINGS_DIR)

#     if len(chunk_df) != len(embeddings):
#         raise ValueError(f"Length mismatch: chunk_df has {len(chunk_df)} rows, but embeddings has {len(embeddings)} vectors.")
    
#     client = get_client()
#     create_chunk_collection(client)
#     ingest_chunks(client, chunk_df, embeddings)
#     client.close()


from retrieval.bm25 import retrieve_all


if __name__ == "__main__":
    # bulk_ingestion()
    H1_queries = [
        "bypass regulation strategy",
        "avoid price caps",
        "regulatory loophole",
        "off the record regulators",
        "do not disclose regulators",
        "confidential market manipulation",
        "talking points mislead",
        "keep this between us",
        "regulator unaware",
        "California price manipulation"
    ]

    hits = retrieve_all(H1_queries, top_k=10)
    print(hits.head())
    print(len(hits))