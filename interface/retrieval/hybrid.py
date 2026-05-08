import pandas as pd
from core import settings

def extract_queries(q):
    """
    Converts:
    {"query1": 0.87, "query2": 0.54}

    into:
    ["query1", "query2"]
    """
    if isinstance(q, dict):
        return list(q.keys())
    return []


def rrf_hybrid(bm25_results, dense_results, K=settings.RRF_CONSTANT):
    bm25 = bm25_results.copy()
    bm25 = bm25.rename(columns={"score": "bm25_score"})

    dense = dense_results.copy()
    dense = dense.rename(columns={"score": "dense_score"})

    # -----------------------------------
    # Create RRF ranks (1-based)
    # Assumes dataframes are already sorted
    # from highest score -> lowest score
    # -----------------------------------
    bm25["bm25_rank"] = range(1, len(bm25) + 1)
    dense["dense_rank"] = range(1, len(dense) + 1)


    ################### Query MERGING ######################
    bm25["query"] = bm25["query"].apply(extract_queries)
    dense["query"] = dense["query"].apply(extract_queries)

    bm25 = bm25.rename(columns={"query": "bm25_queries"})
    dense = dense.rename(columns={"query": "dense_queries"})
    ########################################################


    merge_cols = [ "email_id", "chunk_id", "chunk_sparse", "chunk_dense"]
    final_df = pd.merge(
        bm25,
        dense,
        on=merge_cols,
        how="outer"
    )

    # Fill missing scores
    final_df["bm25_score"] = final_df["bm25_score"].fillna(0)
    final_df["dense_score"] = final_df["dense_score"].fillna(0)

    # RRF
    final_df["RRF"] = 0.0

    bm25_mask = final_df["bm25_rank"].notna()
    dense_mask = final_df["dense_rank"].notna()

    final_df.loc[bm25_mask, "RRF"] += (
        1 / (K + final_df.loc[bm25_mask, "bm25_rank"])
    )

    final_df.loc[dense_mask, "RRF"] += (
        1 / (K + final_df.loc[dense_mask, "dense_rank"])
    )


    ###### Combine queries from bm25 and dense ######
    final_df["query"] = final_df.apply(
        lambda row: {
            "dense": row["dense_queries"]
            if isinstance(row["dense_queries"], list)
            else [],
            "bm25": row["bm25_queries"]
            if isinstance(row["bm25_queries"], list)
            else []
        },
        axis=1
    ) 
    ##################################################

    final_df = final_df[
        [
            "email_id",
            "chunk_id",
            "chunk_sparse",
            "chunk_dense",
            "bm25_score",
            "dense_score",
            "RRF",
            "query"
        ]
    ]

    final_df = final_df.sort_values(
                    by="RRF",
                    ascending=False
                ).reset_index(drop=True)
    
    return final_df
