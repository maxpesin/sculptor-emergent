@echo off
REM 💪 Sculptor - Roman Gladiator Workout Tracker
REM Windows Startup Script

echo 🏛️ Welcome to Sculptor - Roman Gladiator Workout Tracker!
echo ⚔️ Starting the gladiator training arena...
echo.

echo 🔍 Checking prerequisites...

REM Check for Node.js
node --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ✅ Node.js found
    node --version
) else (
    echo ❌ Node.js not found. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check for Python
python --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ✅ Python found
    python --version
) else (
    python3 --version >nul 2>&1
    if %ERRORLEVEL% == 0 (
        echo ✅ Python3 found
        python3 --version
    ) else (
        echo ❌ Python not found. Please install Python from https://python.org/
        pause
        exit /b 1
    )
)

REM Check for pip
pip --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ✅ pip found
) else (
    echo ❌ pip not found. Please install pip
    pause
    exit /b 1
)

REM Check for MongoDB
mongod --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ✅ MongoDB found
) else (
    echo ❌ MongoDB not found. Please install MongoDB from https://www.mongodb.com/try/download/community
    echo    Or use MongoDB Atlas (cloud) instead
    pause
    exit /b 1
)

REM Check for Yarn
yarn --version >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ✅ Yarn found
    yarn --version
) else (
    echo ⚠️ Yarn not found. Installing yarn...
    npm install -g yarn
)

echo.
echo 🛠️ Setting up the arena...

REM Create data directory for MongoDB
if not exist "data\db" mkdir data\db
echo ✅ Created MongoDB data directory

REM Install backend dependencies
echo 📦 Installing backend dependencies...
cd backend
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..
echo ✅ Backend dependencies installed

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
yarn install
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..
echo ✅ Frontend dependencies installed

REM Install concurrently for running multiple processes
echo 📦 Installing development tools...
npm install
echo ✅ Development tools installed

echo.
echo 🚀 Starting services...
echo    📊 MongoDB: http://localhost:27017
echo    ⚔️ Backend API: http://localhost:8001
echo    💪 Frontend: http://localhost:3000
echo.
echo Press Ctrl+C to stop all services
echo.

REM Start all services using concurrently
npm run dev