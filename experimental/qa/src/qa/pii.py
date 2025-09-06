"""Simple PII sanitization helpers for texts and nested payloads."""

import re
from typing import Any, Dict, Tuple

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(
    r"(?:\+\d{1,3}[ \-]?)?(?:\(?\d{2,4}\)?[ \-]?)?\d{3,4}[ \-]?\d{3,4}"
)
CC_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


def sanitize_text(text: str) -> Tuple[str, Dict[str, int]]:
    """Replace common PII patterns with placeholders and return counts found."""
    counts = {"emails": 0, "phones": 0, "cards": 0}
    if not isinstance(text, str):
        return text, counts

    def _sub_email(m):
        counts["emails"] += 1
        return "[REDACTED_EMAIL]"

    def _sub_phone(m):
        counts["phones"] += 1
        return "[REDACTED_PHONE]"

    def _sub_card(m):
        counts["cards"] += 1
        return "[REDACTED_CARD]"

    t = EMAIL_RE.sub(_sub_email, text)
    t = CC_RE.sub(_sub_card, t)
    t = PHONE_RE.sub(_sub_phone, t)
    return t, counts


def sanitize_payload(payload: Any) -> Tuple[Any, Dict[str, int]]:
    """Recursively sanitize strings inside payload dict/list and aggregate counts."""
    agg = {"emails": 0, "phones": 0, "cards": 0}

    if isinstance(payload, str):
        t, counts = sanitize_text(payload)
        for k in agg:
            agg[k] += counts.get(k, 0)
        return t, agg
    if isinstance(payload, dict):
        out = {}
        for k, v in payload.items():
            nv, counts = sanitize_payload(v)
            out[k] = nv
            for key in agg:
                agg[key] += counts.get(key, 0)
        return out, agg
    if isinstance(payload, list):
        out_list = []
        for v in payload:
            nv, counts = sanitize_payload(v)
            out_list.append(nv)
            for key in agg:
                agg[key] += counts.get(key, 0)
        return out_list, agg
    # other types
    return payload, agg
