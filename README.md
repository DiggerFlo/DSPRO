# NZZ ContextAI

**Retrieval-Augmented Generation (RAG) system for semantic search over NZZ archive articles**

> DSPRO1 FS26 — Hochschule Luzern  
> Team: Raphael Wunderlin, Enrico Tesan, Florentin Genge  
> Coach: Dimitris Mousadakos

---

## Overview

NZZ ContextAI allows journalists and editors to ask questions against the NZZ archive and receive source-backed answers. The system combines semantic search (embedding + reranking) with local LLM generation via Ollama.

**Pipeline:**
```
JSON articles → BeautifulSoup → Chunking → Qwen3-Embedding → ChromaDB
                                                                   ↓
                Gemma4 (Ollama) ← Reranking ← Semantic Search ←───┘
```

---

## Project Structure

```
nzz-contextai/
├── src/
│   ├── config.py          # Central configuration (models, paths, parameters)
│   ├── ingest.py          # Ingestion pipeline (load → preprocess → chunk → embed)
│   ├── preprocess.py      # HTML cleaning (BeautifulSoup), normalization
│   ├── chunking.py        # Article chunking
│   ├── embed.py           # Embedding generation, ChromaDB storage
│   ├── retrieval.py       # Semantic search + reranking
│   ├── generate.py        # Answer generation with Gemma4 via Ollama
│   ├── evaluate.py        # Metrics: Faithfulness, ROUGE-L, Precision, Recall
│   ├── experiment.py      # Evaluation runner with MLflow logging
│   ├── setup_models.py    # Download required models (run once)
│   └── prompts/
│       └── system_prompt.md
├── scripts/
│   └── build_expected_answers.py  # Generate reference answers for ground truth
├── notebooks/
│   ├── Pipeline.ipynb             # Run the full pipeline (Ingest → Eval → Query)
│   ├── Explorer Notebook.ipynb    # Inspect raw data & debug retrieval
│   └── Data Exploration.ipynb     # Dataset statistics & charts
├── demo/
│   └── app.py                     # Streamlit chat interface
├── data/
│   ├── raw/                       # NZZ JSON source files (not in git)
│   ├── chroma/                    # ChromaDB vector store (not in git)
│   └── eval/
│       └── ground_truth.jsonl     # 14 evaluation queries with reference answers
├── tests/
│   └── test_pipeline.py
├── main.py                        # Query pipeline entry point
├── requirements.txt
├── Makefile
└── .env.example
```

---

## Setup

### 1. Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 2. Install Ollama and download models
```bash
curl -fsSL https://ollama.com/install.sh | sh
make setup
```

### 3. Configure environment variables
```bash
cp .env.example .env
```

---

## Running the Pipeline

```bash
# Index all articles (run on first setup or after new data arrives)
make ingest

# Index a single month
.venv/bin/python src/ingest.py --month 2025_12 --reset

# Generate reference answers for evaluation (run once)
make ground-truth

# Run full evaluation with MLflow tracking
make experiment

# Start the Streamlit demo
make demo

# Open MLflow UI → http://localhost:5000
make mlflow
```

Or run everything from the notebook: `notebooks/Pipeline.ipynb`

---

## Configuration

All parameters are defined in [`src/config.py`](src/config.py):

| Parameter | Value | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `Qwen/Qwen3-Embedding-0.6B` | Embedding model |
| `RERANKER_MODEL` | `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` | Reranker |
| `LLM_MODEL` | `gemma4` | Generation model (Ollama) |
| `CHUNK_SIZE` | `1000` | Words per chunk |
| `CHUNK_OVERLAP` | `250` | Overlap between chunks |
| `EVAL_TOP_K_RETRIEVAL` | `20` | Candidates retrieved from ChromaDB |
| `EVAL_TOP_K_FINAL` | `5` | Kept after reranking |

---

## Evaluation & MLflow

The following metrics are logged per run:

| Metric | Description |
|---|---|
| `hit_at_1/3/5` | Does the correct article appear in top-K results? |
| `mrr` | Mean Reciprocal Rank |
| `precision_at_5` | Fraction of relevant chunks in top-5 |
| `recall_at_5` | Coverage of relevant articles |
| `ndcg_at_5` | Normalized Discounted Cumulative Gain |
| `faithfulness` | How well the answer is grounded in retrieved sources |
| `rouge_l_approx` | Token overlap against the reference answer |

**Current results (Dec. 2025, 1,763 articles):**  
Hit@1: **86%** · Hit@3: **100%** · MRR: **0.917** · NDCG@5: **0.938**

---

## License

Internal academic project — HSLU FS26. Not for public redistribution.
