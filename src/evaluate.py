"""Evaluation — retrieval and answer quality metrics."""

import json


def load_ground_truth(path: str) -> list[dict]:
    """Load evaluation samples from a JSONL file."""
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _dedupe_article_ids(results: list[dict]) -> list[str]:
    """Return article IDs in ranked order, deduplicated (chunks → articles)."""
    seen = []
    for r in results:
        if r["article_id"] not in seen:
            seen.append(r["article_id"])
    return seen


# ── Retrieval Metrics ──────────────────────────────────────────────────────────

def hit_at_k(article_ids: list[str], relevant_ids: set[str], k: int) -> float:
    return float(any(id_ in relevant_ids for id_ in article_ids[:k]))


def mrr(article_ids: list[str], relevant_ids: set[str]) -> float:
    for i, id_ in enumerate(article_ids, start=1):
        if id_ in relevant_ids:
            return 1.0 / i
    return 0.0


def evaluate_retrieval(results: list[dict], relevant_ids: list[str], k: int = 5) -> dict:
    """Compute retrieval metrics for one query.

    Results are deduplicated at article level before computing —
    ensures metrics stay in [0, 1] even when multiple chunks per article are returned.
    """
    article_ids = _dedupe_article_ids(results)
    rel_set     = set(relevant_ids)

    return {
        "hit_at_1":    hit_at_k(article_ids, rel_set, 1),
        f"hit_at_{k}": hit_at_k(article_ids, rel_set, k),
        "mrr":         mrr(article_ids, rel_set),
    }


def evaluate_faithfulness(answer: str, context_chunks: list[dict]) -> dict:
    """Measures how grounded the answer is in the retrieved context.

    Computed as the fraction of answer tokens (length > 3) that appear
    in the concatenated chunk texts — a proxy for hallucination detection.
    Score of 1.0 = fully grounded, 0.0 = no overlap with sources.
    """
    context_tokens = set(
        " ".join(c["chunk_text"] for c in context_chunks).lower().split()
    )
    answer_tokens = [t for t in answer.lower().split() if len(t) > 3]
    if not answer_tokens:
        return {"faithfulness": 0.0}
    supported = sum(1 for t in answer_tokens if t in context_tokens)
    return {"faithfulness": supported / len(answer_tokens)}
