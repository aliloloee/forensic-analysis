import time

from retrieval.bm25 import retrieve_all
from generation.chunk_analysis import generate_chunk_reasoning



def bm25_rag(hypothesis, queris, top_k):
    hits = retrieve_all(queris, top_k=top_k)
    reasoning_results = generate_chunk_reasoning(hits, hypothesis, limit=1)

    return reasoning_results