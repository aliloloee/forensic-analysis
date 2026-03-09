import pandas as pd

from core.weaviate_client import get_client
from retrieval.search import search_bm25



def _retrieve(client, query: str, top_k=20):
    return search_bm25(
        client=client,
        query=query,
        limit=top_k,
    )


def retrieve_all(queries: list[str], top_k=20):
    client = get_client()
    try:
        all_hits = []
        for q in queries:
            df = _retrieve(client, q, top_k=top_k)
            df["query"] = q
            all_hits.append(df)

        if not all_hits:
            return pd.DataFrame()

        hypothesis_hits = pd.concat(all_hits, ignore_index=True)

        # return add_email_evidence(hypothesis_hits) ## Add later
        return hypothesis_hits
    finally:
        client.close()
