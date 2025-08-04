@echo off
REM 💪 Sculptor - Windows Stop Script

echo 🏛️ Shutting down the gladiator arena...

REM Kill processes by port using netstat and taskkill
echo ⚔️ Stopping backend (port 8001)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8001" ^| find "LISTENING"') do taskkill /f /pid %%a 2>nul

echo 💪 Stopping frontend (port 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do taskkill /f /pid %%a 2>nul

echo 📊 Stopping MongoDB (port 27017)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":27017" ^| find "LISTENING"') do taskkill /f /pid %%a 2>nul

REM Kill by process name
taskkill /f /im "python.exe" 2>nul
taskkill /f /im "node.exe" 2>nul
taskkill /f /im "mongod.exe" 2>nul

echo 🏛️ Arena closed. All gladiators dismissed!