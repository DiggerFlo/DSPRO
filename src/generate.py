import os
import ollama

from config import LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_KEEP_ALIVE, MIN_RELEVANCE_SCORE

_PROMPTS_DIR        = os.path.join(os.path.dirname(__file__), "prompts")
_MIN_SIMILARITY_SCORE = 0.35  # Fallback wenn kein Reranker aktiv


def _load_prompt(filename: str) -> str:
    with open(os.path.join(_PROMPTS_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()


def _merge_chunks_by_article(chunks: list[dict]) -> list[dict]:
    """Chunks desselben Artikels zusammenführen, Reihenfolge nach Retrieval-Rank."""
    seen_articles: dict[str, dict] = {}
    ordered_ids:   list[str]       = []

    for chunk in chunks:
        aid = chunk["article_id"]
        if aid not in seen_articles:
            seen_articles[aid] = {**chunk, "_parts": [(chunk["chunk_index"], chunk["chunk_text"])]}
            ordered_ids.append(aid)
        else:
            seen_articles[aid]["_parts"].append((chunk["chunk_index"], chunk["chunk_text"]))

    merged = []
    for aid in ordered_ids:
        entry = seen_articles[aid]
        parts = sorted(entry["_parts"], key=lambda x: x[0])
        entry["chunk_text"] = "\n\n[...]\n\n".join(text for _, text in parts)
        del entry["_parts"]
        merged.append(entry)
    return merged


def _build_context(chunks: list[dict]) -> str:
    merged = _merge_chunks_by_article(chunks)
    parts  = []
    for i, chunk in enumerate(merged, start=1):
        meta = f"[{i}] Artikel-ID: {chunk['article_id']}"
        if chunk.get("title"):
            meta += f" | Titel: {chunk['title']}"
        if chunk.get("published_date"):
            meta += f" | Datum: {chunk['published_date']}"
        if chunk.get("category"):
            meta += f" | Ressort: {chunk['category']}"
        parts.append(f"{meta}\n{chunk['chunk_text']}")
    return "\n\n---\n\n".join(parts)


def fetch_full_article_chunks(article_ids: list[str], collection) -> list[dict]:
    """Holt alle Chunks der gegebenen Artikel aus ChromaDB, sortiert nach chunk_index.
    Artikel-Reihenfolge entspricht dem Retrieval-Ranking."""
    if not article_ids:
        return []

    result  = collection.get(
        where={"article_id": {"$in": article_ids}},
        include=["documents", "metadatas"],
    )
    grouped: dict[str, list[dict]] = {aid: [] for aid in article_ids}

    for doc, meta in zip(result["documents"], result["metadatas"]):
        aid = meta["article_id"]
        if aid in grouped:
            grouped[aid].append({
                "chunk_text":     doc,
                "article_id":     aid,
                "chunk_index":    meta.get("chunk_index", 0),
                "title":          meta.get("title", ""),
                "category":       meta.get("category", ""),
                "published_date": meta.get("published_date", ""),
            })

    chunks = []
    for aid in article_ids:
        chunks.extend(sorted(grouped[aid], key=lambda x: x["chunk_index"]))
    return chunks


def _is_relevant(chunks: list[dict]) -> bool:
    if not chunks:
        return False
    top = chunks[0]
    if "rerank_score" in top:
        return top["rerank_score"] >= MIN_RELEVANCE_SCORE
    return top.get("similarity_score", 0.0) >= _MIN_SIMILARITY_SCORE


def generate(query: str, context_chunks: list[dict]) -> str:
    if not _is_relevant(context_chunks):
        return "Zu dieser Anfrage wurden keine ausreichend relevanten Artikel im NZZ-Archiv gefunden."

    system_prompt = _load_prompt("system_prompt.md")
    context       = _build_context(context_chunks)
    user_message  = f"Frage: {query}\n\nQuellen:\n{context}"

    response = ollama.chat(
        model=LLM_MODEL,
        options={"temperature": LLM_TEMPERATURE, "num_predict": LLM_MAX_TOKENS},
        keep_alive=LLM_KEEP_ALIVE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
    )
    return response.message.content.strip()


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))

    from config import (
        CHROMA_PATH, CHROMA_COLLECTION,
        EMBEDDING_MODEL, RERANKER_MODEL, USE_RERANKING,
        EVAL_TOP_K_RETRIEVAL, EVAL_TOP_K_FINAL,
    )
    from embed import get_chroma_collection
    from retrieval import load_models, retrieve

    query = input("Frage: ").strip() if len(sys.argv) < 2 else sys.argv[1]

    collection      = get_chroma_collection(CHROMA_PATH, CHROMA_COLLECTION)
    model, reranker = load_models(use_reranking=USE_RERANKING)
    chunks = retrieve(
        query, model, collection, reranker,
        top_k_retrieval=EVAL_TOP_K_RETRIEVAL,
        top_k_rerank=EVAL_TOP_K_FINAL,
    )

    print(f"\nTop-{len(chunks)} Quellen:")
    for i, c in enumerate(chunks, 1):
        score = c.get("rerank_score", c.get("similarity_score", 0))
        print(f"  [{i}] {c['title'][:60]}  (score: {score:.3f})")

    print("\nAntwort:")
    print(generate(query, chunks))
