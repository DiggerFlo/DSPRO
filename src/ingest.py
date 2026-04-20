"""Ingestion pipeline — loads, preprocesses, chunks, embeds and indexes articles."""

import argparse
import os

import chromadb

from config import CHROMA_PATH, CHROMA_COLLECTION, EMBEDDING_MODEL
from preprocess import _load_nzz_json, preprocess
from chunking import chunk_dataframe
from embed import get_chroma_collection, load_model, embed_chunks, upload_to_chroma


def ingest(month: str = None, reset: bool = False) -> None:
    """Run the full ingestion pipeline.

    Args:
        month: Optional month filter e.g. '2025_12'. None = all months.
        reset: If True, wipe the ChromaDB collection before indexing.
    """
    # 1. Load raw articles
    if month:
        base_dir     = os.path.dirname(os.path.dirname(__file__))
        glob_pattern = os.path.join(base_dir, "data", "raw", f"articles_{month}.json")
        print(f"Lade Monat: {month}")
        raw_df = _load_nzz_json(glob_pattern)
    else:
        print("Lade alle Monate...")
        raw_df = _load_nzz_json()

    # 2. Preprocess
    df = preprocess(raw_df)
    print(f"Artikel: {len(raw_df):,} geladen  →  {len(df):,} nach Preprocessing")

    # 3. Chunk
    chunks_df = chunk_dataframe(df)
    print(f"Chunks:  {len(chunks_df):,}")

    # 4. ChromaDB vorbereiten
    if reset:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        existing = [c.name for c in client.list_collections()]
        if CHROMA_COLLECTION in existing:
            client.delete_collection(CHROMA_COLLECTION)
            print("ChromaDB Collection geleert.")

    collection = get_chroma_collection(CHROMA_PATH, CHROMA_COLLECTION)

    # 5. Embed & upload
    model      = load_model(EMBEDDING_MODEL)
    embeddings = embed_chunks(model, chunks_df["chunk_text"].tolist())
    upload_to_chroma(collection, chunks_df, embeddings)

    print(f"\n✓ Indexierung abgeschlossen — {collection.count():,} Chunks in ChromaDB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NZZ-Artikel indexieren.")
    parser.add_argument(
        "--month", type=str, default=None, metavar="YYYY_MM",
        help="Nur einen Monat laden, z.B. --month 2025_12",
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="ChromaDB Collection vor dem Indexieren leeren",
    )
    args = parser.parse_args()
    ingest(month=args.month, reset=args.reset)
