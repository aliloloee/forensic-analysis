from core import settings
from chunks.adapters import row_to_properties
from weaviate.util import generate_uuid5


def ingest_chunks(client, chunk_df, embeddings):

    collection = client.collections.get(settings.CHUNK_COLLECTION)

    with collection.batch.dynamic() as batch:
        for i, row in chunk_df.iterrows():
            batch.add_object(
                properties=row_to_properties(row),
                vector={settings.COLLECTION_VECTOR_NAME: embeddings[i].tolist()},
                uuid=generate_uuid5(
                        {
                            "email_id": int(row["email_id"]),
                            "chunk_index": int(row["chunk_index"]),
                        }
                    ),
            )