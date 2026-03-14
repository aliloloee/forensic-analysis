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
            Property(
                name="topic",
                data_type=DataType.INT,
                description="The topics are: 201, 202, 203, 204, 205, 206, 207",
            ),
            Property(
                name="responsiveness",
                data_type=DataType.INT,
                description="Responsiveness to the corresponding topic: 0 or 1",
            ),
            Property(
                name="info",
                data_type=DataType.TEXT,
                description="Hypothesis information"
                ),
            Property(name="from", data_type=DataType.TEXT),
            Property(name="to", data_type=DataType.TEXT),
            Property(name="date", data_type=DataType.TEXT),
            Property(name="subject", data_type=DataType.TEXT),
            Property(name="message", data_type=DataType.TEXT),    ## Original raw email
            Property(name="text_base", data_type=DataType.TEXT),  ## subject + body of the email
            Property(name="body_base", data_type=DataType.TEXT),  ## body of the email
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
            Property(name="chunk_id", data_type=DataType.TEXT),
            Property(name="email_id", data_type=DataType.INT),
            Property(name="chunk_index", data_type=DataType.INT),

            Property(name="chunk_base", data_type=DataType.TEXT),
            Property(name="chunk_text_sparse", data_type=DataType.TEXT),
            Property(name="chunk_text_dense", data_type=DataType.TEXT),

            # Property(name="subject", data_type=DataType.TEXT),
            # Property(name="from", data_type=DataType.TEXT),
            # Property(name="to", data_type=DataType.TEXT),
            # Property(name="date", data_type=DataType.TEXT),
        ],
    )

    return client.collections.get(settings.CHUNK_COLLECTION)