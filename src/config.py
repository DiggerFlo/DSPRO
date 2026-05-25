import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

NZZ_JSON_GLOB = os.path.join(BASE_DIR, "data", "raw", "articles_*.json")

CHROMA_PATH       = os.path.join(BASE_DIR, "data", "chroma")
CHROMA_COLLECTION = "chunks"

# Artikel kürzer als X Zeichen werden beim Preprocessing gefiltert
MIN_TEXT_LENGTH = 100

CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 250

EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"

RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
USE_RERANKING  = False

USE_RRF = True
RRF_K   = 60  # Dämpfungskonstante, Standard ist 60

MLFLOW_TRACKING_URI = f"sqlite:///{os.path.join(BASE_DIR, 'mlflow.db')}"
MLFLOW_EXPERIMENT   = "rag-evaluation"

LLM_MODEL       = "llama3.1:8b"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS  = 1200
LLM_THINK       = False  # Thinking-Modus kostet ~25s pro Anfrage
LLM_KEEP_ALIVE  = -1     # Modell dauerhaft im VRAM halten

EVAL_GROUND_TRUTH      = os.path.join(BASE_DIR, "data", "eval", "ground_truth.jsonl")
EVAL_TOP_K_RETRIEVAL   = 10
EVAL_TOP_K_FINAL       = 5
ENABLE_GENERATION_EVAL = True
USE_FULL_ARTICLE       = False  # True: LLM bekommt den ganzen Artikel statt nur Top-Chunks

# Empirisch kalibriert: relevante Anfragen >0, irrelevante <0
# Bei USE_RERANKING=False wird stattdessen similarity_score >= 0.35 geprüft
MIN_RELEVANCE_SCORE = 0.0
