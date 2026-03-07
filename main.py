from core import settings
from prepration.embedding import read_embeddings
from prepration.preprocessing import apply_chunking_and_normalization
from core.settings import EMBEDDINGS_DIR
from core.weaviate_client import get_client
from chunks.ingest import ingest_chunks
from chunks.collection import create_chunk_collection

def bulk_ingestion():
    chunk_df = apply_chunking_and_normalization()

    #### This part need to be updated to compute embeddings instead of reading from file
    embeddings = read_embeddings(EMBEDDINGS_DIR)

    if len(chunk_df) != len(embeddings):
        raise ValueError(f"Length mismatch: chunk_df has {len(chunk_df)} rows, but embeddings has {len(embeddings)} vectors.")
    
    client = get_client()
    create_chunk_collection(client)
    ingest_chunks(client, chunk_df, embeddings)
    client.close()

def check():
    client = get_client()
    collection = client.collections.get(settings.CHUNK_COLLECTION)

    resp = collection.aggregate.over_all(total_count=True)
    print(resp.total_count)

    client.close()

def check_2():
    client = get_client()
    collection = client.collections.get(settings.CHUNK_COLLECTION)

    resp = collection.query.fetch_objects(limit=3)

    for obj in resp.objects:
        print(obj.properties)

    client.close()

if __name__ == "__main__":
    # bulk_ingestion()
    check_2()