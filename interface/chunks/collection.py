from weaviate.classes.config import Configure, Property, DataType
from core import settings


def create_hypothesis_collection(client):
    if client.collections.exists(settings.HYPOTHESIS_COLLECTION):
        return client.collections.get(settings.HYPOTHESIS_COLLECTION)

    collection = client.collections.create(
        name=settings.HYPOTHESIS_COLLECTION,
        properties=[
            Property(
                name="title",
                data_type=DataType.TEXT,
                description="Title of the hypothesis",
            ),
            Property(
                name="hypothesis",
                data_type=DataType.TEXT,
                description="A forensic hypothesis derived from the email",
            ),
            Property(
                name="queries",
                data_type=DataType.TEXT_ARRAY,
                description="A list of search queries associated with the hypothesis",
            ),
        ],
    )

    return collection


def create_email_collection(client):
    if client.collections.exists(settings.EMAIL_COLLECTION):
        return client.collections.get(settings.EMAIL_COLLECTION)

    collection = client.collections.create(
        name=settings.EMAIL_COLLECTION,
        properties=[
            Property(name="email_id", data_type=DataType.INT),
            Property(name="Annotation", data_type=DataType.TEXT),
            Property(name="docID", data_type=DataType.TEXT),
            Property(name="from", data_type=DataType.TEXT),
            Property(name="to", data_type=DataType.TEXT),
            Property(name="date", data_type=DataType.TEXT),
            Property(name="subject", data_type=DataType.TEXT),
            Property(name="message", data_type=DataType.TEXT),    ## Original raw email
        ]
    )

    return client.collections.get(settings.EMAIL_COLLECTION)


def create_chunk_collection(client):
    if client.collections.exists(settings.CHUNK_COLLECTION):
        return client.collections.get(settings.CHUNK_COLLECTION)

    client.collections.create(
        name=settings.CHUNK_COLLECTION,
        vector_config=Configure.Vectors.self_provided(
            name=settings.COLLECTION_VECTOR_NAME,
        ),
        properties=[
            Property(name="email_id", data_type=DataType.INT),
            Property(name="chunk_id", data_type=DataType.TEXT),

            Property(name="chunk_sparse", data_type=DataType.TEXT),
            Property(name="chunk_dense", data_type=DataType.TEXT),

            Property(name="subject", data_type=DataType.TEXT),
            Property(name="length", data_type=DataType.INT),
        ],
    )

    return client.collections.get(settings.CHUNK_COLLECTION)