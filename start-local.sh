#!/usr/bin/env bash
set -e

PORT=8000
APP_MODULE="app.main:app"

echo "🔍 Checking for process on port $PORT..."

PID=$(lsof -ti tcp:$PORT || true)

if [ -n "$PID" ]; then
  echo "🛑 Killing existing process on port $PORT (PID: $PID)"
  kill -9 $PID
else
  echo "✅ No existing process on port $PORT"
fi

echo "🐍 Activating virtual environment..."

if [ ! -d ".venv" ]; then
  echo "❌ .venv not found. Please create virtualenv first."
  exit 1
fi

source .venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🚀 Starting FastAPI backend on port $PORT"
exec uvicorn $APP_MODULE --host 0.0.0.0 --port $PORT --reload