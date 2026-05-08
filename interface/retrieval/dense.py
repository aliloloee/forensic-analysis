import pandas as pd

from retrieval.search import search_dense

from core.weaviate_client import get_client
from core.embedding_client import EmbeddingClient
from core import settings


def _retrieve(client, query_vec, top_k):
    return search_dense(
        client=client,
        query_vector=query_vec,
        limit=top_k,
    )

def retrieve_all(queries: list[str], top_k):
    top_k_per_query = top_k // len(queries)
    embedder = EmbeddingClient()
    client = get_client()
    try:
        all_hits = []
        for q in queries:
            query_vec = embedder.embed([q])[0]
            df = _retrieve(client, query_vec, top_k=top_k_per_query)
            # Normalization of scores is not needed for dense retrieval
            df["query"] = q
            # print(f"Retrieved {len(df)} hits for query: {q}")
            all_hits.append(df)

        if not all_hits:
            return pd.DataFrame()

        hypothesis_hits = pd.concat(all_hits, ignore_index=True)

        ## Aggregate queries and scores | Sort on scores
        group_cols = [settings.EMAIL_ID, settings.CHUNK_INDEX]
        same_cols = [c for c in hypothesis_hits.columns if c not in group_cols + ["score", "query"]]
        hypothesis_hits = (
                hypothesis_hits.groupby(group_cols, as_index=False)
                .apply(
                    lambda g: pd.Series({
                        **{col: g[col].iloc[0] for col in same_cols},
                        "score": g["score"].max(),
                        # "score": g["score"].sum(),
                        "query": dict(zip(g["query"], g["score"]))
                    })
                )
                .sort_values(["score"],ascending=[False])
            ).reset_index(drop=True)
        
        hypothesis_hits = hypothesis_hits.drop('distance', axis=1)

        # hypothesis_hits.to_csv(
        #     settings.BASE_DIR/ 'dense_hits.csv',
        #     index=False,
        #     encoding="utf-8",
        # )

        # return add_email_evidence(hypothesis_hits) ## Add later
        return hypothesis_hits
    finally:
        client.close()
