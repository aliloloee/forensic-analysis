import time

from retrieval.bm25 import retrieve_all as retrieve_all_bm25
from retrieval.dense import retrieve_all as retrieve_all_dense
from generation.chunk_analysis import generate_chunk_reasoning



def bm25_rag(hypothesis, queris, top_k):
    hits = retrieve_all_bm25(queris, top_k=top_k)
    reasoning_results = generate_chunk_reasoning(hits, hypothesis, limit=3)

    return reasoning_results


def dense_rag(hypothesis, queris, top_k):
    hits = retrieve_all_dense(queris, top_k=top_k)
    reasoning_results = generate_chunk_reasoning(hits, hypothesis, limit=3)

    return reasoning_results