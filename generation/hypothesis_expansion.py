import json
import requests

from core import settings



MODEL = settings.HE_MODEL


def _load_prompt_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _build_prompt(hypothesis, num_queries, max_query_length, template_path=settings.HE_PROMPT_TEMPLATE):
    template = _load_prompt_template(template_path)
    return template.format(
        hypothesis=hypothesis,
        num_queries=num_queries,
        max_query_length=max_query_length
    )


def generate_queries(
                    hypothesis,
                    num_queries=settings.HE_QUERIES,
                    max_query_length=settings.HE_MAX_LENGTH,
                    model=settings.HE_MODEL
                ):
    prompt = _build_prompt(hypothesis, num_queries, max_query_length)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.4
        }
    }

    r = requests.post(settings.BASE_URL, json=payload)
    r.raise_for_status()
    data = r.json()

    text = data.get("response", "").strip()

    # Try parsing JSON
    try:
        parsed = json.loads(text)
        return parsed["queries"]
    except Exception:
        return text

