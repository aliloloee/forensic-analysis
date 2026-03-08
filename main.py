from core import settings
from prepration.embedding import read_embeddings
from prepration.preprocessing import apply_chunking_and_normalization
from core.settings import EMBEDDINGS_DIR
from core.weaviate_client import get_client
from chunks.ingest import ingest_chunks
from chunks.collection import create_chunk_collection


## 1
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


## 2
# from retrieval.bm25 import retrieve_all

## 3
from generation.hypothesis_expansion import generate_queries


if __name__ == "__main__":

    ## 1
    # bulk_ingestion()

    ## 2
    # H1_queries = [
    #     "bypass regulation strategy",
    #     "avoid price caps",
    #     "regulatory loophole",
    #     "off the record regulators",
    #     "do not disclose regulators",
    #     "confidential market manipulation",
    #     "talking points mislead",
    #     "keep this between us",
    #     "regulator unaware",
    #     "California price manipulation"
    # ]

    # hits = retrieve_all(H1_queries, top_k=10)
    # print(hits.head())
    # print(len(hits))

    ## 3
    hypothesis = "During the California Energy Crisis (2000–2001), Enron personnel deliberately engaged in false import practices (“Ricochet” or “Megawatt Laundering”) by scheduling electricity exports from California with no intent of physical delivery, then reselling the same power back to the California ISO during declared emergencies at higher, uncapped real-time prices, in order to create an artificial appearance of scarcity and increase revenues"

    queries = generate_queries(
        hypothesis,
        num_queries=settings.HE_QUERIES,
        max_query_length=settings.HE_MAX_LENGTH,
        model=settings.HE_MODEL
        )
    print(queries)
    print(type(queries))  # Str. Need to be parsed as list