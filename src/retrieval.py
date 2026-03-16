"""Retrieval pipeline — semantic search with reranking."""
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, CrossEncoder
from supabase import create_client, Client
from config import EMBEDDING_MODEL, RERANKER_MODEL

load_dotenv()

def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def embed_query(model: SentenceTransformer, query: str) -> list[float]:
    """Embed a user query with the same model used for documents."""
    prefixed = f"query: {query}"
    embedding = model.encode(
        prefixed,
        normalize_embeddings=True,
    )
    return embedding.tolist()

def search(client: Client, query_embedding: list[float], top_k: int = 20) -> list[dict]:
    """Retrieve top-k chunks from Supabase using vector similarity."""
    result = client.rpc("match_chunks", {
        "query_embedding": query_embedding,
        "match_count":     top_k,
    }).execute()
    return result.data

def rerank(query: str, chunks: list[dict], reranker: CrossEncoder, top_k: int = 5) -> list[dict]:
    pairs  = [(query, chunk["chunk_text"]) for chunk in chunks]
    scores = reranker.predict(pairs)
    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = float(score)
    reranked = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]

def retrieve(
    query:           str,
    model:           SentenceTransformer,
    client:          Client,
    reranker:        CrossEncoder = None,
    top_k_retrieval: int = 20,
    top_k_rerank:    int = 5,
) -> list[dict]:
    query_embedding = embed_query(model, query)
    chunks          = search(client, query_embedding, top_k=top_k_retrieval)

    if reranker is not None:
        return rerank(query, chunks, reranker, top_k=top_k_rerank)
    
    return chunks[:top_k_rerank]