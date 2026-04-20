"""MLflow experiment runner — evaluates the full RAG pipeline."""

import csv
import io
import tempfile
import os
from datetime import datetime

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


def _print_results_table(rows: list[dict], show_generation: bool = False) -> None:
    """Print a readable per-query results table to stdout."""
    gen_col = f" {'ROUGE':>6}" if show_generation else ""
    header = f"  {'Query':<52} {'H@1':>4} {'H@3':>4} {'H@5':>4} {'MRR':>6}{gen_col}"
    print(header)
    print("  " + "─" * (len(header) - 2))
    for r in rows:
        h1  = "✓" if r["hit_at_1"]  else "✗"
        h3  = "✓" if r["hit_at_3"]  else "✗"
        h5  = "✓" if r["hit_at_5"]  else "✗"
        gen_val = f" {r.get('rouge_l_approx', 0):>6.3f}" if show_generation else ""
        print(f"  {r['query']:<52} {h1:>4} {h3:>4} {h5:>4} {r['mrr']:>6.3f}{gen_val}")


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

    if run_name is None:
        run_name = datetime.now().strftime("%Y-%m-%d_%H-%M")

    with mlflow.start_run(run_name=run_name):

        mlflow.log_params({
            "embedding_model":  EMBEDDING_MODEL,
            "reranker_model":   RERANKER_MODEL if USE_RERANKING else "none",
            "use_reranking":    USE_RERANKING,
            "chunk_size":       CHUNK_SIZE,
            "chunk_overlap":    CHUNK_OVERLAP,
            "top_k_retrieval":  EVAL_TOP_K_RETRIEVAL,
            "top_k_final":      EVAL_TOP_K_FINAL,
            "num_eval_samples": len(ground_truth),
        })

        per_query_rows            = []
        retrieval_metrics_list    = []
        generation_metrics_list   = []

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

            metrics = evaluate_retrieval(results, relevant_ids, k=EVAL_TOP_K_FINAL)
            retrieval_metrics_list.append(metrics)

            per_query_rows.append({
                "query":    query[:55],
                "hit_at_1": metrics["hit_at_1"],
                "hit_at_3": metrics["hit_at_3"],
                "hit_at_5": metrics[f"hit_at_{EVAL_TOP_K_FINAL}"],
                "mrr":      metrics["mrr"],
                "top1_article": results[0]["article_id"] if results else "",
                "top1_title":   results[0]["title"][:60] if results else "",
                "top1_score":   round(results[0].get("similarity_score", 0), 3) if results else 0,
            })

            if ENABLE_GENERATION_EVAL:
                expected = sample.get("expected_answer")
                if expected:
                    from generate import generate
                    answer = generate(query, results)
                    gen_metrics = evaluate_answers(answer, expected)
                    generation_metrics_list.append(gen_metrics)
                    per_query_rows[-1]["generated_answer"] = answer
                    per_query_rows[-1]["rouge_l_approx"]   = round(gen_metrics["rouge_l_approx"], 3)

        # ── Durchschnittliche Metriken loggen ──────────────────────────────────
        avg = _average(retrieval_metrics_list)
        mlflow.log_metrics(avg)

        if generation_metrics_list:
            mlflow.log_metrics(_average(generation_metrics_list))

        # ── Per-Query CSV als Artifact speichern ───────────────────────────────
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=per_query_rows[0].keys())
        writer.writeheader()
        writer.writerows(per_query_rows)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv",
                                         delete=False, encoding="utf-8") as f:
            f.write(csv_buffer.getvalue())
            tmp_path = f.name

        mlflow.log_artifact(tmp_path, artifact_path="eval")
        os.unlink(tmp_path)

        # ── Ausgabe ───────────────────────────────────────────────────────────
        print(f"\n{'═' * 65}")
        print(f"  Experiment: {MLFLOW_EXPERIMENT}  |  Run: {run_name}")
        print(f"{'═' * 65}")
        print(f"  Chunks in DB:   {collection.count():,}")
        print(f"  Eval-Queries:   {len(ground_truth)}")
        print(f"  Reranking:      {'an' if USE_RERANKING else 'aus'}")
        print(f"{'─' * 65}")
        print()
        has_gen = bool(generation_metrics_list)
        _print_results_table(per_query_rows, show_generation=has_gen)
        print()
        print(f"{'─' * 65}")
        print(f"  Hit@1:  {avg['hit_at_1']:.0%}   "
              f"Hit@3:  {avg['hit_at_3']:.0%}   "
              f"Hit@{EVAL_TOP_K_FINAL}: {avg[f'hit_at_{EVAL_TOP_K_FINAL}']:.0%}   "
              f"MRR:  {avg['mrr']:.3f}")
        print(f"  Precision@{EVAL_TOP_K_FINAL}: {avg[f'precision_at_{EVAL_TOP_K_FINAL}']:.3f}   "
              f"Recall@{EVAL_TOP_K_FINAL}: {avg[f'recall_at_{EVAL_TOP_K_FINAL}']:.3f}   "
              f"NDCG@{EVAL_TOP_K_FINAL}: {avg[f'ndcg_at_{EVAL_TOP_K_FINAL}']:.3f}")
        if has_gen:
            avg_gen = _average(generation_metrics_list)
            print(f"  ROUGE-L (approx):  {avg_gen['rouge_l_approx']:.3f}")
        print(f"{'═' * 65}")
        print(f"\n  MLflow UI → http://localhost:5000\n")


if __name__ == "__main__":
    run_experiment()
