from core import settings


def list_hypotheses(client):
    collection = client.collections.get(settings.HYPOTHESIS_COLLECTION)
    results = {}

    for item in collection.iterator():
        props = item.properties or {}
        results[props.get("title")] = str(item.uuid)

    return results


def get_hypothesis_by_uuid(client, hypothesis_uuid):
    collection = client.collections.get(settings.HYPOTHESIS_COLLECTION)

    obj = collection.query.fetch_object_by_id(hypothesis_uuid)
    if obj is None:
        return None

    props = obj.properties or {}
    return {
        "uuid": str(obj.uuid),
        "title": props.get("title"),
        "hypothesis": props.get("hypothesis"),
        "queries": props.get("queries", []),
    }