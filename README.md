# NZZ ContextAI

**Retrieval-Augmented Generation (RAG) System for Journalistic Archive Data**

> DSPRO1 FS26 | Hochschule Luzern  
> Team: Raphael Wunderlin, Enrico Tesan, Florentin Genge  
> Coach: Dimitris Mousadakos

---

## Project Overview

NZZ ContextAI is a RAG-based system that enables semantic search and context-aware answer generation across archived NZZ articles. The goal is to help journalists and editors quickly retrieve historical context, recognize patterns over time, and generate citation-backed answers.

---

## Repository Structure

```
nzz-contextai/
├── data/
│   ├── raw/            # Raw ingested article data (never modified)
│   ├── processed/      # Cleaned and normalized articles
│   ├── chunks/         # Chunked documents with metadata
│   └── embeddings/     # Generated vector embeddings
│
├── src/
│   ├── ingestion/      # Data ingestion pipeline
│   ├── preprocessing/  # Text cleaning and normalization
│   ├── chunking/       # Document chunking strategies
│   ├── embedding/      # Embedding model wrappers
│   ├── retrieval/      # Vector store and semantic search
│   ├── generation/     # Prompt templates and LLM calls
│   └── evaluation/     # Retrieval and answer quality metrics
│
├── notebooks/          # Exploratory analysis and experiments
├── experiments/
│   └── mlflow/         # MLflow tracking data
├── configs/            # Configuration files (YAML/JSON)
├── tests/              # Unit and integration tests
├── docs/
│   ├── architecture/   # Architecture diagrams and decisions
│   └── reports/        # Project reports and deliverables
├── demo/
│   └── assets/         # Demo screenshots and example outputs
│
├── main.py             # End-to-end RAG pipeline entry point
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── .gitignore
```

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/<your-org>/nzz-contextai.git
cd nzz-contextai
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your API keys and paths
```

### 5. Start MLflow tracking server
```bash
mlflow ui --backend-store-uri experiments/mlflow
# Open http://localhost:5000
```

---

## Running the Pipeline

```bash
# Full end-to-end pipeline
python main.py

# Individual stages
python -m src.ingestion.ingest
python -m src.preprocessing.preprocess
python -m src.chunking.chunk
python -m src.embedding.embed
python -m src.retrieval.retrieve --query "your question here"
```

---

## Running the Demo
```bash
python demo/app.py
```

---

## Running Tests
```bash
pytest tests/
```

---

## Experiment Tracking

All experiments are tracked with MLflow. Logged parameters include:

| Category      | Variables                                          |
|---------------|----------------------------------------------------|
| Embedding     | Model name, dimension, language                    |
| Chunking      | Chunk size, overlap, strategy                      |
| Retrieval     | Top-k, similarity metric, reranking                |
| Prompts       | Template version, system prompt                    |
| Metrics       | Precision@k, relevance score, hallucination rate   |
| Runtime       | Latency, throughput                                |

---

## Naming Conventions

| Type           | Convention                  | Example                        |
|----------------|-----------------------------|--------------------------------|
| Python files   | `snake_case.py`             | `chunk_pipeline.py`            |
| Config files   | `snake_case.yaml`           | `embedding_config.yaml`        |
| Data files     | `YYYY-MM-DD_description`    | `2024-01-15_raw_articles.json` |
| Notebooks      | `##_description.ipynb`      | `01_data_exploration.ipynb`    |
| MLflow runs    | `<component>_<variant>_v<n>`| `chunking_semantic_v1`         |

---

## Team & Roles

| Name               | Primary Area                      |
|--------------------|-----------------------------------|
| Raphael Wunderlin  | TBD                               |
| Enrico Tesan       | TBD                               |
| Florentin Genge    | TBD                               |

---

## License

Internal project — Hochschule Luzern, FS26. Not for public redistribution.
