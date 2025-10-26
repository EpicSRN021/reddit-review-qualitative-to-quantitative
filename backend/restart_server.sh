#!/bin/bash
# Restart the FastAPI backend server

cd "$(dirname "$0")"

echo "🔄 Restarting FastAPI backend..."
./stop_server.sh
sleep 2
./start_server.sh

