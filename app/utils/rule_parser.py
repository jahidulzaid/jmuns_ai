from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, List
from app.schemas.parse_items import LineItem


MONEY_RE = re.compile(
    r"(?P<dollar>\$)\s*(?P<amt>\d+(?:\.\d+)?)|(?P<amt2>\d+(?:\.\d+)?)\s*(?:dollars|usd)\b",
    re.IGNORECASE,
)

QTY_RE_LIST = [
    re.compile(r"\bqty\s*(?P<q>\d+)\b", re.IGNORECASE),
    re.compile(r"\bquantity\s*(?P<q>\d+)\b", re.IGNORECASE),
    re.compile(r"\bx(?P<q>\d+)\b", re.IGNORECASE),
    re.compile(r"\b(?P<q>\d+)\s*(?:units|unit|pcs|pieces)\b", re.IGNORECASE),
]

EACH_RE = re.compile(r"\b(each|per\s+item|per\s+unit)\b", re.IGNORECASE)

TAX_YES_RE = re.compile(r"\b(taxable|include\s+tax|with\s+tax)\b", re.IGNORECASE)
TAX_NO_RE = re.compile(r"\b(no\s+tax|tax\s+exempt|non\s*taxable|not\s+taxable)\b", re.IGNORECASE)

MARKUP_RE = re.compile(r"\b(markup\s*)?(?P<m>\d{1,3}(?:\.\d+)?)\s*%\b", re.IGNORECASE)


def _first_money(text: str) -> Optional[float]:
    m = MONEY_RE.search(text)
    if not m:
        return None
    amt = m.group("amt") or m.group("amt2")
    try:
        return float(amt)
    except Exception:
        return None


def _extract_qty(text: str) -> Optional[int]:
    for qre in QTY_RE_LIST:
        m = qre.search(text)
        if m:
            try:
                return int(m.group("q"))
            except Exception:
                return None
    return None


def _extract_taxable(text: str, default_taxable: bool) -> bool:
    if TAX_NO_RE.search(text):
        return False
    if TAX_YES_RE.search(text):
        return True
    return default_taxable


def _extract_markup(text: str) -> Optional[float]:
    m = MARKUP_RE.search(text)
    if not m:
        return None
    try:
        val = float(m.group("m"))
        if 0.0 <= val <= 100.0:
            return val
    except Exception:
        return None
    return None


def _clean_description(text: str) -> str:
    t = text.strip()

    # remove money tokens
    t = MONEY_RE.sub("", t)

    # remove qty tokens
    for qre in QTY_RE_LIST:
        t = qre.sub("", t)

    # remove tax/markup keywords
    t = TAX_YES_RE.sub("", t)
    t = TAX_NO_RE.sub("", t)
    t = MARKUP_RE.sub("", t)

    # remove "each" tokens
    t = EACH_RE.sub("", t)

    # extra cleanup
    t = re.sub(r"\s{2,}", " ", t).strip(" -,:")
    return t.strip()


def parse_line_to_item(line: str, default_taxable: bool = True) -> LineItem:
    rate = _first_money(line)
    qty = _extract_qty(line) or 1
    taxable = _extract_taxable(line, default_taxable=default_taxable)
    markup = _extract_markup(line)
    desc = _clean_description(line)

    # If user wrote "$250 each, quantity 2" => rate is per-item; qty already extracted
    # If user wrote total-only without “each”, we still treat it as rate (common estimate behavior)

    return LineItem(
        description=desc or line.strip(),
        rate=rate,
        quantity=qty,
        taxable=taxable,
        markupPercent=markup,
    )


def compute_confidence(items: List[LineItem]) -> float:
    if not items:
        return 0.0

    # Simple heuristic:
    # + rate present => +0.35
    # + qty present (always >=1) but if extracted from text? we infer via qty>1 => +0.15
    # + description non-trivial => +0.35
    # + taxable inferred/explicit => +0.15 (always exists, but if tax keywords present we can boost)
    scores = []
    for it in items:
        s = 0.0
        if it.rate is not None:
            s += 0.35
        if it.quantity > 1:
            s += 0.15
        if it.description and len(it.description.strip()) >= 6:
            s += 0.35
        # taxable always exists; we assume some confidence baseline
        s += 0.15
        scores.append(min(1.0, s))

    return round(sum(scores) / len(scores), 2)
