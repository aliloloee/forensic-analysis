import time
import json

from retrieval.bm25 import retrieve_all as retrieve_all_bm25
from retrieval.dense import retrieve_all as retrieve_all_dense

from core import settings


def bm25_retrieve(queris, top_k):
    hits = retrieve_all_bm25(queris, top_k=top_k)
    print(f"bm25 hits are {len(hits)}")
    return hits

def dense_retrieve(queris, top_k):
    hits = retrieve_all_dense(queris, top_k=top_k)
    print(f"dense hits are {len(hits)}")
    return hits