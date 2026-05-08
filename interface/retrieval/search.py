import pandas as pd
from core import settings

from weaviate.classes.query import Filter


def _objects_to_df(objects, score_attr):
    rows = []

    for obj in objects:
        row = {prop: obj.properties.get(prop) for prop in settings.RETURN_PROPERTIES}

        metadata = getattr(obj, "metadata", None)

        if metadata is not None:
            if score_attr == settings.BM25_SCORE and hasattr(metadata, settings.BM25_SCORE):
                try:
                    row[settings.BM25_SCORE] = float(metadata.score)
                except (TypeError, ValueError):
                    row[settings.BM25_SCORE] = metadata.score

            elif score_attr == settings.DENSE_DISTANCE and hasattr(metadata, settings.DENSE_DISTANCE):
                # Convert distance to a score-like quantity for easier downstream use
                dist = float(metadata.distance)
                row[settings.DENSE_DISTANCE] = dist
                row[settings.DENSE_SCORE] = 1.0 - dist

        rows.append(row)

    return pd.DataFrame(rows)


def search_bm25(client, query: str, limit: int = 20) -> pd.DataFrame:
    collection = client.collections.get(settings.CHUNK_COLLECTION)

    response = collection.query.bm25(
        query=query,
        query_properties=[settings.CHUNK_TEXT_SPARSE],
        limit=limit,
        # filters=Filter.by_property("topic").equal(204),
        return_properties=settings.RETURN_PROPERTIES,
        return_metadata=[settings.BM25_SCORE],  # Higher score means more relevant
    )

    return _objects_to_df(response.objects, score_attr=settings.BM25_SCORE)


def search_dense(client, query_vector, limit: int = 20) -> pd.DataFrame:
    collection = client.collections.get(settings.CHUNK_COLLECTION)

    if hasattr(query_vector, "tolist"):
        query_vector = query_vector.tolist()

    response = collection.query.near_vector(
        near_vector=query_vector,
        target_vector=settings.COLLECTION_VECTOR_NAME,
        limit=limit,
        # filters=Filter.by_property("topic").equal(204),
        return_properties=settings.RETURN_PROPERTIES,
        return_metadata=[settings.DENSE_DISTANCE],    # Smaller distance means more relevant
    )

    return _objects_to_df(response.objects, score_attr=settings.DENSE_DISTANCE)
