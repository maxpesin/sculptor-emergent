# 💪 Sculptor - Roman Gladiator Workout Tracker
# PowerShell Startup Script

Write-Host "🏛️ Welcome to Sculptor - Roman Gladiator Workout Tracker!" -ForegroundColor Yellow
Write-Host "⚔️ Starting the gladiator training arena..." -ForegroundColor Yellow
Write-Host ""

Write-Host "🔍 Checking prerequisites..." -ForegroundColor Cyan

# Function to check if a command exists
function Test-Command($command) {
    try {
        Get-Command $command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Check for Node.js
if (Test-Command "node") {
    Write-Host "✅ Node.js found: $(node --version)" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js not found. Please install from https://nodejs.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for Python
if (Test-Command "python") {
    Write-Host "✅ Python found: $(python --version)" -ForegroundColor Green
} elseif (Test-Command "python3") {
    Write-Host "✅ Python3 found: $(python3 --version)" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found. Please install from https://python.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for pip
if (Test-Command "pip") {
    Write-Host "✅ pip found" -ForegroundColor Green
} else {
    Write-Host "❌ pip not found. Please install pip" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for MongoDB
if (Test-Command "mongod") {
    Write-Host "✅ MongoDB found" -ForegroundColor Green
} else {
    Write-Host "❌ MongoDB not found. Please install from https://www.mongodb.com/try/download/community" -ForegroundColor Red
    Write-Host "   Or use MongoDB Atlas (cloud) instead" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for Yarn
if (Test-Command "yarn") {
    Write-Host "✅ Yarn found: $(yarn --version)" -ForegroundColor Green
} else {
    Write-Host "⚠️ Yarn not found. Installing yarn..." -ForegroundColor Yellow
    npm install -g yarn
}

Write-Host ""
Write-Host "🛠️ Setting up the arena..." -ForegroundColor Cyan

# Create data directory for MongoDB
New-Item -ItemType Directory -Force -Path "data\db" | Out-Null
Write-Host "✅ Created MongoDB data directory" -ForegroundColor Green

# Install backend dependencies
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Set-Location ..
Write-Host "✅ Backend dependencies installed" -ForegroundColor Green

# Install frontend dependencies
Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
yarn install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Set-Location ..
Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green

# Install concurrently
Write-Host "📦 Installing development tools..." -ForegroundColor Yellow
npm install
Write-Host "✅ Development tools installed" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Cyan
Write-Host "   📊 MongoDB: http://localhost:27017" -ForegroundColor White
Write-Host "   ⚔️ Backend API: http://localhost:8001" -ForegroundColor White
Write-Host "   💪 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Start all services using concurrently
npm run dev