from __future__ import annotations
from typing import List
from app.schemas.parse_items import LineItem


def compute_confidence(items: List[LineItem]) -> float:
    if not items:
        return 0.0

    scores = []
    for it in items:
        s = 0.0
        if it.description and len(it.description.strip()) >= 4:
            s += 0.4
        if it.rate is not None:
            s += 0.25
        if it.quantity is not None:
            s += 0.15
        if it.taxable is not None:
            s += 0.1
        if it.markupPercent is not None:
            s += 0.1
        scores.append(min(1.0, s))

    return round(sum(scores) / len(scores), 2)
