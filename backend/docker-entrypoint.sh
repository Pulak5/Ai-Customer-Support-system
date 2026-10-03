#!/bin/sh
set -eu

CHROMA_DIRECTORY="/app/app/chroma_db"
INITIALIZATION_MARKER="$CHROMA_DIRECTORY/.initialized"

mkdir -p "$CHROMA_DIRECTORY"

if [ ! -f "$INITIALIZATION_MARKER" ]; then
  echo "Building the local RAG knowledge index..."
  python -m app.ai.rag.embedder
  touch "$INITIALIZATION_MARKER"
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000
