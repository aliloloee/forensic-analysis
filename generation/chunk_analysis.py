import json
import requests
import pandas as pd

from core import settings


def _load_prompt_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _build_prompt(hypothesis, chunk, template_path=settings.CG_PROMPT_TEMPLATE):
    template = _load_prompt_template(template_path)
    return template.format(
        hypothesis=hypothesis,
        chunk=chunk
    )


def _process_chunk(prompt):
    payload = {
        "model": settings.CG_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(settings.BASE_URL, json=payload)
    response.raise_for_status()
    data = response.json()

    raw_text = data.get("response", "").strip()

    # Remove markdown code fences if present
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw_text = "\n".join(lines).strip()

    # First attempt: direct JSON parse
    try:
        parsed = json.loads(raw_text)
        parsed["raw_response"] = raw_text
        parsed["json_valid"] = True
        return parsed
    except json.JSONDecodeError:
        pass

    # Light repair: extract outer JSON object if extra text exists
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = raw_text[start:end + 1]
        try:
            parsed = json.loads(candidate)
            parsed["raw_response"] = raw_text
            parsed["json_valid"] = True
            return parsed
        except json.JSONDecodeError:
            pass

    # Fallback: return raw string instead of crashing
    return {
        "label": None,
        "reason": None,
        "evidence_spans": [],
        "raw_response": raw_text,
        "json_valid": False,
    }


def generate_chunk_reasoning(df, hypothesis, limit=None):
    ## The required columns must be dynamic based on "settings.RETURN_PROPERTIES"

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    required_cols = {settings.EMAIL_ID, settings.CHUNK_INDEX, settings.CHUNK_TEXT_SPARSE}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame is missing required columns: {missing}")

    results = []

    rows = df if limit is None else df.head(limit)

    for i, row in rows.iterrows():
        email_id = row[settings.EMAIL_ID]
        chunk_index = row[settings.CHUNK_INDEX]
        chunk_text = row[settings.CHUNK_TEXT_SPARSE]

        prompt = _build_prompt(hypothesis, chunk_text)
        llm_result = _process_chunk(prompt)

        llm_result[settings.EMAIL_ID] = email_id
        llm_result[settings.CHUNK_INDEX] = chunk_index
        # llm_result["chunk"] = chunk_text
        results.append(llm_result)

        print(f"Processed row {i}")

    return results
