"""Embedding pipeline — generates vector embeddings for all chunks."""
import os
import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from config import EMBEDDING_MODEL

load_dotenv()

def get_supabase_client() -> Client:
    """Initialize and return a Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def load_model(model_name: str) -> SentenceTransformer:
    """Load and return the specified embedding model."""
    print(f"Lädt embedding model: {model_name}")
    return SentenceTransformer(model_name)

def embed_chunks(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    print(f"Generiere Embeddings für {len(texts)} Chunks...")
    prefixed = [f"passage {t}" for t in texts]
    embedding = model.encode(
        prefixed,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return embedding.tolist()

def upload_articles(client: Client, df: pd.DataFrame):
    """Upload article metadata to Supabase."""
    print(f"Upload von {len(df)} Artikeln zu Supabase...")
    articles = df[["article_id", "title", "category"]].drop_duplicates("article_id")
    rows = articles.to_dict(orient="records")
    for row in rows:
        row["source"] = "10kgnad"
    client.table("articles").upsert(rows).execute()
    print(f"{len(rows)} Artikel hochgeladen")
    
def upload_chunks(client: Client, df: pd.DataFrame, embeddings: list[list[float]]):
    """Upload chunk embeddings to Supabase."""
    print(f"Upload von {len(embeddings)} Chunks zu Supabase...")
    df = df.copy()
    df["embedding"] = embeddings
    rows = df[["chunk_id", "article_id", "chunk_index",
               "chunk_text", "title", "category", "embedding"]].to_dict(orient="records")
    client.table("chunks").upsert(rows).execute()
    print(f"{len(rows)} Chunks hochgeladen")

if __name__ == "__main__":
    client = get_supabase_client()
    model  = load_model(EMBEDDING_MODEL)
    
    from preprocessing import load_dataset, preprocess
    from chunking import chunk_dataframe
    
    train        = preprocess(load_dataset("train"))
    train_chunks = chunk_dataframe(train)
    embeddings   = embed_chunks(model, train_chunks["chunk_text"].tolist())
    
    upload_articles(client, train_chunks)
    upload_chunks(client, train_chunks, embeddings)
