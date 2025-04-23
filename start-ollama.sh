#!/bin/sh

echo "🧠 Pulling model..."
ollama pull mistral:7b-instruct-q4_K_M || true

echo "🚀 Starting Ollama..."
ollama serve
