"""Model setup — downloads all required models for the RAG pipeline.

Run once after cloning the repo:
    python src/setup_models.py
"""

import subprocess
import sys


def _header(text: str) -> None:
    print(f"\n{'─' * 55}")
    print(f"  {text}")
    print(f"{'─' * 55}")


# ── 1. Ollama LLM ─────────────────────────────────────────────────────────────

def setup_ollama(model: str) -> None:
    _header(f"Ollama — {model}")

    if subprocess.run(["which", "ollama"], capture_output=True).returncode != 0:
        print("  Ollama nicht gefunden. Bitte installieren:")
        print("  curl -fsSL https://ollama.com/install.sh | sh")
        sys.exit(1)

    installed = subprocess.run(
        ["ollama", "list"], capture_output=True, text=True
    ).stdout
    if model.split(":")[0] in installed:
        print(f"  {model} bereits vorhanden — übersprungen.")
        return

    print(f"  Lade {model} ...")
    result = subprocess.run(["ollama", "pull", model])
    if result.returncode != 0:
        print(f"  Fehler beim Download von {model}.")
        sys.exit(1)
    print(f"  {model} erfolgreich geladen.")


# ── 2. HuggingFace Modelle ────────────────────────────────────────────────────

def setup_hf_models(embedding_model: str, reranker_model: str) -> None:
    _header("HuggingFace — Embedding & Reranker")

    print(f"  Embedding:  {embedding_model}")
    from sentence_transformers import SentenceTransformer
    SentenceTransformer(embedding_model, trust_remote_code=True)
    print(f"  Embedding-Modell geladen.")

    print(f"  Reranker:   {reranker_model}")
    from sentence_transformers import CrossEncoder
    CrossEncoder(reranker_model)
    print(f"  Reranker-Modell geladen.")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.dirname(__file__))

    from config import EMBEDDING_MODEL, RERANKER_MODEL, LLM_MODEL

    print("\n  NZZ ContextAI — Model Setup")

    setup_ollama(LLM_MODEL)
    setup_hf_models(EMBEDDING_MODEL, RERANKER_MODEL)

    print(f"\n{'═' * 55}")
    print("  Alle Modelle bereit. Pipeline kann gestartet werden.")
    print(f"{'═' * 55}\n")
