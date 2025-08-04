# 💪 Sculptor - PowerShell Stop Script (JSON Version)

Write-Host "🏛️ Shutting down the gladiator arena..." -ForegroundColor Yellow

# Function to kill process by port
function Stop-ProcessByPort($port) {
    try {
        $processes = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($process in $processes) {
            $pid = $process.OwningProcess
            Write-Host "Stopping process $pid on port $port" -ForegroundColor Gray
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    } catch {
        Write-Host "No process found on port $port" -ForegroundColor Gray
    }
}

Write-Host "⚔️ Stopping backend (port 8001)..." -ForegroundColor Red
Stop-ProcessByPort 8001

Write-Host "💪 Stopping frontend (port 3000)..." -ForegroundColor Red
Stop-ProcessByPort 3000

# Also kill by process name
Write-Host "Stopping remaining processes..." -ForegroundColor Gray
try {
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue  
} catch {
    # Ignore errors for processes not found
}

Write-Host "🏛️ Arena closed. All gladiators dismissed!" -ForegroundColor Green