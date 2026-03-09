import pandas as pd

from core.weaviate_client import get_client
from core.embedding_client import EmbeddingClient
from retrieval.search import search_dense


def _retrieve(client, query_vec, top_k=20):
    return search_dense(
        client=client,
        query_vector=query_vec,
        limit=top_k,
    )

def retrieve_all(queries: list[str], top_k=20):
    embedder = EmbeddingClient()
    client = get_client()
    try:
        all_hits = []
        for q in queries:
            texts = list(q)
            query_vec = embedder.embed(texts)[0]
            df = _retrieve(client, query_vec, top_k=top_k)
            df["query"] = q
            all_hits.append(df)

        if not all_hits:
            return pd.DataFrame()

        hypothesis_hits = pd.concat(all_hits, ignore_index=True)

        # return add_email_evidence(hypothesis_hits) ## Add later
        return hypothesis_hits
    finally:
        client.close()
