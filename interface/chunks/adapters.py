
def row_to_properties(row) -> dict:
    """
    Convert a DataFrame row into Weaviate-ready object.
    """
    return {
        "chunk_id": str(row["chunk_id"]),
        "email_id": int(row["email_id"]),
        "chunk_index": int(row["chunk_index"]),

        "chunk_base": row["chunk_base"],
        "chunk_text_sparse": row["chunk_text_sparse"],
        "chunk_text_dense": row["chunk_text_dense"],

        # "subject": row.get("subject", ""),
        # "from": row.get("from", ""),
        # "to": row.get("to", ""),
        # "date": row.get("date", ""),
    }



def row_to_properties_email_level(row) -> dict:
    """
    Convert a DataFrame row into Weaviate-ready object.
    """
    return {
        "email_id": int(row["email_id"]),
        "topic": int(row["topic"]),
        "responsiveness": int(row["responsiveness"]),

        "info": row["info"],

        "from": row.get("from", ""),
        "date": row.get("date", ""),
        "to": row.get("to", ""),
        "subject": row.get("subject", ""),

        "message": row["message"],
        "text_base": row["text_base"],
        "body_base": row["body_base"]
    }