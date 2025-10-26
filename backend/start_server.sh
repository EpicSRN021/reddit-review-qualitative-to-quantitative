#!/bin/bash
# Start the FastAPI backend server in the background

cd "$(dirname "$0")"

# Activate virtual environment
source ../venv/bin/activate

# Kill any existing server on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start server in background
nohup python3 server.py > server.log 2>&1 &

# Get the process ID
SERVER_PID=$!

echo "✅ FastAPI Backend started!"
echo "📝 Process ID: $SERVER_PID"
echo "📋 Logs: backend/server.log"
echo "🌐 Running on: http://localhost:8000"
echo ""
echo "To stop the server, run: ./stop_server.sh"

