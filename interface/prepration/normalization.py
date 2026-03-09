import re

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)


def normalize(text):
    """
    Normalize text for retrieval (e.g., BM25 indexing).

    Steps:
    - Convert to lowercase
    - Remove URLs
    - Replace non-alphanumeric characters (except email-safe symbols) with spaces
    - Collapse multiple spaces into one

    Parameters
    ----------
    text : str

    Returns
    -------
    str
        Normalized text suitable for retrieval models.
    """
    text = text.lower()
    text = URL_RE.sub(" ", text)
    text = re.sub(r"[^a-z0-9@\.\+\-_]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def apply_method_normalization(chunk_df, base_col: str = "chunk_base"):

    ingest_df = chunk_df.copy()
    ingest_df["chunk_text_sparse"] = chunk_df["chunk_base"].apply(normalize)
    ingest_df["chunk_text_dense"] = chunk_df["chunk_base"].astype(str)

    return ingest_df