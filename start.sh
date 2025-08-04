#!/bin/bash

# 💪 Sculptor - Roman Gladiator Workout Tracker
# Local Development Startup Script

echo "🏛️ Welcome to Sculptor - Roman Gladiator Workout Tracker!"
echo "⚔️ Starting the gladiator training arena..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null
}

echo ""
echo "🔍 Checking prerequisites..."

# Check for Node.js
if command_exists node; then
    echo -e "${GREEN}✅ Node.js found: $(node --version)${NC}"
else
    echo -e "${RED}❌ Node.js not found. Please install Node.js${NC}"
    exit 1
fi

# Check for Python
if command_exists python3; then
    echo -e "${GREEN}✅ Python found: $(python3 --version)${NC}"
elif command_exists python; then
    echo -e "${GREEN}✅ Python found: $(python --version)${NC}"
else
    echo -e "${RED}❌ Python not found. Please install Python${NC}"
    exit 1
fi

# Check for MongoDB
if command_exists mongod; then
    echo -e "${GREEN}✅ MongoDB found${NC}"
else
    echo -e "${RED}❌ MongoDB not found. Please install MongoDB${NC}"
    echo "   Ubuntu/Debian: sudo apt install mongodb"
    echo "   macOS: brew install mongodb/brew/mongodb-community"
    exit 1
fi

# Check for pip
if command_exists pip3; then
    echo -e "${GREEN}✅ pip found${NC}"
elif command_exists pip; then
    echo -e "${GREEN}✅ pip found${NC}"
else
    echo -e "${RED}❌ pip not found. Please install pip${NC}"
    exit 1
fi

# Check for yarn
if command_exists yarn; then
    echo -e "${GREEN}✅ Yarn found: $(yarn --version)${NC}"
else
    echo -e "${YELLOW}⚠️  Yarn not found. Installing yarn...${NC}"
    npm install -g yarn
fi

echo ""
echo "🛠️ Setting up the arena..."

# Create data directory for MongoDB
mkdir -p data/db
echo -e "${GREEN}✅ Created MongoDB data directory${NC}"

# Install backend dependencies
echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
cd backend
if command_exists pip3; then
    pip3 install -r requirements.txt
else
    pip install -r requirements.txt
fi
cd ..
echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Install frontend dependencies
echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
cd frontend
yarn install
cd ..
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

# Install concurrently for running multiple processes
echo -e "${YELLOW}📦 Installing development tools...${NC}"
npm install
echo -e "${GREEN}✅ Development tools installed${NC}"

echo ""
echo "🚀 Starting services..."

# Check if ports are available
if port_in_use 27017; then
    echo -e "${YELLOW}⚠️  Port 27017 (MongoDB) is already in use${NC}"
else
    echo -e "${GREEN}✅ Port 27017 (MongoDB) is available${NC}"
fi

if port_in_use 8001; then
    echo -e "${YELLOW}⚠️  Port 8001 (Backend) is already in use${NC}"
else
    echo -e "${GREEN}✅ Port 8001 (Backend) is available${NC}"
fi

if port_in_use 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 (Frontend) is already in use${NC}"
else
    echo -e "${GREEN}✅ Port 3000 (Frontend) is available${NC}"
fi

echo ""
echo "🏛️ Launching the Colosseum..."
echo "   📊 MongoDB: http://localhost:27017"
echo "   ⚔️ Backend API: http://localhost:8001"
echo "   💪 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Start all services using concurrently
npm run dev