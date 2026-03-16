"""Chunking pipeline — splits processed articles into retrievable chunks."""

import uuid
import pandas as pd
from config import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_article(row: pd.Series) -> list[dict]:
    words  = row["body"].split()
    chunks = []
    start  = 0
    index  = 0

    while start < len(words):
        end        = start + CHUNK_SIZE
        chunk_text = row["title"] + ". " + " ".join(words[start:end])  # Titel voranstellen

        if len(chunk_text.strip()) > 20:
            article_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, row["title"] + row["body"][:50]))
            chunks.append({
                "article_id":  article_id,
                "chunk_id":    f"{article_id}-{index}",
                "chunk_index": index,
                "chunk_text":  chunk_text,
                "title":       row["title"],
                "category":    row["category"],
            })
            index += 1

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks

def chunk_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply chunking to the entire DataFrame."""
    all_chunks = []
    for _, row in df.iterrows():
        all_chunks.extend(chunk_article(row))
    return pd.DataFrame(all_chunks)

if __name__ == "__main__":
    from preprocessing import load_dataset, preprocess
    train = preprocess(load_dataset("train"))
    chunks = chunk_dataframe(train)
    print(f"Chunks: {len(chunks)}")
