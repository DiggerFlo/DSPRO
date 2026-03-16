"""Evaluation — retrieval and answer quality metrics."""


def evaluate_retrieval(results: list[dict], ground_truth: list[str]) -> dict:
    """Compute retrieval metrics (e.g. Precision@k)."""
    raise NotImplementedError("Implement retrieval evaluation here.")


def evaluate_answers(answers: list[str], ground_truth: list[str]) -> dict:
    """Compute answer quality metrics."""
    raise NotImplementedError("Implement answer evaluation here.")
