#!/bin/bash
# Stop the FastAPI backend server

echo "Stopping FastAPI backend..."
lsof -ti:8000 | xargs kill -9 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Server stopped successfully"
else
    echo "ℹ️  No server running on port 8000"
fi

