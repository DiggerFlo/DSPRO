import json


def load_ground_truth(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _dedupe_article_ids(results: list[dict]) -> list[str]:
    # Mehrere Chunks pro Artikel → nur einmal zählen, Reihenfolge beibehalten
    seen = []
    for r in results:
        if r["article_id"] not in seen:
            seen.append(r["article_id"])
    return seen


def hit_at_k(article_ids: list[str], relevant_ids: set[str], k: int) -> float:
    return float(any(id_ in relevant_ids for id_ in article_ids[:k]))


def mrr(article_ids: list[str], relevant_ids: set[str]) -> float:
    for i, id_ in enumerate(article_ids, start=1):
        if id_ in relevant_ids:
            return 1.0 / i
    return 0.0


def evaluate_retrieval(results: list[dict], relevant_ids: list[str], k: int = 5) -> dict:
    article_ids = _dedupe_article_ids(results)
    rel_set     = set(relevant_ids)
    return {
        "hit_at_1":    hit_at_k(article_ids, rel_set, 1),
        f"hit_at_{k}": hit_at_k(article_ids, rel_set, k),
        "mrr":         mrr(article_ids, rel_set),
    }


def evaluate_faithfulness(answer: str, context_chunks: list[dict]) -> dict:
    """Misst wie stark die Antwort im Kontext verankert ist.
    Zählt den Anteil der Antwort-Tokens (>3 Zeichen) die im Kontext vorkommen.
    1.0 = vollständig aus Quellen, 0.0 = kein Überlapp."""
    context_tokens = set(
        " ".join(c["chunk_text"] for c in context_chunks).lower().split()
    )
    answer_tokens = [t for t in answer.lower().split() if len(t) > 3]
    if not answer_tokens:
        return {"faithfulness": 0.0}
    supported = sum(1 for t in answer_tokens if t in context_tokens)
    return {"faithfulness": supported / len(answer_tokens)}
