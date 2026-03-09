"""
NZZ ContextAI — End-to-End RAG Pipeline Entry Point
"""

import argparse
from dotenv import load_dotenv

load_dotenv()


def run_pipeline(query: str) -> None:
    """Run the full RAG pipeline for a given query."""
    # TODO: wire up pipeline stages once implemented
    # from src.retrieval.retrieve import retrieve
    # from src.generation.generate import generate

    print(f"[NZZ ContextAI] Query: {query}")
    print("[NZZ ContextAI] Pipeline not yet wired up — implement src/ modules first.")


def main() -> None:
    parser = argparse.ArgumentParser(description="NZZ ContextAI — RAG Pipeline")
    parser.add_argument(
        "--query",
        type=str,
        default="Was berichtete die NZZ über die Finanzkrise 2008?",
        help="Question to answer using the archive",
    )
    args = parser.parse_args()
    run_pipeline(args.query)


if __name__ == "__main__":
    main()
