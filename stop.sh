#!/bin/bash

# 💪 Sculptor - Stop Script
echo "🏛️ Shutting down the gladiator arena..."

# Kill processes by port
echo "⚔️ Stopping backend (port 8001)..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || echo "No process running on port 8001"

echo "💪 Stopping frontend (port 3000)..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "No process running on port 3000"

echo "📊 Stopping MongoDB (port 27017)..."
lsof -ti:27017 | xargs kill -9 2>/dev/null || echo "No process running on port 27017"

# Also kill by process name
pkill -f "python.*server.py" 2>/dev/null || echo "No Python server found"
pkill -f "react-scripts start" 2>/dev/null || echo "No React dev server found"
pkill -f "mongod" 2>/dev/null || echo "No MongoDB process found"

echo "🏛️ Arena closed. All gladiators dismissed!"