import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# ── Datenquelle ───────────────────────────────────────────────────────────────
NZZ_JSON_GLOB = os.path.join(BASE_DIR, "data", "raw", "articles_*.json")

# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_PATH       = os.path.join(BASE_DIR, "data", "chroma")
CHROMA_COLLECTION = "chunks"

# ── Preprocessing ─────────────────────────────────────────────────────────────
MIN_TEXT_LENGTH = 100   # Artikel kürzer als X Zeichen werden gefiltert

# ── Chunking ──────────────────────────────────────────────────────────────────
CHUNK_SIZE    = 1000    # Wörter pro Chunk
CHUNK_OVERLAP = 250     # Überlappung zwischen Chunks in Wörtern

# ── Embedding ─────────────────────────────────────────────────────────────────
# Modell-Auswahl: https://huggingface.co/spaces/mteb/leaderboard
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"

# ── Retrieval & Reranking ─────────────────────────────────────────────────────
RERANKER_MODEL    = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
USE_RERANKING     = True

# ── MLflow ────────────────────────────────────────────────────────────────────
MLFLOW_TRACKING_URI = f"sqlite:///{os.path.join(BASE_DIR, 'mlflow.db')}"
MLFLOW_EXPERIMENT   = "rag-evaluation"

# ── LLM / Generation ──────────────────────────────────────────────────────────
LLM_MODEL       = "gemma4"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS  = 1500

# ── Evaluation ────────────────────────────────────────────────────────────────
EVAL_GROUND_TRUTH      = os.path.join(BASE_DIR, "data", "eval", "ground_truth.jsonl")
EVAL_TOP_K_RETRIEVAL   = 20   # Kandidaten aus ChromaDB
EVAL_TOP_K_FINAL       = 5    # Nach Reranking
ENABLE_GENERATION_EVAL = True
