import re
import ast


# Matches URLs starting with http://, https://, or www.
# Used to remove links from email text during normalization.
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

# Patterns that indicate the beginning of quoted replies (NOT forwards).
# We avoid cutting on "Forwarded by" because many Enron EDRM emails are pure forwards.
REPLY_CUTOFF_PATTERNS = [
    # Lines like: "----- Original Message -----"
    re.compile(r"(?im)^-{2,}\s*original message\s*-{2,}"),
    re.compile(r"(?im)^\s*-----\s*original message\s*-----\s*$"),
    re.compile(r"(?im)^\s*-----\s*original\s+message\s*-----\s*$"),

    # Lines like: "On Mon, Jan 1, 2024, John wrote:"
    re.compile(r"(?im)^on .+ wrote:\s*$"),

    # Apple Mail / iOS style
    re.compile(r"(?im)^begin forwarded message:\s*$"),  # rare, but typically denotes older content in replies
]

# Divider lines used in Enron EDRM-style forwards
FORWARD_DIVIDER_RE = re.compile(r"(?im)^\s*-{2,}\s*forwarded by\b.*$")
FORWARD_TIMEBAR_RE = re.compile(r"(?im)^\s*\d{1,2}:\d{2}\s*(am|pm)\b.*-{2,}\s*$")

# Mini “wrapper headers” that appear inside forwarded blocks
FORWARD_MINI_HEADER_RE = re.compile(r"(?im)^(from|sent by|to|cc|bcc|subject)\s*:\s+.*$")


ORIGINAL_MSG_LINE_RE = re.compile(r"(?im)^\s*-{2,}\s*original message\s*-{2,}\s*$")
ATTACH_RE = re.compile(r"(?im)^\s*<<\s*file:.*?>>\s*$")

# Outlook-style mini header block that repeats inside threads
REPLY_HDR_BLOCK_RE = re.compile(
    r"(?ims)^\s*from:\s.*?\n\s*sent:\s.*?\n\s*to:\s.*?\n\s*subject:\s.*?(?:\n\s*cc:\s.*)?\s*(?:\n|$)"
)

# Remove standalone lines that are just thanks / regards / a name.
SHORT_PLEASANTRY_RE = re.compile(
    r"(?im)^\s*(thanks|thank you|thx|regards|best|sincerely|cheers)\s*[,\.\!]*\s*$"
)

# SINGLE_NAME_LINE_RE = re.compile(r"(?im)^\s*[A-Z][a-z]+(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z]+)?\s*$")

INFO_LINE_RE = re.compile(r"(?i)^\s*info\s*:\s*(.+)\s*$")





def remove_original_message_lines(text: str) -> str:
    return ORIGINAL_MSG_LINE_RE.sub("", text)

def remove_attachment_placeholders(text: str) -> str:
    return ATTACH_RE.sub("", text)

def remove_reply_header_blocks(text: str) -> str:
    return REPLY_HDR_BLOCK_RE.sub("", text)

def drop_short_pleasantries(text: str) -> str:
    lines = [ln for ln in text.split("\n") if not SHORT_PLEASANTRY_RE.match(ln)]
    return "\n".join(lines)


# def drop_lonely_name_lines(text: str) -> str:
#     out = []
#     for ln in text.split("\n"):
#         if SINGLE_NAME_LINE_RE.match(ln.strip()) and len(ln.strip().split()) <= 3:
#             # drop only if it's a tiny standalone line
#             continue
#         out.append(ln)
#     return "\n".join(out)


def split_info_and_email(raw: str):
    """
    Extract first INFO line like 'INFO: (<tuple>)' even if there's BOM/blank lines.
    Returns (info_obj_or_str, email_text_without_info_line).
    """
    if not raw:
        return None, ""

    raw = raw.replace("\r\n", "\n").replace("\r", "\n")

    # remove UTF-8 BOM if present
    raw = raw.lstrip("\ufeff")

    lines = raw.split("\n")

    # skip leading blank lines
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    if i < len(lines):
        m = INFO_LINE_RE.match(lines[i])
        if m:
            payload = m.group(1).strip()
            try:
                info = ast.literal_eval(payload)
            except Exception:
                info = payload  # keep raw if not a valid literal
            email_text = "\n".join(lines[i + 1 :]).lstrip("\n")
            return info, email_text

    return None, raw


def split_headers_body(raw_msg: str):
    """
    Split email into header and body.

    The EDRM Enron v2 TXT exports often insert blank lines between header fields,
    so we cannot rely on '\n\n' as the separator.

    Strategy:
    - Treat initial lines matching 'Field: value' (plus whitespace-continuations) as header.
    - Allow blank lines inside the header block.
    - First line that is not blank/continuation and not 'Field: ...' starts the body.
    """
    raw_msg = (raw_msg or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = raw_msg.split("\n")

    header_lines = []
    body_start = len(lines)

    header_field_re = re.compile(r"^[A-Za-z][A-Za-z0-9-]*:\s*.*$")

    saw_any_header = False
    for i, ln in enumerate(lines):
        s = ln.strip("\ufeff")
        if s == "":
            # keep blank lines in header until we decide body started
            header_lines.append(ln)
            continue

        if header_field_re.match(s) or (saw_any_header and (ln.startswith(" ") or ln.startswith("\t"))):
            saw_any_header = True
            header_lines.append(ln)
            continue

        # first non-header line
        body_start = i
        break

    header = "\n".join(header_lines).strip("\n")
    body = "\n".join(lines[body_start:]).lstrip("\n")
    return header, body


def parse_headers(header: str) -> dict:
    """
    Extract selected email header fields from a header block.

    Extracts:
    - From
    - To
    - Subject
    - Date
    - Cc (optional)
    """
    headers = {}
    for line in header.split("\n"):
        low = line.lower()
        if low.startswith("from:"):
            headers["from"] = line[5:].strip()
        elif low.startswith("to:"):
            headers["to"] = line[3:].strip()
        elif low.startswith("subject:"):
            headers["subject"] = line[8:].strip()
        elif low.startswith("date:"):
            headers["date"] = line[5:].strip()
        elif low.startswith("cc:"):
            headers["cc"] = line[3:].strip()
    return headers


def normalize_spaces(text: str) -> str:
    """
    Normalize whitespace in a text block.

    - Collapses consecutive spaces or tabs into a single space
    - Collapses 3 or more newlines into 2 newlines
    - Strips leading and trailing whitespace
    """
    text = re.sub(r"[ \t]+", " ", text or "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_quoted_lines(text: str) -> str:
    """
    Remove quoted lines from an email body.

    Lines whose first non-whitespace character is '>' are removed.
    """
    lines = (text or "").split("\n")
    lines = [ln for ln in lines if not ln.lstrip().startswith(">")]
    return "\n".join(lines)


def _drop_forward_mini_header_block(lines):
    """
    In forwarded content, remove a short block of header-like lines:
    From:, Sent by:, To:, cc:, Subject: (until first blank line after seeing any).
    """
    j = 0
    saw_headerish = False

    # Allow a one-liner like: 'Mark Whitt@ENRON on 02/08/2001 03:44 PM MST'
    if j < len(lines) and re.search(r"(?i)\bon\s+\d{1,2}/\d{1,2}/\d{4}\b", lines[j]):
        j += 1
        saw_headerish = True

    while j < len(lines):
        ln = lines[j].strip()
        if ln == "":
            if saw_headerish:
                return lines[j + 1 :]
            return lines
        if FORWARD_MINI_HEADER_RE.match(ln):
            saw_headerish = True
            j += 1
            continue
        break

    return lines


def unwrap_forwarded(text: str) -> str:
    """
    Remove Enron forward wrapper divider(s) while keeping the forwarded message content.
    Handles nested forwards by repeatedly unwrapping when a divider is found.
    """
    if not text:
        return ""

    lines = text.split("\n")

    def drop_leading_dividers(ls):
        i = 0
        while i < len(ls):
            if FORWARD_DIVIDER_RE.match(ls[i]):
                i += 1
                if i < len(ls) and FORWARD_TIMEBAR_RE.match(ls[i].strip()):
                    i += 1
                while i < len(ls) and ls[i].strip() == "":
                    i += 1
                continue
            if ls[i].strip() == "":
                i += 1
                continue
            break
        return ls[i:]

    # unwrap at start
    lines = drop_leading_dividers(lines)
    lines = _drop_forward_mini_header_block(lines)

    out = []
    i = 0
    while i < len(lines):
        if FORWARD_DIVIDER_RE.match(lines[i]):
            # drop this divider and unwrap the following block
            i += 1
            if i < len(lines) and FORWARD_TIMEBAR_RE.match(lines[i].strip()):
                i += 1
            while i < len(lines) and lines[i].strip() == "":
                i += 1
            tail = lines[i:]
            tail = _drop_forward_mini_header_block(tail)
            lines = tail
            i = 0
            continue

        out.append(lines[i])
        i += 1

    return "\n".join(out).strip()


def truncate_at_reply(text: str) -> str:
    """
    Truncate an email body at the start of a quoted reply chain.

    Practical rule for this dataset:
    - If a reply marker appears very early (e.g. the body is *only* an "Original Message"
      block because the email is a forward), we keep it rather than truncating to empty.
    - We intentionally do NOT truncate on "Forwarded by" markers (handled by unwrap_forwarded()).
    """
    txt = text or ""
    earliest = None
    for pat in REPLY_CUTOFF_PATTERNS:
        m = pat.search(txt)
        if m:
            if earliest is None or m.start() < earliest:
                earliest = m.start()

    if earliest is None:
        return txt.strip()

    # If the marker is at/near the start, don't truncate away the whole message.
    if earliest < 80:
        return txt.strip()

    return txt[:earliest].strip()


def normalize_newlines(text: str) -> str:
    """
    Convert all newline variants to '\n' and collapse excessive blank lines.
    """
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Optional: collapse 3+ blank lines to max 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def parse_and_clean_email(raw_msg: str) -> dict:
    """
    Parse a raw email message and produce a cleaned representation suitable for retrieval.

    New dataset support:
    - Optional first line: 'INFO: <python-literal>' (ground-truth tuple etc.)
    - Headers may contain blank lines between fields.
    - Many emails are pure forwards; we unwrap forward wrappers instead of truncating them away.

    Returns:
      dict with:
        - info (parsed INFO payload or None)
        - from, to, cc, date, subject
        - body_base, text_base, len_base
    """
    info, email_text = split_info_and_email(raw_msg)

    header, body = split_headers_body(email_text)
    headers = parse_headers(header)

    subject = headers.get("subject", "").strip()

    # body_base = normalize_spaces(body)
    # body_base = unwrap_forwarded(body_base)
    # body_base = remove_quoted_lines(body_base)
    # body_base = truncate_at_reply(body_base)


    body_base = drop_short_pleasantries(body)
    # body_base = drop_lonely_name_lines(body_base)
    body_base = normalize_newlines(body_base)
    body_base = unwrap_forwarded(body_base)              # removes "Forwarded by..." wrappers, keeps content
    body_base = remove_reply_header_blocks(body_base)    # removes From/Sent/To/Subject blocks inside threads
    body_base = remove_original_message_lines(body_base) # removes the "-----Original Message-----" separator lines
    body_base = remove_attachment_placeholders(body_base)
    body_base = normalize_spaces(body_base)


    text_base = f"{subject} {body_base}".strip()

    return {
        # "info": info,
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        # "cc": headers.get("cc", ""),
        "date": headers.get("date", ""),
        "subject": subject,
        "body_base": body_base,
        "text_base": text_base,
        "len_base": len(text_base),
    }
