.PHONY: mlflow

mlflow:
	.venv/bin/mlflow ui --backend-store-uri sqlite:///mlflow.db
