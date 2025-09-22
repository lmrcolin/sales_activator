from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException
from typing import List, Dict
import time
import random

SEARCH_QUERIES = [
    'site:.com "event agency" "United States"',
    'site:.com "event planning" "corporate events"',
    'site:.com "destination management company" "USA"',
    'site:.com "incentive travel" "agency"',
    'site:.com "conference organizer" "United States"',
    'site:.com "exhibition organizer" "United States"',
]


def search_mice_companies(limit: int = 50) -> List[Dict]:
    results: List[Dict] = []
    with DDGS() as ddgs:
        per_q = max(2, limit // max(1, len(SEARCH_QUERIES)))
        for q in SEARCH_QUERIES:
            attempts = 0
            while attempts < 3:
                try:
                    for r in ddgs.text(q, max_results=per_q, region="wt-wt"):
                        results.append({
                            "title": r.get("title"),
                            "href": r.get("href"),
                            "body": r.get("body"),
                            "source": q,
                        })
                    # gentle throttle between queries
                    time.sleep(2 + random.random() * 2)
                    break
                except RatelimitException:
                    attempts += 1
                    time.sleep(8 * attempts)
                except Exception:
                    break
    # Deduplicate by href
    seen = set()
    deduped = []
    for r in results:
        href = r.get("href")
        if href and href not in seen:
            deduped.append(r)
            seen.add(href)
    return deduped[:limit]
