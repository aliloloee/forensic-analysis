# from sentence_transformers import SentenceTransformer
# from core.weaviate_client import get_client
# from chunks.search import search_hybrid

# model = SentenceTransformer("BAAI/bge-small-en")
# query = "energy trading losses"
# query_vec = model.encode(
#     [query],
#     convert_to_numpy=True,
#     normalize_embeddings=True,
# ).astype("float32")[0]

# client = get_client()

# hits = search_hybrid(
#     client=client,
#     query=query,
#     query_vector=query_vec,
#     alpha=0.5,
#     limit=20,
# )

# client.close()
# print(hits.head())