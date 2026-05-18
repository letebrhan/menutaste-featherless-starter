from __future__ import annotations

from typing import List


def clean_ingredients(raw: str) -> List[str]:
    items = []
    for part in raw.replace("\n", ",").split(","):
        item = " ".join(part.strip().lower().split())
        if item:
            items.append(item)
    return items
