.PHONY: setup ingest experiment demo mlflow test

# ─── Setup ────────────────────────────────────────────────────────────────────
setup:
	.venv/bin/python src/setup_models.py

# ─── Pipeline ─────────────────────────────────────────────────────────────────
ingest:
	.venv/bin/python src/ingest.py

ingest-reset:
	.venv/bin/python src/ingest.py --reset

experiment:
	.venv/bin/python src/experiment.py

ground-truth:
	.venv/bin/python scripts/build_expected_answers.py

# ─── Demo ─────────────────────────────────────────────────────────────────────
demo:
	.venv/bin/streamlit run demo/app.py

# ─── MLflow ───────────────────────────────────────────────────────────────────
mlflow:
	.venv/bin/mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

# ─── Tests ────────────────────────────────────────────────────────────────────
test:
	.venv/bin/pytest tests/ -v
