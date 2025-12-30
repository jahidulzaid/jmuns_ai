from __future__ import annotations

from app.schemas.parse_items import ParseItemsRequest, ParseItemsResponse, LineItem
from app.services.llm_client import extract_items_with_llm
from app.utils.rule_confidence import compute_confidence


def parse_estimate_items(payload: ParseItemsRequest) -> ParseItemsResponse:
    items = extract_items_with_llm(
        text=payload.text,
        context=payload.context.model_dump() if payload.context else None,
    )

    # Basic cleanup: remove empty descriptions
    cleaned: list[LineItem] = []
    for it in items:
        if it.description and it.description.strip():
            cleaned.append(it)

    conf = compute_confidence(cleaned)

    notes = None
    if not cleaned:
        notes = "No line items found. Try separating tasks with new lines or semicolons."

    return ParseItemsResponse(items=cleaned, confidence=conf, notes=notes)
