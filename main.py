"""NZZ ContextAI — Query Pipeline Entry Point"""

import argparse
from dotenv import load_dotenv

load_dotenv()

from config import (
    CHROMA_PATH, CHROMA_COLLECTION,
    USE_RERANKING, EVAL_TOP_K_RETRIEVAL, EVAL_TOP_K_FINAL,
)
from src.embed import get_chroma_collection
from src.retrieval import load_models, retrieve
from src.generate import generate


def run_pipeline(query: str) -> str:
    """Run the full RAG pipeline for a given query and return the answer."""
    collection      = get_chroma_collection(CHROMA_PATH, CHROMA_COLLECTION)
    model, reranker = load_models(use_reranking=USE_RERANKING)

    chunks = retrieve(
        query, model, collection, reranker,
        top_k_retrieval=EVAL_TOP_K_RETRIEVAL,
        top_k_rerank=EVAL_TOP_K_FINAL,
    )

    return generate(query, chunks)


def main() -> None:
    parser = argparse.ArgumentParser(description="NZZ ContextAI — RAG Pipeline")
    parser.add_argument(
        "--query",
        type=str,
        default="Was berichtete die NZZ über die Finanzkrise 2008?",
        help="Frage an das System",
    )
    args = parser.parse_args()

    print(f"\nFrage: {args.query}\n")
    print(run_pipeline(args.query))


if __name__ == "__main__":
    main()
