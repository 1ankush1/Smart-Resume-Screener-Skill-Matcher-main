# Purpose: Installs missing local dependencies, launches the Flask API and Vite frontend, and opens the site.
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $projectRoot "frontend\src\backend"
$frontend = Join-Path $projectRoot "frontend"
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$viteScript = Join-Path $frontend "node_modules\vite\bin\vite.js"
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
$nodeCommand = Get-Command node -ErrorAction SilentlyContinue

if (-not $pythonCommand) {
    throw "Python 3.10 or later is required. Install Python and enable 'Add Python to PATH', then run this script again."
}
if (-not $nodeCommand) {
    throw "Node.js LTS is required. Install Node.js (which includes npm), then run this script again."
}

# Bootstrap the project the first time, or repair the setup if dependencies are missing.
if (-not (Test-Path $venvPython) -or -not (Test-Path $viteScript)) {
    Write-Output "Installing the app's dependencies. This may take a few minutes..."
    & (Join-Path $projectRoot "setup.ps1")
}

function Test-LocalPort($port) {
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $attempt = $client.BeginConnect("127.0.0.1", $port, $null, $null)
        if (-not $attempt.AsyncWaitHandle.WaitOne(500)) { return $false }
        $client.EndConnect($attempt)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Dispose()
    }
}

$apiInUse = Test-LocalPort 5000
$webInUse = Test-LocalPort 8080
if ($apiInUse -and $webInUse) {
    Write-Output "The app is already running at http://localhost:8080"
    Start-Process "http://localhost:8080"
    exit 0
}
if ($apiInUse -or $webInUse) {
    throw "Port 5000 or 8080 is already in use. Close the other app using that port, then run this script again."
}

$backendCommand = "Set-Location -LiteralPath '$backend'; & '$venvPython' app.py"
$frontendCommand = "Set-Location -LiteralPath '$frontend'; & '$($nodeCommand.Source)' '$viteScript' --host 127.0.0.1 --port 8080 --configLoader runner"

# Keep each service in its own visible PowerShell window so startup errors are easy to see.
$backendEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($backendCommand))
$frontendEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($frontendCommand))
Start-Process powershell.exe -WorkingDirectory $projectRoot -ArgumentList @(
    "-NoExit", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $backendEncoded
)
Start-Process powershell.exe -WorkingDirectory $projectRoot -ArgumentList @(
    "-NoExit", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $frontendEncoded
)

Write-Output "Starting the app..."
Write-Output "Frontend: http://localhost:8080"
Write-Output "API health: http://localhost:5000/api/health"
Start-Sleep -Seconds 2
Start-Process "http://localhost:8080"
