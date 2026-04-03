"""Retrieval pipeline — semantic search with optional reranking via ChromaDB."""

import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder

from config import EMBEDDING_MODEL, RERANKER_MODEL, CHROMA_PATH, CHROMA_COLLECTION
from embed import get_chroma_collection


def load_models(use_reranking: bool = False) -> tuple:
    """Load embedding model and optionally the reranker."""
    model    = SentenceTransformer(EMBEDDING_MODEL)
    reranker = CrossEncoder(RERANKER_MODEL) if use_reranking else None
    return model, reranker


def embed_query(model: SentenceTransformer, query: str) -> list[float]:
    """Embed a user query with the same model used for documents."""
    embedding = model.encode(
        f"query: {query}",
        normalize_embeddings=True,
    )
    return embedding.tolist()


def search(
    collection: chromadb.Collection,
    query_embedding: list[float],
    top_k: int = 20,
) -> list[dict]:
    """Retrieve top-k chunks from ChromaDB using cosine similarity."""
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "chunk_text":       doc,
            "article_id":       meta["article_id"],
            "chunk_index":      meta["chunk_index"],
            "title":            meta["title"],
            "category":         meta.get("category", ""),
            "author":           meta.get("author", ""),
            "published_date":   meta.get("published_date", ""),
            "similarity_score": 1 - dist,   # cosine distance → similarity
        })
    return chunks


def rerank(
    query: str,
    chunks: list[dict],
    reranker: CrossEncoder,
    top_k: int = 5,
) -> list[dict]:
    """Rerank chunks using a cross-encoder and return top-k."""
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
) -> list[dict]:
    """Full retrieval pipeline: embed → search → (optional) rerank."""
    query_embedding = embed_query(model, query)
    chunks          = search(collection, query_embedding, top_k=top_k_retrieval)

    if reranker is not None:
        return rerank(query, chunks, reranker, top_k=top_k_rerank)

    return chunks[:top_k_rerank]


if __name__ == "__main__":
    from config import USE_RERANKING

    collection     = get_chroma_collection(CHROMA_PATH, CHROMA_COLLECTION)
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
