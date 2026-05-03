from dataclasses import dataclass

import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder

from config import EMBEDDING_MODEL, RERANKER_MODEL, CHROMA_PATH, CHROMA_COLLECTION
from embed import get_chroma_collection


@dataclass
class BM25Index:
    bm25:  BM25Okapi
    docs:  list[str]
    metas: list[dict]


def build_bm25_index(collection: chromadb.Collection) -> BM25Index:
    """Lädt alle Chunks aus ChromaDB und baut einen BM25-Index. Läuft einmal pro Experiment."""
    print("BM25-Index wird aufgebaut...", flush=True)
    result    = collection.get(include=["documents", "metadatas"])
    docs      = result["documents"]
    metas     = result["metadatas"]
    tokenized = [doc.lower().split() for doc in docs]
    print(f"BM25-Index fertig — {len(docs):,} Chunks indiziert.")
    return BM25Index(bm25=BM25Okapi(tokenized), docs=docs, metas=metas)


def search_bm25(query: str, index: BM25Index, top_k: int) -> list[dict]:
    scores      = index.bm25.get_scores(query.lower().split())
    top_indices = scores.argsort()[::-1][:top_k]
    return [
        {
            "chunk_text":     index.docs[i],
            "article_id":     index.metas[i]["article_id"],
            "chunk_index":    index.metas[i].get("chunk_index", 0),
            "title":          index.metas[i].get("title", ""),
            "category":       index.metas[i].get("category", ""),
            "author":         index.metas[i].get("author", ""),
            "published_date": index.metas[i].get("published_date", ""),
            "bm25_score":     float(scores[i]),
        }
        for i in top_indices
    ]


def reciprocal_rank_fusion(ranked_lists: list[list[dict]], k: int = 60) -> list[dict]:
    """Kombiniert mehrere Ranglisten per RRF. Chunks die in beiden Listen auftauchen
    bekommen höhere Scores — k=60 dämpft den Effekt der Top-Plätze."""
    scores:    dict[str, float] = {}
    chunk_map: dict[str, dict]  = {}

    for ranked_list in ranked_lists:
        for rank, chunk in enumerate(ranked_list, start=1):
            cid = f"{chunk['article_id']}_{chunk['chunk_index']}"
            scores[cid]    = scores.get(cid, 0.0) + 1.0 / (k + rank)
            chunk_map[cid] = chunk

    return [
        {**chunk_map[cid], "rrf_score": scores[cid]}
        for cid in sorted(scores, key=lambda x: scores[x], reverse=True)
    ]


def load_models(use_reranking: bool = False) -> tuple:
    model    = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)
    reranker = CrossEncoder(RERANKER_MODEL) if use_reranking else None
    return model, reranker


_QUERY_INSTRUCTION = (
    "Instruct: Gegeben eine Suchanfrage auf Deutsch, finde relevante Nachrichtenartikel "
    "aus dem NZZ-Archiv, die die Frage beantworten.\nQuery: "
)


def embed_query(model: SentenceTransformer, query: str) -> list[float]:
    # Qwen3 braucht eine Task-Instruction vor der Query
    return model.encode(
        _QUERY_INSTRUCTION + query,
        normalize_embeddings=True,
    ).tolist()


def search(
    collection: chromadb.Collection,
    query_embedding: list[float],
    top_k: int = 20,
) -> list[dict]:
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "chunk_text":       doc,
            "article_id":       meta["article_id"],
            "chunk_index":      meta["chunk_index"],
            "title":            meta["title"],
            "category":         meta.get("category", ""),
            "author":           meta.get("author", ""),
            "published_date":   meta.get("published_date", ""),
            "similarity_score": 1 - dist,
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


def rerank(
    query: str,
    chunks: list[dict],
    reranker: CrossEncoder,
    top_k: int = 5,
) -> list[dict]:
    pairs  = [(query, chunk["chunk_text"]) for chunk in chunks]
    scores = reranker.predict(pairs)
    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = float(score)
    return sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)[:top_k]


def retrieve(
    query:           str,
    model:           SentenceTransformer,
    collection:      chromadb.Collection,
    reranker:        CrossEncoder = None,
    top_k_retrieval: int = 20,
    top_k_rerank:    int = 5,
    bm25_index:      BM25Index = None,
    rrf_k:           int = 60,
) -> list[dict]:
    query_embedding = embed_query(model, query)
    dense_chunks    = search(collection, query_embedding, top_k=top_k_retrieval)

    if bm25_index is not None:
        bm25_chunks = search_bm25(query, bm25_index, top_k=top_k_retrieval)
        chunks      = reciprocal_rank_fusion([dense_chunks, bm25_chunks], k=rrf_k)
    else:
        chunks = dense_chunks

    if reranker is not None:
        return rerank(query, chunks, reranker, top_k=top_k_rerank)

    return chunks[:top_k_rerank]


if __name__ == "__main__":
    from config import USE_RERANKING

    collection      = get_chroma_collection(CHROMA_PATH, CHROMA_COLLECTION)
    model, reranker = load_models(use_reranking=USE_RERANKING)

    query   = "Welche Forderungen stellt die Gewerkschaft zu All-in-Verträgen?"
    results = retrieve(query, model, collection, reranker)

    for r in results:
        meta = f"[{r['category']}]"
        if r.get("author"):
            meta += f" {r['author']}"
        if r.get("published_date"):
            meta += f" ({r['published_date']})"
        print(f"{meta}  {r['title'][:60]}  score: {r['similarity_score']:.3f}")
