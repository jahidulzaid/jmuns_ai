from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI
from dotenv import load_dotenv

from app.schemas.parse_items import LineItem
from app.utils.json_safety import extract_json_object

# Load env variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"  # fast + cheap + good extraction

SYSTEM_PROMPT = """
You extract estimate line items from contractor notes.

CRITICAL RULES:
- Return ONLY valid JSON
- Do NOT include markdown or explanations
- Do NOT guess missing values
- If a field is not explicitly present, return null

JSON SCHEMA:
{
  "items": [
    {
      "description": string,
      "rate": number|null,
      "quantity": number|null,
      "taxable": boolean|null,
      "markupPercent": number|null,
      "detail": string|null
    }
  ]
}
"""

USER_PROMPT_TEMPLATE = """
Text:
{TEXT}

Context:
{CONTEXT}

Extract estimate line items now.
"""


def extract_items_with_llm(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> List[LineItem]:

    if not text.strip():
        return []

    user_prompt = USER_PROMPT_TEMPLATE.format(
        TEXT=text.strip(),
        CONTEXT=json.dumps(context or {}, ensure_ascii=False),
    )

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},  # 🔒 JSON-only guarantee
        timeout=20,
    )

    raw = response.choices[0].message.content or ""

    parsed = extract_json_object(raw)
    items = parsed.get("items", [])

    results: List[LineItem] = []

    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            results.append(LineItem(**item))
        except Exception:
            # skip invalid rows instead of crashing
            continue

    return results
