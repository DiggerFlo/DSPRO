"""Evaluation — retrieval and answer quality metrics."""

import json
import math


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


def precision_at_k(article_ids: list[str], relevant_ids: set[str], k: int) -> float:
    hits = sum(1 for id_ in article_ids[:k] if id_ in relevant_ids)
    return hits / k if k > 0 else 0.0


def recall_at_k(article_ids: list[str], relevant_ids: set[str], k: int) -> float:
    hits = sum(1 for id_ in article_ids[:k] if id_ in relevant_ids)
    return hits / len(relevant_ids) if relevant_ids else 0.0


def mrr(article_ids: list[str], relevant_ids: set[str]) -> float:
    for i, id_ in enumerate(article_ids, start=1):
        if id_ in relevant_ids:
            return 1.0 / i
    return 0.0


def ndcg_at_k(article_ids: list[str], relevant_ids: set[str], k: int) -> float:
    dcg  = sum(
        1.0 / math.log2(i + 2)
        for i, id_ in enumerate(article_ids[:k])
        if id_ in relevant_ids
    )
    idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(relevant_ids), k)))
    return dcg / idcg if idcg > 0 else 0.0


def evaluate_retrieval(results: list[dict], relevant_ids: list[str], k: int = 5) -> dict:
    """Compute retrieval metrics for one query.

    Results are deduplicated at article level before computing —
    ensures metrics stay in [0, 1] even when multiple chunks per article are returned.
    """
    article_ids = _dedupe_article_ids(results)
    rel_set     = set(relevant_ids)

    return {
        "hit_at_1":         hit_at_k(article_ids, rel_set, 1),
        "hit_at_3":         hit_at_k(article_ids, rel_set, 3),
        f"hit_at_{k}":      hit_at_k(article_ids, rel_set, k),
        f"precision_at_{k}": precision_at_k(article_ids, rel_set, k),
        f"recall_at_{k}":   recall_at_k(article_ids, rel_set, k),
        "mrr":              mrr(article_ids, rel_set),
        f"ndcg_at_{k}":     ndcg_at_k(article_ids, rel_set, k),
    }


# ── Generation Metrics ─────────────────────────────────────────────────────────

def _token_overlap_f1(predicted: str, expected: str) -> float:
    pred_tokens = set(predicted.lower().split())
    exp_tokens  = set(expected.lower().split())
    if not exp_tokens or not pred_tokens:
        return 0.0
    overlap   = len(pred_tokens & exp_tokens)
    precision = overlap / len(pred_tokens)
    recall    = overlap / len(exp_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def evaluate_answers(predicted: str, expected: str) -> dict:
    """Token-overlap F1 as a lightweight proxy for ROUGE-L."""
    return {"rouge_l_approx": _token_overlap_f1(predicted, expected)}
