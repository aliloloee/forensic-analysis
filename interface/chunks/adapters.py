
def row_to_properties(row) -> dict:
    """
    Convert a DataFrame row into Weaviate-ready object.
    """
    return {
        "chunk_id": str(row["chunk_id"]),
        "email_id": int(row["email_id"]),

        "chunk_sparse": row["chunk_sparse"],
        "chunk_dense": row["chunk_dense"],

        "length": int(row["length"]),
        "subject": row.get("subject", ""),
    }



def row_to_properties_email_level(row) -> dict:
    """
    Convert a DataFrame row into Weaviate-ready object.
    """
    return {
        "email_id": int(row["email_id"]),
        "Annotation": row["Annotation"],

        "docID": row.get("docID", ""),
        "from": row.get("from", ""),
        "date": row.get("date", ""),
        "to": row.get("to", ""),
        "subject": row.get("subject", ""),

        "message": row["message"]
    }