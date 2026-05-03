import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, CHROMA_PATH, CHROMA_COLLECTION


def get_chroma_collection(path: str, collection_name: str) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=path)
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def load_model(model_name: str) -> SentenceTransformer:
    print(f"Lädt Embedding-Modell: {model_name}")
    return SentenceTransformer(model_name, trust_remote_code=True)


def embed_chunks(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    print(f"Generiere Embeddings für {len(texts)} Chunks...")
    embeddings = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return embeddings.tolist()


_BASE_META_COLS     = ["article_id", "chunk_index", "title", "category"]
_OPTIONAL_META_COLS = ["author", "published_date"]


def upload_to_chroma(
    collection: chromadb.Collection,
    df: pd.DataFrame,
    embeddings: list[list[float]],
) -> None:
    print(f"Speichere {len(embeddings)} Chunks in ChromaDB...")
    meta_cols  = _BASE_META_COLS + [c for c in _OPTIONAL_META_COLS if c in df.columns]
    batch_size = 500

    for start in range(0, len(df), batch_size):
        batch      = df.iloc[start : start + batch_size]
        batch_embs = embeddings[start : start + batch_size]
        collection.upsert(
            ids        = batch["chunk_id"].tolist(),
            embeddings = batch_embs,
            documents  = batch["chunk_text"].tolist(),
            metadatas  = batch[meta_cols].to_dict(orient="records"),
        )

    print(f"Fertig — {len(embeddings)} Chunks gespeichert.")
