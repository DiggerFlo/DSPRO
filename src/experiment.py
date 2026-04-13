"""MLflow experiment runner — evaluates the full RAG pipeline."""

import mlflow
from sentence_transformers import SentenceTransformer, CrossEncoder

from config import (
    MLFLOW_TRACKING_URI,
    MLFLOW_EXPERIMENT,
    EMBEDDING_MODEL,
    RERANKER_MODEL,
    USE_RERANKING,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EVAL_GROUND_TRUTH,
    EVAL_TOP_K_RETRIEVAL,
    EVAL_TOP_K_FINAL,
    ENABLE_GENERATION_EVAL,
    CHROMA_PATH,
    CHROMA_COLLECTION,
)
from embed import get_chroma_collection
from retrieval import retrieve
from evaluate import load_ground_truth, evaluate_retrieval, evaluate_answers


def _average(list_of_dicts: list[dict]) -> dict:
    keys = list_of_dicts[0].keys()
    n    = len(list_of_dicts)
    return {k: sum(d[k] for d in list_of_dicts) / n for k in keys}


def run_experiment(run_name: str = None) -> None:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    ground_truth = load_ground_truth(EVAL_GROUND_TRUTH)
    if not ground_truth:
        print("Keine Ground-Truth-Daten gefunden. Bitte data/eval/ground_truth.jsonl befüllen.")
        return

    collection = get_chroma_collection(CHROMA_PATH, CHROMA_COLLECTION)
    model      = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)
    reranker   = CrossEncoder(RERANKER_MODEL) if USE_RERANKING else None

    with mlflow.start_run(run_name=run_name):

        mlflow.log_params({
            "embedding_model":   EMBEDDING_MODEL,
            "reranker_model":    RERANKER_MODEL if USE_RERANKING else "none",
            "use_reranking":     USE_RERANKING,
            "chunk_size":        CHUNK_SIZE,
            "chunk_overlap":     CHUNK_OVERLAP,
            "top_k_retrieval":   EVAL_TOP_K_RETRIEVAL,
            "top_k_final":       EVAL_TOP_K_FINAL,
            "generation_eval":   ENABLE_GENERATION_EVAL,
            "num_eval_samples":  len(ground_truth),
        })

        retrieval_metrics_per_query  = []
        generation_metrics_per_query = []

        for sample in ground_truth:
            query        = sample["query"]
            relevant_ids = sample["relevant_article_ids"]

            results = retrieve(
                query,
                model,
                collection,
                reranker,
                top_k_retrieval=EVAL_TOP_K_RETRIEVAL,
                top_k_rerank=EVAL_TOP_K_FINAL,
            )
            retrieval_metrics_per_query.append(
                evaluate_retrieval(results, relevant_ids, k=EVAL_TOP_K_FINAL)
            )

            if ENABLE_GENERATION_EVAL:
                expected = sample.get("expected_answer")
                if expected:
                    from generate import generate
                    answer = generate(query, results)
                    generation_metrics_per_query.append(
                        evaluate_answers(answer, expected)
                    )

        avg_retrieval = _average(retrieval_metrics_per_query)
        mlflow.log_metrics(avg_retrieval)

        if generation_metrics_per_query:
            avg_generation = _average(generation_metrics_per_query)
            mlflow.log_metrics(avg_generation)

        print("\nExperiment abgeschlossen:")
        print("  Retrieval:")
        for k, v in avg_retrieval.items():
            print(f"    {k}: {v:.4f}")
        if generation_metrics_per_query:
            print("  Generation:")
            for k, v in avg_generation.items():
                print(f"    {k}: {v:.4f}")

        print(f"\nMLflow UI: mlflow ui --backend-store-uri {MLFLOW_TRACKING_URI}")


if __name__ == "__main__":
    run_experiment()
