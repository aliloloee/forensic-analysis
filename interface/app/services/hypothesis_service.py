from chunks.ingest import ingest_hypothesis

from core import settings

from core.weaviate_client import get_client
from chunks.collection import create_hypothesis_collection
from chunks.retrieve import list_hypotheses, get_hypothesis_by_uuid



def add_hypothesis(title, hypothesis, queries):
    client = get_client()
    create_hypothesis_collection(client)

    obj_id = ingest_hypothesis(
        client,
        title=title,
        hypothesis=hypothesis,
        queries=queries,
    )

    # Update setting
    settings.ALL_HYPOTHESES[title] = str(obj_id)
    # print(settings.ALL_HYPOTHESES)
    # print(obj_id)
    
    client.close()


def get_all_hypotheses():
    client = get_client()
    create_hypothesis_collection(client)
    all_hypotheses = list_hypotheses(client)
    # print(all_hypotheses)
    client.close()
    return all_hypotheses


def get_hypothesis(uuid):
    client = get_client()
    create_hypothesis_collection(client)
    one_hypothesis = get_hypothesis_by_uuid(client, uuid)
    # print(one_hypothesis)
    client.close()
    return one_hypothesis
