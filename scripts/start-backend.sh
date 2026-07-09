#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)"
echo "Starting AI Research Assistant backend (auth + upload on :8000)..."
python -m uvicorn backend.dev_server:app --reload --host 0.0.0.0 --port 8000
