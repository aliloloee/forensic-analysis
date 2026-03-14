import re
import pandas as pd



PARA_SPLIT_RE = re.compile(r"\n\s*\n+")

def split_into_paragraphs(text):
    if not text:
        return []
    return [p.strip() for p in PARA_SPLIT_RE.split(text) if p.strip()]


def chunk_email_text(
    text: str,
    min_chars: int = 200,
    max_chars: int = 1200,
    min_chunk_chars: int = 80
    ):
    paragraphs = split_into_paragraphs(text)
    chunks = []

    current_chunk = ""

    for para in paragraphs:
        # If a single paragraph is too long, split it
        if len(para) > max_chars:
            # Finish current chunk first
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            for i in range(0, len(para), max_chars):
                part = para[i:i + max_chars].strip()
                if len(part) >= min_chars:
                    chunks.append(part)
            continue

        # Try to add paragraph to current chunk
        if not current_chunk:
            current_chunk = para
        else:
            candidate = current_chunk + "\n\n" + para
            if len(candidate) <= max_chars:
                current_chunk = candidate
            else:
                chunks.append(current_chunk.strip())
                current_chunk = para

        # If current chunk is large enough, finalize it
        if len(current_chunk) >= min_chars:
            chunks.append(current_chunk.strip())
            current_chunk = ""

    # Add remaining text
    if current_chunk:
        chunks.append(current_chunk.strip())

    # Drop very small chunks (noise)
    return [c for c in chunks if len(c) >= min_chunk_chars]


def build_chunk_df(
    parsed_df,
    email_id_col: str = "email_id",
    text_col: str = "body_base",
    min_chars: int = 200,
    max_chars: int = 1200,
    min_chunk_chars: int = 80
):
    if email_id_col not in parsed_df.columns:
        parsed_df = parsed_df.copy()
        parsed_df[email_id_col] = parsed_df.index.astype(str)

    rows = []

    for _, row in parsed_df.iterrows():
        email_id = str(row[email_id_col])
        text = row.get(text_col, "") or ""

        chunks = chunk_email_text(text, min_chars=min_chars, max_chars=max_chars, min_chunk_chars=min_chunk_chars)

        for i, chunk_text in enumerate(chunks):
            rows.append({
                "chunk_id": f"{email_id}:{i}",
                "email_id": email_id,
                "chunk_index": i,
                "chunk_base": chunk_text,   # <-- changed from chunk_text
                # "subject": row.get("subject", ""),
                # "from": row.get("from", ""),
                # "to": row.get("to", ""),
                # "date": row.get("date", ""),
                "len_chunk_base": len(chunk_text),
            })

    return pd.DataFrame(rows)