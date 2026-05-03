import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Rohdaten
NZZ_JSON_GLOB = os.path.join(BASE_DIR, "data", "raw", "articles_*.json")

# ChromaDB
CHROMA_PATH       = os.path.join(BASE_DIR, "data", "chroma")
CHROMA_COLLECTION = "chunks"

# Artikel kürzer als X Zeichen werden beim Preprocessing gefiltert
MIN_TEXT_LENGTH = 100

# Chunking
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 250

# Embedding-Modell: https://huggingface.co/spaces/mteb/leaderboard
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"

# Retrieval & Reranking
RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
USE_RERANKING  = True

# Reciprocal Rank Fusion — kombiniert Dense + BM25 Retrieval
USE_RRF = False
RRF_K   = 60  # Dämpfungskonstante, Standard ist 60

# MLflow
MLFLOW_TRACKING_URI = f"sqlite:///{os.path.join(BASE_DIR, 'mlflow.db')}"
MLFLOW_EXPERIMENT   = "rag-evaluation"

# LLM
LLM_MODEL       = "llama3.1:8b"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS  = 1200
LLM_THINK       = False  # Thinking-Modus kostet ~25s pro Anfrage
LLM_KEEP_ALIVE  = -1     # Modell dauerhaft im VRAM halten

# Evaluation
EVAL_GROUND_TRUTH      = os.path.join(BASE_DIR, "data", "eval", "ground_truth.jsonl")
EVAL_TOP_K_RETRIEVAL   = 10
EVAL_TOP_K_FINAL       = 5
ENABLE_GENERATION_EVAL = True
USE_FULL_ARTICLE       = False  # True: LLM bekommt den ganzen Artikel statt nur Top-Chunks

# Mindest-Score damit eine Anfrage als relevant gilt (Cross-Encoder-Logit)
# Empirisch kalibriert: relevante Anfragen >0, irrelevante <0
# Bei USE_RERANKING=False wird stattdessen similarity_score >= 0.35 geprüft
MIN_RELEVANCE_SCORE = 0.0
