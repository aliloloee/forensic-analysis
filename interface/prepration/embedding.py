from core import settings
import numpy as np

# import torch
# from sentence_transformers import SentenceTransformer


# def compute_embeddings(chunk_df):
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     model = SentenceTransformer(settings.EMBEDDING_MODEL, device=device)

#     embeddings = model.encode(
#         chunk_df["chunk_text_dense"].tolist(),
#         batch_size=settings.BATCH_SIZE,
#         convert_to_numpy=True,
#         normalize_embeddings=settings.EMBEDDING_NORMALIZED,
#         show_progress_bar=True
#     ).astype("float32")
#     return embeddings



def read_embeddings(npy_path=settings.EMBEDDINGS_DIR):
    return np.load(npy_path)

