import json
import requests

from core import settings



MODEL = settings.HE_MODEL


def _load_prompt_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _build_prompt(hypothesis, num_queries, template_path):
    template = _load_prompt_template(template_path)
    return template.format(
        hypothesis=hypothesis,
        num_queries=num_queries,
    )


def generate_queries(
                    hypothesis,
                    num_queries,
                    model,
                    template_path
                ):
    prompt = _build_prompt(hypothesis, num_queries, template_path)

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

