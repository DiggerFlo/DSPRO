#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# NZZ ContextAI — Repository Setup Script
# Run once after cloning: bash setup.sh
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

echo "──────────────────────────────────────────"
echo "  NZZ ContextAI — Project Setup"
echo "──────────────────────────────────────────"

# 1. Create virtual environment
echo "[1/5] Creating virtual environment (.venv)..."
python3 -m venv .venv
source .venv/bin/activate

# 2. Upgrade pip
echo "[2/5] Upgrading pip..."
pip install --upgrade pip --quiet

# 3. Install dependencies
echo "[3/5] Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet

# 4. Create .env from template if it doesn't exist
echo "[4/5] Setting up .env..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  → .env created from .env.example. Please fill in your values."
else
  echo "  → .env already exists, skipping."
fi

# 5. Create .gitkeep files so empty data folders are tracked by git
echo "[5/5] Adding .gitkeep to empty data directories..."
for dir in data/raw data/processed data/chunks data/embeddings experiments/mlflow; do
  touch "$dir/.gitkeep"
done

echo ""
echo "✅  Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate your environment:  source .venv/bin/activate"
echo "  2. Edit your .env file with the correct API keys and paths"
echo "  3. Start MLflow:               mlflow ui --backend-store-uri experiments/mlflow"
echo "  4. Run the pipeline:           python main.py --query 'your question'"
echo ""
