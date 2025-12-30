from __future__ import annotations

import json
import re
from typing import Any, Dict


_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json_object(text: str) -> Dict[str, Any]:
    text = (text or "").strip()

    # best case: valid JSON already
    try:
        return json.loads(text)
    except Exception:
        pass

    # fallback: find first {...} block
    m = _JSON_RE.search(text)
    if not m:
        return {"items": []}

    chunk = m.group(0)
    try:
        return json.loads(chunk)
    except Exception:
        return {"items": []}
