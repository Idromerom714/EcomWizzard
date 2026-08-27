#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
uvicorn backend.api.main:app --host 0.0.0.0 --port "${BACKEND_PORT:-8000}" &
exec streamlit run frontend/app.py --server.port "${PORT:-8501}" --server.address 0.0.0.0
