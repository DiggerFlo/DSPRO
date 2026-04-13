.PHONY: setup mlflow

setup:
	.venv/bin/python src/setup_models.py

mlflow:
	.venv/bin/mlflow ui --backend-store-uri sqlite:///mlflow.db
