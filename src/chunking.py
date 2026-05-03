import uuid
import pandas as pd
from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_article(row: pd.Series) -> list[dict]:
    words  = row["body"].split()
    chunks = []
    start  = 0
    index  = 0

    # NZZ liefert eine echte article_id, Kaggle-Daten nicht
    article_id = str(
        row.get("article_id")
        or uuid.uuid5(uuid.NAMESPACE_DNS, row["title"] + row["body"][:50])
    )

    while start < len(words):
        end        = start + CHUNK_SIZE
        chunk_text = row["title"] + ". " + " ".join(words[start:end])

        if len(chunk_text.strip()) > 20:
            chunks.append({
                "article_id":     article_id,
                "chunk_id":       f"{article_id}-{index}",
                "chunk_index":    index,
                "chunk_text":     chunk_text,
                "title":          row["title"],
                "category":       row.get("category", ""),
                "author":         row.get("author", ""),
                "published_date": row.get("published_date", ""),
            })
            index += 1

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def chunk_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    all_chunks = []
    for _, row in df.iterrows():
        all_chunks.extend(chunk_article(row))
    return pd.DataFrame(all_chunks)
