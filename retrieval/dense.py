# from sentence_transformers import SentenceTransformer
# from core.weaviate_client import get_client
# from chunks.search import search_dense

# model = SentenceTransformer("BAAI/bge-small-en")
# query_vec = model.encode(
#     ["energy trading losses"],
#     convert_to_numpy=True,
#     normalize_embeddings=True,
# ).astype("float32")[0]

# client = get_client()

# hits = search_dense(
#     client=client,
#     query_vector=query_vec,
#     limit=20,
# )

# client.close()
# print(hits.head())