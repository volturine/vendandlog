import hashlib
import json


def event_hash(prev_hash: str, listing_id: int, kind: str, summary: str, detail: str | None, created_at: str) -> str:
    """Content-chained hash so every log entry commits to the one before it."""
    payload = json.dumps(
        {
            'prev': prev_hash,
            'listing_id': listing_id,
            'kind': kind,
            'summary': summary,
            'detail': detail,
            'created_at': created_at,
        },
        sort_keys=True,
        separators=(',', ':'),
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:12]


GENESIS = '000000000000'


def trust_score(
    sales_count: int,
    ratings_received_stars: list[int],
    flags_upheld: int,
    listings_count: int,
) -> int:
    """HN-style karma: earned slowly through visible behavior, cheap to lose."""
    positive = sum(1 for s in ratings_received_stars if s >= 4)
    negative = sum(1 for s in ratings_received_stars if s <= 2)
    return max(
        0,
        15 * sales_count + 8 * positive - 30 * negative - 75 * flags_upheld + 2 * listings_count,
    )


def positive_pct(ratings_received_stars: list[int]) -> int:
    if not ratings_received_stars:
        return 100
    positive = sum(1 for s in ratings_received_stars if s >= 4)
    return round(100 * positive / len(ratings_received_stars))
