# ── Data Source ───────────────────────────────────────────────────────────────
#switch between kaggle and nzz api
DATA_SOURCE = "kaggle"  # "kaggle" | "nzz_api"

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# ── Kaggle Settings ───────────────────────────────────────────────────────────
KAGGLE_DATASET  = "tblock/10kgnad"
KAGGLE_TRAIN    = os.path.join(BASE_DIR, "data", "raw", "train.csv")
KAGGLE_TEST     = os.path.join(BASE_DIR, "data", "raw", "test.csv")
KAGGLE_ARTICLES = os.path.join(BASE_DIR, "data", "raw", "articles.csv")

# ── NZZ API Settings (noch nicht aktiv) ──────────────────────────────────────
NZZ_API_URL     = "placeholder"   
NZZ_API_KEY     = ""                      

# ── Preprocessing ─────────────────────────────────────────────────────────────
MIN_TEXT_LENGTH = 100   # Artikel kürzer als X Zeichen werden gefiltert

# ── Chunking ──────────────────────────────────────────────────────────────────
CHUNK_SIZE    = 200   # Wörter pro Chunk
CHUNK_OVERLAP = 50    # Überlappung zwischen Chunks in Wörtern

# ── Embedding ─────────────────────────────────────────────────────────────────
# pick model from https://huggingface.co/spaces/mteb/leaderboard (Wichtig: schauen das es muli ling ist oder nur deutsch)
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"

# ── Retrieval ─────────────────────────────────────────────────────────────────
RERANKER_MODEL = "cross-encoder/msmarco-MiniLM-L6-en-de-v1"

# ── Reranking ─────── ─────────────────────────────────────────────────────────
USE_RERANKING = False