from core import settings
from chunks.adapters import row_to_properties, row_to_properties_email_level
from weaviate.util import generate_uuid5


def ingest_hypothesis(client, title: str, hypothesis: str, queries: list[str]):
    hypothesis_collection = client.collections.get(settings.HYPOTHESIS_COLLECTION)

    result = hypothesis_collection.data.insert(
        properties={
            "title": title,
            "hypothesis": hypothesis,
            "queries": queries,
        }
    )

    return result


def ingest_emails(client, emails_df):
    emails_collection = client.collections.get(settings.EMAIL_COLLECTION)

    with emails_collection.batch.dynamic() as batch:
        for i, row in emails_df.iterrows():
            batch.add_object(
                properties=row_to_properties_email_level(row),
                uuid=generate_uuid5(
                        {
                            "email_id": int(row["email_id"]),
                        }
                    ),
            )


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