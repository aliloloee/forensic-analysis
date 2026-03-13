from chunks.ingest import ingest_hypothesis

from core import settings

from core.weaviate_client import get_client
from chunks.collection import create_hypothesis_collection



def add_hypothesis(title, hypothesis, queries):
    client = get_client()
    create_hypothesis_collection(client)

    obj_id = ingest_hypothesis(
        client,
        title=title,
        hypothesis=hypothesis,
        queries=queries,
    )

    print(obj_id)
    client.close()