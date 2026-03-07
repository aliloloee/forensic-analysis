# import numpy as np
# import pandas as pd


# def add_email_evidence(results: pd.DataFrame) -> pd.DataFrame:
#     if results.empty:
#         return results.copy()

#     out = results.copy()

#     g = out.groupby("email_id")["score"]
#     out["email_max_score"] = g.transform("max")
#     out["email_sum_score"] = g.transform("sum")
#     out["email_hit_count"] = g.transform("count")

#     out["chunk_rank_in_email"] = (
#         out.groupby("email_id")["score"]
#         .rank(method="first", ascending=False)
#         .astype(int)
#     )

#     out["email_score"] = (
#         out["email_max_score"]
#         + 0.3 * out["email_sum_score"]
#         + 0.2 * np.log1p(out["email_hit_count"])
#     )

#     return out.sort_values(
#         ["email_score", "score"],
#         ascending=False
#     ).reset_index(drop=True)