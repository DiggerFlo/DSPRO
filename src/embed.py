"""Embedding pipeline — generates vector embeddings and stores them in ChromaDB."""

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, CHROMA_PATH, CHROMA_COLLECTION


def get_chroma_collection(path: str, collection_name: str) -> chromadb.Collection:
    """Initialize persistent ChromaDB client and return the collection."""
    client = chromadb.PersistentClient(path=path)
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def load_model(model_name: str) -> SentenceTransformer:
    """Load and return the specified embedding model."""
    print(f"Lädt embedding model: {model_name}")
    return SentenceTransformer(model_name)


def embed_chunks(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    """Generate normalized embeddings for a list of texts."""
    print(f"Generiere Embeddings für {len(texts)} Chunks...")
    prefixed = [f"passage: {t}" for t in texts]
    embeddings = model.encode(
        prefixed,
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
    """Upload chunks with embeddings and metadata to ChromaDB."""
    print(f"Speichere {len(embeddings)} Chunks in ChromaDB...")

    meta_cols = _BASE_META_COLS + [c for c in _OPTIONAL_META_COLS if c in df.columns]

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


if __name__ == "__main__":
    import argparse
    import os
    from preprocess import preprocess, _load_nzz_json
    from chunking import chunk_dataframe

    parser = argparse.ArgumentParser(description="Artikel embedden und in ChromaDB laden.")
    parser.add_argument(
        "--month",
        type=str,
        default=None,
        metavar="YYYY_MM",
        help="Nur einen Monat laden, z.B. --month 2025_12. Ohne Argument: alle Monate.",
    )
    args = parser.parse_args()

    if args.month:
        base_dir   = os.path.dirname(os.path.dirname(__file__))
        glob_pattern = os.path.join(base_dir, "data", "raw", f"articles_{args.month}.json")
        print(f"Lade Monat: {args.month}")
        df = preprocess(_load_nzz_json(glob_pattern))
    else:
        from preprocess import load_dataset
        print("Lade alle Monate …")
        df = preprocess(load_dataset())

    collection = get_chroma_collection(CHROMA_PATH, CHROMA_COLLECTION)
    model      = load_model(EMBEDDING_MODEL)

    chunks     = chunk_dataframe(df)
    embeddings = embed_chunks(model, chunks["chunk_text"].tolist())

    upload_to_chroma(collection, chunks, embeddings)
