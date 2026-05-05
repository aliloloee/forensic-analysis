import time
import json

from retrieval.bm25 import retrieve_all as retrieve_all_bm25
from retrieval.dense import retrieve_all as retrieve_all_dense
from generation.chunk_analysis import generate_chunk_reasoning


from core import settings
def bm25_rag(hypothesis, queris, top_k):
    hits = retrieve_all_bm25(queris, top_k=top_k)
    print(hits)
    # unique_hits = hits.groupby('email_id', as_index=False).first()[['email_id','info']]
    # unique_hits.to_csv(
    #         settings.BASE_DIR/ 'bm25_h1_ground_truth.csv',
    #         index=False,
    #         encoding="utf-8",
    #     )
    reasoning_results = generate_chunk_reasoning(hits, hypothesis, limit=1)

    # with open(settings.BASE_DIR/ 'bm25_h1_reasonings.csv', "w", encoding="utf-8") as f:
    #     json.dump(reasoning_results, f, ensure_ascii=False, indent=4)


    # reasoning_results.to_csv(
    #         settings.BASE_DIR/ 'bm25_h1_reasonings.csv',
    #         index=False,
    #         encoding="utf-8",
    #     )
    # print(reasoning_results)
    # print(type(reasoning_results))

    return reasoning_results


def dense_rag(hypothesis, queris, top_k):
    hits = retrieve_all_dense(queris, top_k=top_k)
    print(hits)
    return None
    # reasoning_results = generate_chunk_reasoning(hits, hypothesis, limit=3)

    return reasoning_results