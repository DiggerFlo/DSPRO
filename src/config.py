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
CHUNK_SIZE    = 500   # Wörter pro Chunk
CHUNK_OVERLAP = 125    # Überlappung zwischen Chunks in Wörtern

# ── Embedding ─────────────────────────────────────────────────────────────────
# pick model from https://huggingface.co/spaces/mteb/leaderboard (Wichtig: schauen das es muli ling ist oder nur deutsch)
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"

# ── Retrieval ─────────────────────────────────────────────────────────────────
RERANKER_MODEL = "cross-encoder/msmarco-MiniLM-L6-en-de-v1"

# ── Reranking ─────── ─────────────────────────────────────────────────────────
USE_RERANKING = False

# ── MLflow ────────────────────────────────────────────────────────────────────
MLFLOW_TRACKING_URI   = f"sqlite:///{os.path.join(BASE_DIR, 'mlflow.db')}"
MLFLOW_EXPERIMENT     = "rag-evaluation"

# ── Evaluation ────────────────────────────────────────────────────────────────
EVAL_GROUND_TRUTH     = os.path.join(BASE_DIR, "data", "eval", "ground_truth.jsonl")
EVAL_TOP_K_RETRIEVAL  = 20   # Kandidaten die aus Supabase geholt werden
EVAL_TOP_K_FINAL      = 5    # Nach Reranking / finale Trefferzahl
ENABLE_GENERATION_EVAL = False  # Auf True setzen sobald generate.py implementiert ist