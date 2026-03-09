import weaviate
from core import settings


def get_client():
    client = weaviate.connect_to_local(
        host=settings.WEAVIATE_HTTP_HOST,
        port=settings.WEAVIATE_HTTP_PORT,
        grpc_port=settings.WEAVIATE_GRPC_PORT,
    )
    return client