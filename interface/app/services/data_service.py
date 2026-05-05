from core.weaviate_client import get_client
from chunks.ingest import ingest_chunks, ingest_emails
from chunks.collection import create_chunk_collection, create_email_collection



def _check_same_size(*vars_):
    lengths = [len(v) for v in vars_]
    if len(set(lengths)) != 1:
        raise ValueError(f"Length mismatch. All inputs must have the same length, got lengths: {lengths}")

def ingest_data(emails_df, chunks_df, embeddings_v1, embeddings_v2=None):

    if embeddings_v2 is not None:
        _check_same_size(chunks_df, embeddings_v1, embeddings_v2)
    else:
        _check_same_size(chunks_df, embeddings_v1)
    
    client = get_client()

    create_email_collection(client)
    ingest_emails(client, emails_df)

    create_chunk_collection(client)
    ingest_chunks(client, chunks_df, embeddings_v1)

    client.close()